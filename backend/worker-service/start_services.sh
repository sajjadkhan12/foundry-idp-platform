#!/bin/bash
# Start gRPC server, REST adapter, and Celery Worker (Beat is now in separate container)

# Ensure Pulumi is in PATH
export PATH="/root/.pulumi/bin:${PATH}"
export PULUMI_HOME="/root/.pulumi"

# Function to cleanup on exit
cleanup() {
    echo "Shutting down services..."
    kill $GRPC_PID $REST_PID $WORKER_PID 2>/dev/null
    wait $GRPC_PID $REST_PID $WORKER_PID 2>/dev/null
    exit 0
}

# Trap signals
trap cleanup SIGTERM SIGINT

# Start gRPC server in background
python -m app.grpc.server > /tmp/grpc.log 2>&1 &
GRPC_PID=$!
echo "Started gRPC server (PID: $GRPC_PID)"

# Start Celery Worker in background (processes tasks)
# Use nohup to ensure it continues running even if parent shell exits
nohup celery -A app.workers worker --loglevel=info --concurrency=2 > /tmp/worker.log 2>&1 &
WORKER_PID=$!
echo "Started Celery Worker (PID: $WORKER_PID)"
sleep 5  # Give worker time to start and register
# Verify worker is running
if ! kill -0 $WORKER_PID 2>/dev/null; then
    echo "ERROR: Celery worker failed to start!"
    cat /tmp/worker.log 2>&1 || echo "No worker.log available"
    exit 1
else
    echo "Celery worker is running (PID: $WORKER_PID)"
    # Show initial worker log to confirm it started
    if [ -f /tmp/worker.log ]; then
        echo "Worker log (first 10 lines):"
        head -10 /tmp/worker.log || echo "Log file empty"
    fi
fi

# Start REST adapter in foreground (keeps container alive)
echo "Starting REST adapter..."
python -m app.rest_adapter
REST_PID=$!
