# Multi-stage build for optimized Python FastAPI backend
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libpq-dev \
    curl \
    ca-certificates \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Install uv to system location (use bash for installer)
RUN curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-install.sh && \
    bash /tmp/uv-install.sh --install-dir /usr/local/bin && \
    chmod +x /usr/local/bin/uv && \
    rm /tmp/uv-install.sh

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies using uv (installs to system Python, uses lock file for reproducibility)
RUN uv pip install --system --locked --no-cache -e .

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    git \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Pulumi CLI (includes Python language plugin)
RUN curl -fsSL https://get.pulumi.com | sh && \
    mv /root/.pulumi/bin/pulumi /usr/local/bin/pulumi && \
    mv /root/.pulumi /opt/pulumi && \
    chmod -R 755 /opt/pulumi && \
    chmod +x /usr/local/bin/pulumi

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/storage /app/logs /app/.pulumi && \
    chown -R appuser:appuser /app && \
    # Make Pulumi binaries accessible but use writable home for credentials
    chmod -R 755 /opt/pulumi

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# Set Pulumi home to writable location for appuser
# Keep binaries in /opt/pulumi/bin but use /app/.pulumi for credentials and plugins
ENV PULUMI_HOME=/app/.pulumi
ENV PATH=/opt/pulumi/bin:$PATH

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden for worker)
# Use 1 worker per pod in K8s (replicas handle scaling)
# For local dev, you can override with --workers flag
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

