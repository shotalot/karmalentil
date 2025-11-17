#!/usr/bin/env python
"""
123.py - Houdini startup script for KarmaLentil

This script initializes the KarmaLentil plugin on Houdini startup.

NOTE: Lentil parameters are added to cameras via OnCreated callback,
not by modifying the node type. See scripts/lop/camera_OnCreated.py
"""

import hou
import sys
import os


def initialize_karmalentil():
    """
    Initialize KarmaLentil plugin on Houdini startup
    """
    # Get KarmaLentil path from environment
    karmalentil_path = hou.getenv("KARMALENTIL")

    if not karmalentil_path:
        print("KarmaLentil: KARMALENTIL environment variable not set")
        return

    # Add Python path
    python_path = os.path.join(karmalentil_path, "python")
    if os.path.exists(python_path) and python_path not in sys.path:
        sys.path.insert(0, python_path)

    # Initialize lens database
    try:
        from lens_database import LensDatabase
        db = LensDatabase()

        # Store in hou.session for later access
        hou.session.lentil_lens_database = db

        print(f"KarmaLentil: Initialized with {len(db.lenses)} lens models")

    except Exception as e:
        print(f"KarmaLentil: Warning - Could not initialize lens database: {e}")

    # Print welcome message
    print("")
    print("=" * 60)
    print("KarmaLentil - Polynomial Optics for Houdini Karma")
    print("=" * 60)
    print("✓ OnCreated callback installed for camera nodes")
    print("✓ Lentil parameters will be added automatically")
    print("Shelf: karmalentil")
    print("Documentation: $KARMALENTIL/")
    print("")
    print("Quick Start:")
    print("  1. Create a camera LOP node")
    print("  2. Look for the 'Lentil Lens' tab (auto-added!)")
    print("  3. Enable 'Enable Lentil' toggle")
    print("  4. Adjust parameters and render!")
    print("")
    print("  OR use shelf: Click 'Lentil Camera' for complete setup")
    print("=" * 60)
    print("")


# Run initialization
try:
    initialize_karmalentil()
except Exception as e:
    print(f"KarmaLentil: Error during initialization: {e}")
    import traceback
    traceback.print_exc()
