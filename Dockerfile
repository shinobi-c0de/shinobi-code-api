# =============================================================================
# Rust + pyo3 + Python Multi-Stage Dockerfile
# =============================================================================
# Key: Build Rust with the SAME Python version as runtime to avoid pyo3 issues
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Build Rust binary (with Python 3.14 for pyo3)
# -----------------------------------------------------------------------------
FROM python:3.14-slim-bookworm AS rust-builder

WORKDIR /build

# Install Rust toolchain and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    pkg-config \
    libssl-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable

ENV PATH="/root/.cargo/bin:$PATH"

# Verify Python version (must match runtime)
RUN python3 --version && rustc --version

# Cache Cargo dependencies
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main() {}" > src/main.rs \
    && cargo build --release \
    && rm -rf src

# Build actual application
COPY src/*.rs ./src/
RUN touch src/main.rs && cargo build --release

# -----------------------------------------------------------------------------
# Stage 2: Build Python virtual environment with dependencies
# -----------------------------------------------------------------------------
FROM python:3.14-slim-bookworm AS python-builder

WORKDIR /build

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Create venv and install dependencies (production only)
# UV_PROJECT_ENVIRONMENT tells uv sync where to install packages
ENV UV_PROJECT_ENVIRONMENT=/opt/venv

RUN uv venv /opt/venv && \
    uv sync --locked --no-dev

# -----------------------------------------------------------------------------
# Stage 3: Runtime
# -----------------------------------------------------------------------------
FROM python:3.14-slim-bookworm

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from python-builder
COPY --from=python-builder /opt/venv /opt/venv

# Copy Rust binary
COPY --from=rust-builder /build/target/release/shinobi-code-api /app/shinobi-code-api

# Copy Python source files
COPY py/*.py /app/src/
RUN touch /app/src/__init__.py

# Set ownership and permissions
RUN chown -R appuser:appuser /app && chmod +x /app/shinobi-code-api

# Switch to non-root user
USER appuser

# Environment configuration
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    RUST_LOG=info

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/api || exit 1

EXPOSE 8080

CMD ["/app/shinobi-code-api"]
