# --- Rust Build Stage ---
FROM rust:1.84-slim AS builder
WORKDIR /usr/src/app

# Install required system libs to build Rust and Python bindings
RUN apt-get update && apt-get install -y \
    python3-dev python3-pip libssl-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN cargo build --release

# --- Python Dependencies Stage ---
FROM python:3.11-slim AS python-deps
WORKDIR /venv

# Install Python dependencies into venv
RUN python3 -m venv /venv
COPY requirements.txt .
RUN /venv/bin/pip install --no-cache-dir --upgrade pip \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

# --- Runtime Stage ---
FROM python:3.11-slim
WORKDIR /usr/local/bin

# ✅ Add debugging tools (curl, net-tools)
RUN apt-get update && apt-get install -y \
    curl net-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy Rust binary
COPY --from=builder /usr/src/app/target/release/shinobi-code-api .

# Copy Python venv + scripts
COPY --from=python-deps /venv /venv
COPY src/*.py .

# Set venv PATH
ENV PATH="/venv/bin:$PATH"

# Start the API
CMD ["./shinobi-code-api"]
