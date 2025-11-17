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

    # Build HDA if it doesn't exist
    hda_path = os.path.join(karmalentil_path, "otls", "karmalentil_camera.hda")
    if not os.path.exists(hda_path):
        print("KarmaLentil: Building camera HDA for first-time use...")
        try:
            import create_lentil_camera_hda
            create_lentil_camera_hda.create_lentil_camera_hda()
            print("KarmaLentil: HDA built successfully!")
        except Exception as e:
            print("KarmaLentil: Warning - Could not build HDA: {}".format(e))
            print("  You can build it manually: Python Shell -> import create_lentil_camera_hda; create_lentil_camera_hda.create_lentil_camera_hda()")

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
    print("")
    print("=" * 60)
    print("KarmaLentil - Polynomial Optics for Houdini Karma")
    print("=" * 60)
    print("HDA: karmalentil::camera::1.0 (ready to use)")
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
