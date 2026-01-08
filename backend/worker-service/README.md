# Worker Microservice

gRPC microservice for executing provisioning and cleanup tasks.

## Services

- **WorkerService**: Execute infrastructure/microservice provisioning, destruction, and cleanup tasks

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
    proto/worker.proto
```

3. Set environment variables (see `.env.example`)

4. Run the server:
```bash
python -m app.grpc.server
```

## Docker

Build and run:
```bash
docker build -t worker-service .
docker run -p 50054:50054 worker-service
```

## Database

Shares PostgreSQL database with monolith. Uses same `jobs`, `job_logs`, `deployments` tables.
