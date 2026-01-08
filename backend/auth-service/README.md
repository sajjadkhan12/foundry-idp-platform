# Auth Microservice

Authentication and Authorization microservice using gRPC.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Generate gRPC code from proto files:
```bash
python -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=. \
    --grpc_python_out=. \
    proto/auth.proto

# Move generated files to proto module
mkdir -p proto
mv auth_pb2.py proto/
mv auth_pb2_grpc.py proto/
touch proto/__init__.py
```

3. Set environment variables (see `.env.example`)

4. Run the server:
```bash
python -m app.grpc.server
```

## Docker

Build and run:
```bash
docker build -t auth-service .
docker run -p 50051:50051 auth-service
```

## gRPC Services

- **AuthenticationService**: Login, logout, token refresh, token validation, registration
- **AuthorizationService**: Permission checks, role queries, admin checks
- **UserService**: User CRUD operations (TODO)
- **RoleService**: Role management (TODO)
- **GroupService**: Group management (TODO)
- **BusinessUnitService**: Business unit management (TODO)

## Database

Shares PostgreSQL database with monolith. Uses same models and schema.
