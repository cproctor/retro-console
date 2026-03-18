#!/bin/bash
# Install retro-console to /opt/retro-console and set up systemd user services.
#
# Run as the user who will run the console (not root), but sudo is required
# for copying files to /opt. The script will prompt for sudo as needed.
#
# Usage:
#   bash config/install.sh
#
# Prerequisites on the Pi:
#   - antimicrox installed (sudo apt install antimicrox)
#   - uv installed (curl -LsSf https://astral.sh/uv/install.sh | sh)
#   - xterm installed (sudo apt install xterm)
#   - Auto-login to desktop configured (via raspi-config > System > Auto Login)

set -euo pipefail

INSTALL_DIR=/opt/retro-console
SERVICE_DIR="$HOME/.config/systemd/user"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Installing retro-console to $INSTALL_DIR"
sudo mkdir -p "$INSTALL_DIR"
sudo rsync -a --delete \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='*.db' \
    "$REPO_DIR/" "$INSTALL_DIR/"
sudo chown -R "$USER:$USER" "$INSTALL_DIR"

echo "==> Syncing Python dependencies"
(cd "$INSTALL_DIR" && uv sync)

echo "==> Installing systemd user services"
mkdir -p "$SERVICE_DIR"
cp "$REPO_DIR/config/systemd/antimicrox.service" "$SERVICE_DIR/"
cp "$REPO_DIR/config/systemd/retro-console.service" "$SERVICE_DIR/"

echo "==> Enabling linger so user services start at boot"
loginctl enable-linger "$USER"

echo "==> Reloading systemd and enabling services"
systemctl --user daemon-reload
systemctl --user enable antimicrox.service retro-console.service

echo ""
echo "Done. Reboot to start the services, or run:"
echo "  systemctl --user start antimicrox retro-console"
