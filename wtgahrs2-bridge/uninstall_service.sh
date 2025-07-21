#!/bin/bash
# Uninstall WTGAHRS2 Bridge systemd service

echo "Uninstalling WTGAHRS2 Bridge systemd service..."

# Stop and disable the service
echo "Stopping and disabling service..."
sudo systemctl stop wtgahrs2-bridge.service 2>/dev/null || true
sudo systemctl disable wtgahrs2-bridge.service 2>/dev/null || true

# Remove service file
echo "Removing service file..."
sudo rm -f /etc/systemd/system/wtgahrs2-bridge.service

# Remove udev rule
echo "Removing udev rule..."
sudo rm -f /etc/udev/rules.d/99-wtgahrs2.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Reload systemd daemon
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo ""
echo "Service uninstallation complete!"
echo ""
echo "Note: User is still in dialout group. To remove:"
echo "      sudo gpasswd -d $USER dialout"