#!/bin/bash
# Generate gRPC Python code from proto files

echo "Generating gRPC code from proto files..."

python3 -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=. \
    --grpc_python_out=. \
    proto/auth.proto

# Create proto module structure
mkdir -p proto
mv auth_pb2.py proto/ 2>/dev/null || true
mv auth_pb2_grpc.py proto/ 2>/dev/null || true
touch proto/__init__.py

echo "Proto files generated successfully!"
echo "Generated files: proto/auth_pb2.py, proto/auth_pb2_grpc.py"
