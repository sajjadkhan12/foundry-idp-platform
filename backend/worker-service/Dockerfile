# Stage 1: Builder
FROM python:3.11-slim-bookworm as builder

WORKDIR /app

# Install build dependencies (minimal - no Pulumi CLI needed)
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install Python dependencies
COPY requirements.txt .
RUN uv pip install --system --no-cache -r requirements.txt --target /install

# Stage 2: Runtime
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install runtime dependencies
# git is needed for GitPython (cloning repos for GitOps)
# postgresql-client is needed for DB health checks
RUN apt-get update && apt-get install -y \
    git \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# NOTE: Pulumi CLI is NO LONGER NEEDED!
# We use Pulumi Deployments API which runs Pulumi on Pulumi Cloud's infrastructure.
# This saves ~800MB from Pulumi CLI and ~600MB from SDK packages.

# Copy Python dependencies from builder
COPY --from=builder /install /usr/local

# Copy proto files
COPY proto/ proto/

# Copy application code
COPY app/ app/

# Generate gRPC code
RUN python -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=proto \
    --grpc_python_out=proto \
    proto/worker.proto proto/notification.proto proto/auth.proto && \
    touch proto/__init__.py && \
    # Fix imports in generated grpc files
    python -c "f=open('proto/worker_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import worker_pb2 as worker__pb2', 'from proto import worker_pb2 as worker__pb2'); f=open('proto/worker_pb2_grpc.py','w'); f.write(content); f.close()" && \
    python -c "f=open('proto/notification_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import notification_pb2 as notification__pb2', 'from proto import notification_pb2 as notification__pb2'); f=open('proto/notification_pb2_grpc.py','w'); f.write(content); f.close()" && \
    python -c "f=open('proto/auth_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import auth_pb2 as auth__pb2', 'from proto import auth_pb2 as auth__pb2'); f=open('proto/auth_pb2_grpc.py','w'); f.write(content); f.close()" || true

# Copy startup scripts
COPY start_services.sh /app/start_services.sh
COPY start_beat.sh /app/start_beat.sh
RUN chmod +x /app/start_services.sh /app/start_beat.sh

# Set Python path
ENV PYTHONPATH=/app

# Create storage directories
RUN mkdir -p /app/storage/plugins /app/storage/git-repos

# Expose gRPC and REST ports
EXPOSE 50054 8000

# Run both gRPC server and REST adapter
CMD ["/app/start_services.sh"]
