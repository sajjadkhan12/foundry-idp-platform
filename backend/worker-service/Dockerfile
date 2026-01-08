FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Pulumi CLI (needed for Automation API and plugin management)
RUN curl -fsSL https://get.pulumi.com | sh
ENV PATH="/root/.pulumi/bin:${PATH}"
ENV PULUMI_HOME="/root/.pulumi"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files
COPY proto/ proto/

# Copy application code
COPY app/ app/

# Generate gRPC code from proto files
RUN python -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=proto \
    --grpc_python_out=proto \
    proto/worker.proto proto/notification.proto && \
    touch proto/__init__.py && \
    # Fix imports in generated grpc files
    python -c "f=open('proto/worker_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import worker_pb2 as worker__pb2', 'from proto import worker_pb2 as worker__pb2'); f=open('proto/worker_pb2_grpc.py','w'); f.write(content); f.close()" && \
    python -c "f=open('proto/notification_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import notification_pb2 as notification__pb2', 'from proto import notification_pb2 as notification__pb2'); f=open('proto/notification_pb2_grpc.py','w'); f.write(content); f.close()" || true

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
