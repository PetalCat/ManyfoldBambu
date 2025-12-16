#!/bin/bash

HOST_NAME="com.manyfold.bambu"
DESCRIPTION="Manyfold Bambu Studio Helper"
HOST_SCRIPT="bambu_host.py"

# Detect directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
HOST_PATH="$SCRIPT_DIR/$HOST_SCRIPT"

echo "Installing Manyfold Bambu Host..."

# 0. Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "It should be pre-installed on macOS or available via 'xcode-select --install'."
    else
        echo "Please install it using your package manager (e.g., 'sudo apt install python3')."
    fi
    exit 1
fi

# 1. Get Extension ID
echo "Example ID: knldjmfmopnpolahpmmgbagdohdnhkik"
# Check if ID is passed as argument
if [ -n "$1" ]; then
    EXTENSION_ID=$1
    echo "Using Extension ID from argument: $EXTENSION_ID"
else
    echo "Enter your Extension ID (from chrome://extensions):"
    read EXTENSION_ID
fi

if [ -z "$EXTENSION_ID" ]; then
    echo "Extension ID is required."
    exit 1
fi

# 2. Verify Host Script
if [ ! -f "$HOST_PATH" ]; then
    echo "Error: Could not find $HOST_SCRIPT at $HOST_PATH"
    exit 1
fi

# Make executable
chmod +x "$HOST_PATH"

# 3. Define Manifest Paths based on OS
OS="$(uname -s)"
MANIFEST_PATHS=()

case "$OS" in
    Darwin*)    
        # Mac Paths
        MANIFEST_PATHS+=("$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts/$HOST_NAME.json")
        MANIFEST_PATHS+=("$HOME/Library/Application Support/Microsoft Edge/NativeMessagingHosts/$HOST_NAME.json")
        ;;
    Linux*)     
        # Linux Paths
        MANIFEST_PATHS+=("$HOME/.config/google-chrome/NativeMessagingHosts/$HOST_NAME.json")
        MANIFEST_PATHS+=("$HOME/.config/microsoft-edge/NativeMessagingHosts/$HOST_NAME.json")
        ;;
    *)          
        echo "Unsupported OS: $OS" 
        exit 1 ;;
esac

# 4. Generate and Install Manifest
for MANIFEST_PATH in "${MANIFEST_PATHS[@]}"; do
    TARGET_DIR="$(dirname "$MANIFEST_PATH")"
    if [ ! -d "$TARGET_DIR" ]; then
        mkdir -p "$TARGET_DIR"
    fi
    
    # Write JSON using cat/EOF
cat > "$MANIFEST_PATH" <<EOF
{
  "name": "$HOST_NAME",
  "description": "$DESCRIPTION",
  "path": "$HOST_PATH",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://$EXTENSION_ID/"
  ]
}
EOF
    echo "Installed for $(basename "$TARGET_DIR") at $MANIFEST_PATH"
done

echo ""
echo "Installation Complete!"
echo "Host script location: $HOST_PATH"
echo "Please reload your extension."
