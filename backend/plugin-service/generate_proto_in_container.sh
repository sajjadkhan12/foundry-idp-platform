#!/bin/bash
# Generate proto files inside the container

echo "Generating proto files in plugin-service container..."

docker exec foundry-idp-plugin-service python -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=proto \
    --grpc_python_out=proto \
    proto/plugin.proto

# Fix imports
docker exec foundry-idp-plugin-service python -c "
file_path = 'proto/plugin_pb2_grpc.py'
with open(file_path, 'r') as f:
    content = f.read()
content = content.replace('import plugin_pb2 as plugin__pb2', 'from proto import plugin_pb2 as plugin__pb2')
with open(file_path, 'w') as f:
    f.write(content)
print('Fixed imports')
"

echo "Proto files generated successfully!"
