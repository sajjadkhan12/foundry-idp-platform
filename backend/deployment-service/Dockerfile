FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Generate proto files
RUN python -m grpc_tools.protoc \
    -I./proto \
    --python_out=./proto \
    --grpc_python_out=./proto \
    --pyi_out=./proto \
    ./proto/deployment.proto ./proto/worker.proto && \
    touch proto/__init__.py && \
    # Fix import in generated grpc file using sed (more reliable)
    sed -i 's/^import deployment_pb2 as deployment__pb2$/from proto import deployment_pb2 as deployment__pb2/' proto/deployment_pb2_grpc.py && \
    sed -i 's/^import worker_pb2 as worker__pb2$/from proto import worker_pb2 as worker__pb2/' proto/worker_pb2_grpc.py || \
    python -c "import os; f=open('proto/deployment_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import deployment_pb2 as deployment__pb2', 'from proto import deployment_pb2 as deployment__pb2'); f=open('proto/deployment_pb2_grpc.py','w'); f.write(content); f.close(); f=open('proto/worker_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import worker_pb2 as worker__pb2', 'from proto import worker_pb2 as worker__pb2'); f=open('proto/worker_pb2_grpc.py','w'); f.write(content); f.close()"

# Copy startup script
COPY start_services.sh /app/start_services.sh
RUN chmod +x /app/start_services.sh

# Set Python path
ENV PYTHONPATH=/app

# Expose gRPC and REST ports
EXPOSE 50055 8000

# Run both gRPC server and REST adapter
CMD ["/app/start_services.sh"]
