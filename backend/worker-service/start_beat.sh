#!/bin/bash
# Start Celery Beat scheduler (separate container)

# Ensure Pulumi is in PATH (needed for some tasks)
export PATH="/root/.pulumi/bin:${PATH}"
export PULUMI_HOME="/root/.pulumi"

# Function to cleanup on exit
cleanup() {
    echo "Shutting down Celery Beat..."
    kill $BEAT_PID 2>/dev/null
    wait $BEAT_PID 2>/dev/null
    exit 0
}

# Trap signals
trap cleanup SIGTERM SIGINT

# Start Celery Beat in foreground
echo "Starting Celery Beat scheduler..."
celery -A app.workers beat --loglevel=info
