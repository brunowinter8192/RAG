#!/bin/bash
# Install the RAG idle watchdog as a macOS LaunchAgent.
# Runs every 15 minutes; stops GPU servers idle > IDLE_TIMEOUT (default 60 min).
# Usage: ./scripts/install_watchdog.sh [--uninstall]
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RAG_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PYTHON="$RAG_ROOT/venv/bin/python3"
WATCHDOG_SCRIPT="$SCRIPT_DIR/idle_watchdog.py"
PLIST_LABEL="com.rag.idle-watchdog"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCHD_DIR/$PLIST_LABEL.plist"

if [ "$1" = "--uninstall" ]; then
    echo "Uninstalling RAG idle watchdog..."
    launchctl unload "$PLIST_PATH" 2>/dev/null && echo "  Unloaded" || echo "  Not loaded"
    rm -f "$PLIST_PATH" && echo "  Removed $PLIST_PATH"
    echo "Done."
    exit 0
fi

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: venv python not found at $VENV_PYTHON"
    echo "Run: cd $RAG_ROOT && python3 -m venv venv && pip install -r requirements.txt"
    exit 1
fi

mkdir -p "$LAUNCHD_DIR"
mkdir -p "$HOME/.rag-locks"

cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV_PYTHON</string>
        <string>$WATCHDOG_SCRIPT</string>
    </array>
    <key>StartInterval</key>
    <integer>900</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.rag-locks/watchdog.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.rag-locks/watchdog.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>RAG_PROJECT_ROOT</key>
        <string>$RAG_ROOT</string>
    </dict>
</dict>
</plist>
PLIST

# Unload existing if present, then load
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo "RAG idle watchdog installed and loaded."
echo "  Label:    $PLIST_LABEL"
echo "  Interval: every 15 minutes"
echo "  Log:      ~/.rag-locks/watchdog.log"
echo "  Uninstall: $SCRIPT_DIR/install_watchdog.sh --uninstall"
