#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${PARAKRAM_VPS_INSTALL_DIR:-/opt/parakram-vps}"
SERVICE_FILE="/etc/systemd/system/parakram-vps.service"
PYTHON_BIN="${PYTHON_BIN:-/usr/bin/python3}"

mkdir -p "$INSTALL_DIR"
cp -R "$(dirname "$0")"/core "$INSTALL_DIR"/core
cp "$(dirname "$0")"/app.py "$INSTALL_DIR"/app.py
cp "$(dirname "$0")"/requirements.txt "$INSTALL_DIR"/requirements.txt

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Parakram VPS
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$INSTALL_DIR
ExecStart=$PYTHON_BIN $INSTALL_DIR/app.py run
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable parakram-vps.service
systemctl restart parakram-vps.service
