#!/bin/bash
# Install WTGAHRS2 Bridge as a systemd service

echo "Installing WTGAHRS2 Bridge as a systemd service..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "Please run this script as your regular user, not as root"
    echo "The script will use sudo when needed"
    exit 1
fi

# Ensure virtual environment exists
if [ ! -d "/home/hic/wtgahrs2_bridge" ]; then
    echo "Creating virtual environment..."
    python3 -m venv /home/hic/wtgahrs2_bridge
    source /home/hic/wtgahrs2_bridge/bin/activate
    pip install pynmea2 pyserial
fi

# Copy service file to systemd directory
echo "Installing service file..."
sudo cp /home/hic/wtgahrs2-bridge.service /etc/systemd/system/

# Set correct permissions
sudo chmod 644 /etc/systemd/system/wtgahrs2-bridge.service

# Add user to dialout group for serial port access
echo "Adding user to dialout group..."
sudo usermod -a -G dialout $USER

# Create udev rule for consistent device permissions
echo "Creating udev rule for WTGAHRS2 device..."
sudo tee /etc/udev/rules.d/99-wtgahrs2.rules > /dev/null << 'EOF'
# WTGAHRS2 device permissions
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", MODE="0666", GROUP="dialout"
EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling service to start on boot..."
sudo systemctl enable wtgahrs2-bridge.service

echo ""
echo "Service installation complete!"
echo ""
echo "Commands:"
echo "  Start service:    sudo systemctl start wtgahrs2-bridge"
echo "  Stop service:     sudo systemctl stop wtgahrs2-bridge"
echo "  Check status:     sudo systemctl status wtgahrs2-bridge"
echo "  View logs:        sudo journalctl -u wtgahrs2-bridge -f"
echo "  Disable service:  sudo systemctl disable wtgahrs2-bridge"
echo ""
echo "Note: You may need to log out and back in for group changes to take effect"
echo "      Or reboot the system to ensure the service starts automatically"