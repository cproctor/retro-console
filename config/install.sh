#!/bin/bash
# Install retro-console and its dependencies.
#
# On Linux (Raspberry Pi): copies the repo to /opt/retro-console and installs
# systemd user services so the console starts automatically at boot.
#
# On macOS: installs dependencies in-place for local development. No services
# are installed.
#
# Run as the user who will run the console (not root), but sudo is required
# on Linux for copying files to /opt.
#
# Usage:
#   bash config/install.sh
#
# Linux prerequisites:
#   - antimicrox installed (sudo apt install antimicrox)
#   - uv installed (curl -LsSf https://astral.sh/uv/install.sh | sh)
#   - xterm installed (sudo apt install xterm)
#   - Auto-login to desktop configured (via raspi-config > System > Auto Login)
#
# macOS prerequisites:
#   - Homebrew installed (https://brew.sh)
#   - uv installed (curl -LsSf https://astral.sh/uv/install.sh | sh)

set -euo pipefail

OS="$(uname -s)"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ---------------------------------------------------------------------------
# Audio dependencies
# ---------------------------------------------------------------------------

echo "==> Installing system audio dependencies"
if [[ "$OS" == "Darwin" ]]; then
    brew install fluidsynth
else
    sudo apt-get install -y fluidsynth fluid-soundfont-gm
fi

# ---------------------------------------------------------------------------
# Copy files (Linux only — on macOS we work in-place)
# ---------------------------------------------------------------------------

if [[ "$OS" == "Darwin" ]]; then
    INSTALL_DIR="$REPO_DIR"
    echo "==> macOS: working in-place at $INSTALL_DIR"
else
    INSTALL_DIR=/opt/retro-console
    echo "==> Installing retro-console to $INSTALL_DIR"
    sudo mkdir -p "$INSTALL_DIR"
    sudo rsync -a --delete \
        --exclude='.git' \
        --exclude='.venv' \
        --exclude='*.db' \
        "$REPO_DIR/" "$INSTALL_DIR/"
    sudo chown -R "$USER:$USER" "$INSTALL_DIR"
fi

# ---------------------------------------------------------------------------
# Shared setup
# ---------------------------------------------------------------------------

echo "==> Initialising git submodules"
(cd "$INSTALL_DIR" && git submodule update --init --recursive)

echo "==> Syncing Python dependencies"
(cd "$INSTALL_DIR" && uv sync)

# ---------------------------------------------------------------------------
# Services (Linux only)
# ---------------------------------------------------------------------------

if [[ "$OS" != "Darwin" ]]; then
    SERVICE_DIR="$HOME/.config/systemd/user"

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
else
    echo ""
    echo "Done. To run retro-console:"
    echo "  cd $INSTALL_DIR && uv run retro-console"
fi
