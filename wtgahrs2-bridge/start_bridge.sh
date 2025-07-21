#!/bin/bash
# WTGAHRS2 to OpenCPN Bridge Startup Script

# Check if virtual environment exists
if [ ! -d "wtgahrs2_bridge" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv wtgahrs2_bridge
    source wtgahrs2_bridge/bin/activate
    pip install pynmea2 pyserial
else
    echo "Activating virtual environment..."
    source wtgahrs2_bridge/bin/activate
fi

# Check if device is connected
if [ ! -e "/dev/ttyUSB1" ]; then
    echo "Error: WTGAHRS2 device not found at /dev/ttyUSB1"
    echo "Please check that the device is connected and accessible"
    exit 1
fi

# Make device accessible
sudo chmod 666 /dev/ttyUSB1

echo "Starting WTGAHRS2 to OpenCPN Bridge..."
echo "Bridge will send NMEA data to UDP port 10110"
echo "Configure OpenCPN to receive UDP data from 127.0.0.1:10110"
echo "Press Ctrl+C to stop, or run ./stop_bridge.sh from another terminal"
echo ""

# Trap signals to ensure clean shutdown
trap 'echo ""; echo "Received signal, shutting down..."; kill $BRIDGE_PID 2>/dev/null; exit 0' INT TERM

# Start the bridge in background and save PID
python wtgahrs2_bridge.py --config config.ini &
BRIDGE_PID=$!

# Wait for the bridge process
wait $BRIDGE_PID

echo "Bridge stopped"