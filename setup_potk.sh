#!/bin/bash
# Setup script for POTK (Polynomial Optics to Karma)
# This clones the required polynomial-optics library

set -e

echo "=========================================="
echo "POTK Setup - Cloning polynomial-optics"
echo "=========================================="

# Create ext directory if it doesn't exist
mkdir -p ext

# Clone lentil repository (contains polynomial-optics)
echo "Cloning lentil repository (this may take a while)..."
git clone --branch dev https://github.com/zpelgrims/lentil.git ext/lentil

# Initialize submodules (polynomial-optics and dependencies)
echo "Initializing submodules..."
cd ext/lentil
git submodule update --init --recursive
cd ../..

echo ""
echo "✓ Setup complete!"
echo ""
echo "polynomial-optics library is now available at:"
echo "  ext/lentil/polynomial-optics/"
echo ""
echo "Next steps:"
echo "  1. Build polynomial-optics: see POTK_IMPLEMENTATION_PLAN.md"
echo "  2. Create Python bindings"
echo "  3. Build lens import tools"
echo ""
