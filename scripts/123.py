#!/usr/bin/env python
"""
123.py - Houdini startup script for KarmaLentil
Automatically loads when Houdini starts
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

    # Check if HDA exists (don't build during startup - UI not ready yet)
    hda_path = os.path.join(karmalentil_path, "otls", "karmalentil_camera.hda")
    if not os.path.exists(hda_path):
        print("KarmaLentil: Camera HDA not found (will be built on first use)")
        print("  Click 'Lentil Camera' shelf tool to auto-build")

    # Initialize lens database
    try:
        from lens_database import LensDatabase
        db = LensDatabase()

        # Store in hou.session for later access
        hou.session.lentil_lens_database = db

        print("KarmaLentil: Initialized with {} lens models".format(len(db.lenses)))

    except Exception as e:
        print("KarmaLentil: Warning - Could not initialize lens database: {}".format(e))

    # Print welcome message
    hda_status = "ready" if os.path.exists(hda_path) else "will build on first use"

    print("")
    print("=" * 60)
    print("KarmaLentil - Polynomial Optics for Houdini Karma")
    print("=" * 60)
    print("HDA: karmalentil::camera::1.0 ({})".format(hda_status))
    print("Shelf: karmalentil")
    print("Documentation: $KARMALENTIL/")
    print("")
    print("Quick Start:")
    print("  Method 1: TAB -> 'karmalentil' -> Drop in LOP network")
    print("  Method 2: Click 'Lentil Camera' shelf tool")
    print("")
    print("  Then: Adjust 'Lentil Lens' tab and render!")
    print("=" * 60)
    print("")


# Run initialization
try:
    initialize_karmalentil()
except Exception as e:
    print("KarmaLentil: Error during initialization: {}".format(e))
    import traceback
    traceback.print_exc()
