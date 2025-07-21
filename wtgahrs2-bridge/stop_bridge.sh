#!/bin/bash
# WTGAHRS2 to OpenCPN Bridge Stop Script

echo "Stopping WTGAHRS2 to OpenCPN Bridge..."

# Find and kill the bridge process
BRIDGE_PID=$(pgrep -f "wtgahrs2_bridge.py")

if [ -n "$BRIDGE_PID" ]; then
    echo "Found bridge process with PID: $BRIDGE_PID"
    echo "Sending SIGTERM to gracefully stop the bridge..."
    kill -TERM $BRIDGE_PID
    
    # Wait up to 5 seconds for graceful shutdown
    for i in {1..5}; do
        if ! kill -0 $BRIDGE_PID 2>/dev/null; then
            echo "Bridge stopped gracefully"
            exit 0
        fi
        echo "Waiting for bridge to stop... ($i/5)"
        sleep 1
    done
    
    # Force kill if still running
    if kill -0 $BRIDGE_PID 2>/dev/null; then
        echo "Bridge did not stop gracefully, forcing shutdown..."
        kill -KILL $BRIDGE_PID
        sleep 1
        if ! kill -0 $BRIDGE_PID 2>/dev/null; then
            echo "Bridge force stopped"
        else
            echo "Error: Unable to stop bridge process"
            exit 1
        fi
    fi
else
    echo "No bridge process found running"
fi

# Also check for any Python processes running the bridge
PYTHON_BRIDGE_PID=$(pgrep -f "python.*wtgahrs2_bridge")

if [ -n "$PYTHON_BRIDGE_PID" ]; then
    echo "Found Python bridge process with PID: $PYTHON_BRIDGE_PID"
    kill -TERM $PYTHON_BRIDGE_PID
    sleep 2
    if kill -0 $PYTHON_BRIDGE_PID 2>/dev/null; then
        kill -KILL $PYTHON_BRIDGE_PID
        echo "Python bridge process force stopped"
    else
        echo "Python bridge process stopped"
    fi
fi

echo "Bridge stop script completed"