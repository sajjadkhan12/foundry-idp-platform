#!/bin/bash
# Start both gRPC server and REST adapter

# Generate gRPC code from proto files if needed (for development with volume mounts)
if [ -d "proto" ]; then
    echo "Generating gRPC code from proto files..."
    python -m grpc_tools.protoc \
        --proto_path=proto \
        --python_out=proto \
        --grpc_python_out=proto \
        proto/deployment.proto && \
        touch proto/__init__.py && \
        python -c "f=open('proto/deployment_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import deployment_pb2 as deployment__pb2', 'from proto import deployment_pb2 as deployment__pb2'); f=open('proto/deployment_pb2_grpc.py','w'); f.write(content); f.close()"
    
    python -m grpc_tools.protoc \
        --proto_path=proto \
        --python_out=proto \
        --grpc_python_out=proto \
        proto/worker.proto && \
        python -c "f=open('proto/worker_pb2_grpc.py','r'); content=f.read(); f.close(); content=content.replace('import worker_pb2 as worker__pb2', 'from proto import worker_pb2 as worker__pb2'); f=open('proto/worker_pb2_grpc.py','w'); f.write(content); f.close()"
    echo "Proto generation complete."
fi

# Start gRPC server in background
python -m app.grpc.server &
GRPC_PID=$!

# Start REST adapter
python -m app.rest_adapter &
REST_PID=$!

# Wait for either process to exit
wait -n

# If one exits, kill the other
kill $GRPC_PID $REST_PID 2>/dev/null
