# Deployment Microservice

gRPC microservice for managing deployments.

## Features

- Deployment CRUD operations
- Deployment history tracking
- Tag management
- CI/CD status tracking
- Statistics and cost tracking

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Generate proto files
python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/deployment.proto

# Run server
python -m app.grpc.server
```

## Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `GRPC_HOST`: gRPC server host (default: 0.0.0.0)
- `GRPC_PORT`: gRPC server port (default: 50055)
- `DEBUG`: Enable debug mode (default: True)
