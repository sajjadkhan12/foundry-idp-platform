#!/bin/bash

# Script to generate TypeScript code from proto files for gRPC-Web

set -e

# Directories
PROTO_DIR="../../proto"
OUTPUT_DIR="src/generated"
AUTH_PROTO="../../auth-service/proto/auth.proto"
NOTIFICATION_PROTO="../../notification-service/proto/notification.proto"
PLUGIN_PROTO="../../plugin-service/proto/plugin.proto"
WORKER_PROTO="../../worker-service/proto/worker.proto"
DEPLOYMENT_PROTO="../../deployment-service/proto/deployment.proto"

# Create output directory
mkdir -p ${OUTPUT_DIR}

echo "Generating TypeScript code from proto files..."

# Check if grpc_tools_node_protoc is available
if ! command -v grpc_tools_node_protoc &> /dev/null; then
    echo "Installing grpc-tools..."
    npm install --save-dev grpc-tools ts-protoc-gen
fi

# Generate code for auth service
if [ -f "$AUTH_PROTO" ]; then
    echo "Generating code for auth.proto..."
    mkdir -p ${OUTPUT_DIR}/auth
    ./node_modules/.bin/grpc_tools_node_protoc \
        --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts \
        --js_out=import_style=commonjs,binary:${OUTPUT_DIR}/auth \
        --ts_out=service=grpc-web:${OUTPUT_DIR}/auth \
        --proto_path=../../auth-service/proto \
        --proto_path=../../auth-service \
        ${AUTH_PROTO}
    # Move files to proper structure
    mv ${OUTPUT_DIR}/auth/auth_pb.js ${OUTPUT_DIR}/auth/auth_pb.js 2>/dev/null || true
    mv ${OUTPUT_DIR}/auth/auth_pb.d.ts ${OUTPUT_DIR}/auth/auth_pb.d.ts 2>/dev/null || true
    # KEEP ORIGINAL NAMES
    # mv ${OUTPUT_DIR}/auth/auth_pb_service.js ${OUTPUT_DIR}/auth/AuthenticationServiceClientPb.js 2>/dev/null || true
    # mv ${OUTPUT_DIR}/auth/auth_pb_service.d.ts ${OUTPUT_DIR}/auth/AuthenticationServiceClientPb.d.ts 2>/dev/null || true
fi

# Generate code for notification service
if [ -f "$NOTIFICATION_PROTO" ]; then
    echo "Generating code for notification.proto..."
    ./node_modules/.bin/grpc_tools_node_protoc \
        --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts \
        --js_out=import_style=commonjs,binary:${OUTPUT_DIR} \
        --ts_out=service=grpc-web:${OUTPUT_DIR} \
        --proto_path=../../notification-service/proto \
        --proto_path=../../notification-service \
        ${NOTIFICATION_PROTO}
fi

# Generate code for plugin service
if [ -f "$PLUGIN_PROTO" ]; then
    echo "Generating code for plugin.proto..."
    ./node_modules/.bin/grpc_tools_node_protoc \
        --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts \
        --js_out=import_style=commonjs,binary:${OUTPUT_DIR} \
        --ts_out=service=grpc-web:${OUTPUT_DIR} \
        --proto_path=../../plugin-service/proto \
        --proto_path=../../plugin-service \
        ${PLUGIN_PROTO}
fi

# Generate code for worker service
if [ -f "$WORKER_PROTO" ]; then
    echo "Generating code for worker.proto..."
    ./node_modules/.bin/grpc_tools_node_protoc \
        --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts \
        --js_out=import_style=commonjs,binary:${OUTPUT_DIR} \
        --ts_out=service=grpc-web:${OUTPUT_DIR} \
        --proto_path=../../worker-service/proto \
        --proto_path=../../worker-service \
        ${WORKER_PROTO}
fi

# Generate code for deployment service
if [ -f "$DEPLOYMENT_PROTO" ]; then
    echo "Generating code for deployment.proto..."
    ./node_modules/.bin/grpc_tools_node_protoc \
        --plugin=protoc-gen-ts=./node_modules/.bin/protoc-gen-ts \
        --js_out=import_style=commonjs,binary:${OUTPUT_DIR} \
        --ts_out=service=grpc-web:${OUTPUT_DIR} \
        --proto_path=../../deployment-service/proto \
        --proto_path=../../deployment-service \
        ${DEPLOYMENT_PROTO}
fi

echo "Proto code generation complete!"
echo "Generated files are in: ${OUTPUT_DIR}"
