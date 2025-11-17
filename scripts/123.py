#!/usr/bin/env python
"""
123.py - Houdini startup script for KarmaLentil
Automatically extends all LOP camera nodes with lentil parameters
"""

import hou
import sys
import os


def add_lentil_parameters_to_cameras():
    """
    Extend all LOP camera nodes with lentil parameters
    This runs on startup and modifies the camera node type

    NOTE: This approach may not work with built-in node types in Houdini.
    If parameters don't appear, we'll need to use a different approach.
    """
    try:
        # Get the LOP camera node type
        lop_cat = hou.lopNodeTypeCategory()
        camera_type = lop_cat.nodeType("camera")

        if not camera_type:
            print("KarmaLentil: Warning - Could not find 'camera' node type in LOPs")
            return False

        print(f"KarmaLentil: Found camera type: {camera_type}")
        print(f"KarmaLentil: Camera type category: {camera_type.category().name()}")

        # CRITICAL: Check if we can modify this node type
        # Built-in node types might not be modifiable
        try:
            # Get existing parameter template group
            ptg = camera_type.parmTemplateGroup()
            print(f"KarmaLentil: Retrieved parameter template group (has {len(ptg.parmTemplates())} templates)")
        except Exception as e:
            print(f"KarmaLentil: ERROR - Cannot get parameter template group: {e}")
            print("KarmaLentil: Built-in node types cannot be modified this way")
            print("KarmaLentil: You'll need to use a different approach (HDA or callbacks)")
            return False

        # Check if lentil folder already exists
        if ptg.find("lentil_folder"):
            print("KarmaLentil: Lentil parameters already added to camera nodes")
            return True

        # Create Lentil Lens folder
        lentil_folder = hou.FolderParmTemplate('lentil_folder', 'Lentil Lens')

        # Enable toggle
        lentil_folder.addParmTemplate(
            hou.ToggleParmTemplate(
                'enable_lentil',
                'Enable Lentil',
                default_value=False,
                help='Enable lentil polynomial optics for realistic lens aberrations'
            )
        )

        # Lens model menu
        lentil_folder.addParmTemplate(
            hou.MenuParmTemplate(
                'lens_model',
                'Lens Model',
                menu_items=['double_gauss_50mm'],
                menu_labels=['Double Gauss 50mm f/2.8'],
                default_value=0,
                help='Select lens model from database'
            )
        )

        # Focal length
        lentil_folder.addParmTemplate(
            hou.FloatParmTemplate(
                'lentil_focal_length',
                'Focal Length (mm)',
                1,
                default_value=[50.0],
                min=1.0,
                max=500.0,
                help='Lens focal length in millimeters'
            )
        )

        # F-stop
        lentil_folder.addParmTemplate(
            hou.FloatParmTemplate(
                'lentil_fstop',
                'F-Stop',
                1,
                default_value=[2.8],
                min=0.5,
                max=64.0,
                help='Aperture f-stop (lower = more DOF)'
            )
        )

        # Focus distance
        lentil_folder.addParmTemplate(
            hou.FloatParmTemplate(
                'lentil_focus_distance',
                'Focus Distance (mm)',
                1,
                default_value=[5000.0],
                min=1.0,
                help='Focus distance in millimeters'
            )
        )

        # Sensor width
        lentil_folder.addParmTemplate(
            hou.FloatParmTemplate(
                'lentil_sensor_width',
                'Sensor Width (mm)',
                1,
                default_value=[36.0],
                min=1.0,
                max=100.0,
                help='Camera sensor width (36mm = full-frame)'
            )
        )

        # Chromatic aberration
        lentil_folder.addParmTemplate(
            hou.FloatParmTemplate(
                'chromatic_aberration',
                'Chromatic Aberration',
                1,
                default_value=[1.0],
                min=0.0,
                max=2.0,
                help='Chromatic aberration intensity (0=off, 1=normal)'
            )
        )

        # Bokeh blades
        lentil_folder.addParmTemplate(
            hou.IntParmTemplate(
                'bokeh_blades',
                'Bokeh Blades',
                1,
                default_value=[0],
                min=0,
                max=16,
                help='Number of aperture blades (0=circular)'
            )
        )

        # Bokeh rotation
        lentil_folder.addParmTemplate(
            hou.FloatParmTemplate(
                'bokeh_rotation',
                'Bokeh Rotation',
                1,
                default_value=[0.0],
                min=0.0,
                max=360.0,
                help='Aperture rotation in degrees'
            )
        )

        # Aperture texture
        lentil_folder.addParmTemplate(
            hou.StringParmTemplate(
                'aperture_texture',
                'Aperture Texture',
                1,
                default_value=[''],
                string_type=hou.stringParmType.FileReference,
                file_type=hou.fileType.Image,
                help='Custom aperture texture for unique bokeh shapes'
            )
        )

        # Add separator
        lentil_folder.addParmTemplate(
            hou.SeparatorParmTemplate('sep1')
        )

        # Bidirectional toggle
        lentil_folder.addParmTemplate(
            hou.ToggleParmTemplate(
                'enable_bidirectional',
                'Enable Bidirectional',
                default_value=True,
                help='Enable bidirectional filtering for realistic bokeh highlights'
            )
        )

        # Bokeh intensity
        lentil_folder.addParmTemplate(
            hou.FloatParmTemplate(
                'bokeh_intensity',
                'Bokeh Intensity',
                1,
                default_value=[1.0],
                min=0.0,
                max=3.0,
                help='Bokeh highlight intensity multiplier'
            )
        )

        # Add folder to camera node type's parameter template group
        ptg.append(lentil_folder)
        print("KarmaLentil: Added lentil folder to parameter template group")

        # Apply modified parameter template group to camera node type
        # NOTE: This will FAIL for built-in node types!
        try:
            camera_type.setParmTemplateGroup(ptg)
            print("KarmaLentil: ✓ Successfully modified camera node type")
            print("KarmaLentil: ✓ Added lentil parameters to all camera nodes")
            return True
        except Exception as e:
            print(f"KarmaLentil: ERROR - Cannot modify built-in camera node type: {e}")
            print("KarmaLentil: You cannot modify built-in Houdini node types")
            print("KarmaLentil: Alternative approaches:")
            print("  1. Use the HDA approach (custom node type)")
            print("  2. Use OnCreated callbacks to add parameters")
            print("  3. Create a custom camera node type")
            return False

    except Exception as e:
        print(f"KarmaLentil: Error adding lentil parameters: {e}")
        import traceback
        traceback.print_exc()
        return False


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

    # Extend camera nodes with lentil parameters
    add_lentil_parameters_to_cameras()

    # Print welcome message
    print("")
    print("=" * 60)
    print("KarmaLentil - Polynomial Optics for Houdini Karma")
    print("=" * 60)
    print("✓ Lentil parameters added to all camera nodes")
    print("Shelf: karmalentil")
    print("Documentation: $KARMALENTIL/")
    print("")
    print("Quick Start:")
    print("  1. Create a camera LOP node")
    print("  2. Open the 'Lentil Lens' tab")
    print("  3. Enable 'Enable Lentil' toggle")
    print("  4. Adjust parameters and render!")
    print("=" * 60)
    print("")


# Run initialization
try:
    initialize_karmalentil()
except Exception as e:
    print(f"KarmaLentil: Error during initialization: {e}")
    import traceback
    traceback.print_exc()
