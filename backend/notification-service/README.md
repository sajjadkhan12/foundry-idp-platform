# Notification Microservice

gRPC microservice for managing user notifications.

## Services

- **NotificationService**: Create, read, update, delete notifications
- Mark notifications as read
- Get unread count

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
    proto/notification.proto
```

3. Set environment variables (see `.env.example`)

4. Run the server:
```bash
python -m app.grpc.server
```

## Docker

Build and run:
```bash
docker build -t notification-service .
docker run -p 50052:50052 notification-service
```

## Database

Shares PostgreSQL database with monolith. Uses same `notifications` table.
