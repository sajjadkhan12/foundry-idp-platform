FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

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
    proto/notification.proto && \
    touch proto/__init__.py && \
    # Fix import in generated grpc file
    python -c "f=open('proto/notification_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import notification_pb2 as notification__pb2', 'from proto import notification_pb2 as notification__pb2'); f=open('proto/notification_pb2_grpc.py','w'); f.write(content); f.close()"

# Copy startup script
COPY start_services.sh /app/start_services.sh
RUN chmod +x /app/start_services.sh

# Set Python path
ENV PYTHONPATH=/app

# Expose gRPC and REST ports
EXPOSE 50052 8000

# Run both gRPC server and REST adapter
CMD ["/app/start_services.sh"]
