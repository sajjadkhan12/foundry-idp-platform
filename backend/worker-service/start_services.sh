#!/bin/bash
# Start gRPC server, REST adapter, and Celery Worker (Beat is now in separate container)

# Generate gRPC code from proto files if needed (for development with volume mounts)
if [ -d "proto" ]; then
    echo "Generating gRPC code from proto files..."
    # Generate worker proto
    python -m grpc_tools.protoc \
        --proto_path=proto \
        --python_out=proto \
        --grpc_python_out=proto \
        proto/worker.proto && \
        touch proto/__init__.py && \
        python -c "f=open('proto/worker_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import worker_pb2 as worker__pb2', 'from proto import worker_pb2 as worker__pb2'); f=open('proto/worker_pb2_grpc.py','w'); f.write(content); f.close()"
    
    # Generate notification proto
    python -m grpc_tools.protoc \
        --proto_path=proto \
        --python_out=proto \
        --grpc_python_out=proto \
        proto/notification.proto && \
        python -c "f=open('proto/notification_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import notification_pb2 as notification__pb2', 'from proto import notification_pb2 as notification__pb2'); f=open('proto/notification_pb2_grpc.py','w'); f.write(content); f.close()"
    
    # Generate auth proto (needed for fetching configuration)
    python -m grpc_tools.protoc \
        --proto_path=proto \
        --python_out=proto \
        --grpc_python_out=proto \
        proto/auth.proto && \
        python -c "f=open('proto/auth_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import auth_pb2 as auth__pb2', 'from proto import auth_pb2 as auth__pb2'); f=open('proto/auth_pb2_grpc.py','w'); f.write(content); f.close()"
    
    echo "Proto generation complete."
fi

# Ensure Pulumi is in PATH
export PATH="/root/.pulumi/bin:${PATH}"
export PULUMI_HOME="/root/.pulumi"

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    kill $GRPC_PID $REST_PID $WORKER_PID 2>/dev/null
    wait $GRPC_PID $REST_PID $WORKER_PID 2>/dev/null
    exit 0
}

# Trap signals
trap cleanup SIGTERM SIGINT

# Start gRPC server in background
python -m app.grpc.server > /tmp/grpc.log 2>&1 &
GRPC_PID=$!
echo "Started gRPC server (PID: $GRPC_PID)"

# Start REST adapter in foreground (keeps container alive)
echo "Starting REST adapter..."
python -m app.rest_adapter
REST_PID=$!
