#!/bin/bash
# Start both gRPC server and REST adapter

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
