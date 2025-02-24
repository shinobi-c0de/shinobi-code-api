# --- Rust Build Stage ---
FROM rust:1.84-slim AS builder
WORKDIR /usr/src/app

# Install system dependencies for Rust
RUN apt-get update && apt-get install -y \
    python3 python3-dev python3-venv python3-pip \
    libssl-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN cargo build --release

# --- Python Dependencies Stage ---
FROM python:3.11-slim AS python-deps
WORKDIR /venv

# Install Python dependencies in a venv
RUN python3 -m venv /venv
COPY requirements.txt .
RUN /venv/bin/pip install --no-cache-dir --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

# --- Runtime Stage ---
FROM python:3.11-slim
WORKDIR /usr/local/bin

# Install minimal Python runtime dependencies
#RUN apt-get update && apt-get install -y \
#    python3 python3-venv python3-pip \
#    libssl3 \
#    && rm -rf /var/lib/apt/lists/* \
#    && apt-get clean autoclean \
#    && apt-get autoremove -y

# Copy Rust binary
COPY --from=builder /usr/src/app/target/release/shinobi-code-api .

# Copy Python venv with dependencies
COPY --from=python-deps /venv /venv

# Copy Python script
COPY src/*.py .

# Set environment variables
ENV PATH="/venv/bin:$PATH"

CMD ["./shinobi-code-api"]
