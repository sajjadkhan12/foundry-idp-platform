#!/bin/bash
# Regenerate gRPC code from proto files

echo "Regenerating gRPC code for plugin service..."

cd /Users/sajjad/Downloads/foundry-idp-setup/foundry-idp/backend/plugin-service

python3 -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=proto \
    --grpc_python_out=proto \
    proto/plugin.proto

# Fix import in generated grpc file
python3 -c "
import os
file_path = 'proto/plugin_pb2_grpc.py'
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    content = content.replace('import plugin_pb2 as plugin__pb2', 'from proto import plugin_pb2 as plugin__pb2')
    with open(file_path, 'w') as f:
        f.write(content)
    print('Fixed imports in plugin_pb2_grpc.py')
else:
    print('Warning: plugin_pb2_grpc.py not found')
"

echo "gRPC code regenerated successfully!"
