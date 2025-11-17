#!/bin/bash
# install_karmalentil.sh
# Simple installation script for KarmaLentil

echo "=========================================="
echo "KarmaLentil Installation"
echo "=========================================="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Detect Houdini version
HOUDINI_VERSIONS=(
    "$HOME/houdini20.5"
    "$HOME/houdini20.0"
    "$HOME/houdini19.5"
)

HOUDINI_USER_DIR=""
for dir in "${HOUDINI_VERSIONS[@]}"; do
    if [ -d "$dir" ]; then
        HOUDINI_USER_DIR="$dir"
        break
    fi
done

if [ -z "$HOUDINI_USER_DIR" ]; then
    echo "Error: Could not find Houdini user directory"
    echo "Please manually add to houdini.env:"
    echo "  KARMALENTIL_PATH = \"$SCRIPT_DIR\""
    echo "Or create a package file in packages/ directory"
    exit 1
fi

echo "Found Houdini directory: $HOUDINI_USER_DIR"
echo ""

# Installation method selection
echo "Select installation method:"
echo "  1. Package file (recommended - automatic loading)"
echo "  2. houdini.env (manual - requires restart)"
echo ""
read -p "Choice [1]: " choice
choice=${choice:-1}

if [ "$choice" == "1" ]; then
    # Create packages directory if it doesn't exist
    PACKAGES_DIR="$HOUDINI_USER_DIR/packages"
    mkdir -p "$PACKAGES_DIR"

    # Create package JSON
    PACKAGE_FILE="$PACKAGES_DIR/karmalentil.json"

    cat > "$PACKAGE_FILE" <<EOF
{
    "env": [
        {
            "KARMALENTIL_PATH": "$SCRIPT_DIR"
        },
        {
            "KARMALENTIL": "\$KARMALENTIL_PATH"
        },
        {
            "HOUDINI_PATH": "\$KARMALENTIL_PATH;&"
        },
        {
            "PYTHONPATH": "\$KARMALENTIL_PATH/python:&"
        }
    ]
}
EOF

    echo ""
    echo "✓ Package file created: $PACKAGE_FILE"
    echo ""
    echo "Installation complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Launch Houdini"
    echo "  2. Find 'karmalentil' shelf"
    echo "  3. Click 'Lentil Camera' to create a camera"
    echo ""

elif [ "$choice" == "2" ]; then
    # Add to houdini.env
    ENV_FILE="$HOUDINI_USER_DIR/houdini.env"

    # Backup existing env file
    if [ -f "$ENV_FILE" ]; then
        cp "$ENV_FILE" "$ENV_FILE.backup"
        echo "✓ Backed up existing houdini.env"
    fi

    # Add KarmaLentil configuration
    cat >> "$ENV_FILE" <<EOF

# KarmaLentil - Polynomial Optics Plugin
KARMALENTIL_PATH = "$SCRIPT_DIR"
KARMALENTIL = "\$KARMALENTIL_PATH"
HOUDINI_PATH = "\$KARMALENTIL_PATH:&"
PYTHONPATH = "\$KARMALENTIL_PATH/python:&"
EOF

    echo ""
    echo "✓ Updated houdini.env: $ENV_FILE"
    echo ""
    echo "Installation complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Restart Houdini (required)"
    echo "  2. Find 'karmalentil' shelf"
    echo "  3. Click 'Lentil Camera' to create a camera"
    echo ""

else
    echo "Invalid choice. Exiting."
    exit 1
fi

echo "=========================================="
echo "For help, see: $SCRIPT_DIR/README.md"
echo "=========================================="
