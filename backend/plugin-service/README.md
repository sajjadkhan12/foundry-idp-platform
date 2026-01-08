# Plugin Microservice

gRPC microservice for managing plugin upload and provisioning.

## Services

- **PluginService**: Upload plugins, create microservice templates, provision plugins, manage jobs

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Generate gRPC code:
```bash
python -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=proto \
    --grpc_python_out=proto \
    proto/plugin.proto
```

3. Set environment variables (see `.env.example`)

4. Run the server:
```bash
python -m app.grpc.server
```

## Docker

Build and run:
```bash
docker build -t plugin-service .
docker run -p 50053:50053 plugin-service
```

## Database

Shares PostgreSQL database with monolith. Uses same `plugins`, `plugin_versions`, `jobs`, and `job_logs` tables.
