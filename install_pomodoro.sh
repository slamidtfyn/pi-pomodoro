#!/bin/bash
# Pi Pomodoro Timer install script
# Installs dependencies and configures systemd service for current user
set -e

# Get current user and home directory
target_user="$(whoami)"
home_dir="$HOME"
project_dir="$home_dir/pi_pomodoro"
script_name="pi_pomodoro_timer.py"
service_name="pi_pomodoro.service"

# Ensure running as non-root (will use sudo for system tasks)
if [ "$target_user" = "root" ]; then
  echo "Please run this script as your regular user, not root."
  exit 1
fi

# Update and install system dependencies
echo "Updating system and installing dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-smbus i2c-tools

# Enable I2C
echo "Enabling I2C..."
sudo raspi-config nonint do_i2c 0

# Add user to gpio and i2c groups
sudo usermod -aG gpio,i2c "$target_user"

# Install Python dependencies
if [ -f "$project_dir/requirements.txt" ]; then
  echo "Installing Python dependencies..."
  pip3 install --user -r "$project_dir/requirements.txt"
else
  echo "requirements.txt not found in $project_dir. Skipping Python dependencies."
fi

# Make script executable
if [ -f "$project_dir/$script_name" ]; then
  chmod +x "$project_dir/$script_name"
else
  echo "$script_name not found in $project_dir."
  exit 1
fi

# Create systemd service file
echo "Configuring systemd service..."
service_path="/etc/systemd/system/$service_name"
sudo tee "$service_path" > /dev/null <<EOF
[Unit]
Description=Pi Pomodoro Timer
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $project_dir/$script_name
WorkingDirectory=$project_dir
Restart=always
User=$target_user

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable "$service_name"
sudo systemctl start "$service_name"

# Show status
sudo systemctl status "$service_name" --no-pager

echo "Installation complete!"
echo "You can view logs with: journalctl -u $service_name -f"
