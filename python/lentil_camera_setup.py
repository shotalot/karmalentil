"""
camera_OnCreated.py - Automatically adds lentil parameters to camera nodes

This script runs AUTOMATICALLY whenever a camera LOP node is created.
Place in: $HOUDINI_PATH/scripts/lop/camera_OnCreated.py

This is how Redshift, Arnold, and other render engines add their custom
parameters to standard Houdini nodes!
"""

import hou


def add_lentil_spare_parameters(node):
    """
    Add lentil parameters as spare parameters to a camera node

    Args:
        node: The camera node that was just created
    """
    # Get the node's current parameter template group
    ptg = node.parmTemplateGroup()

    # Check if lentil parameters already exist
    if ptg.find('enable_lentil'):
        return  # Already added

    # IMPORTANT: Preserve existing folder structure
    # Log existing folders for debugging
    existing_folders = []
    for pt in ptg.entries():
        if isinstance(pt, hou.FolderParmTemplate):
            existing_folders.append(pt.name())

    print(f"KarmaLentil: Found existing folders: {existing_folders}")

    # Create Lentil Lens folder
    lentil_folder = hou.FolderParmTemplate('lentil_folder', 'Lentil Lens', folder_type=hou.folderType.Tabs)

    # Enable toggle (with callback)
    enable_parm = hou.ToggleParmTemplate(
        'enable_lentil',
        'Enable Lentil',
        default_value=False,
        help='Enable lentil polynomial optics for realistic lens aberrations'
    )
    # Add callback that runs when parameter changes
    enable_parm.setTags({
        'script_callback': 'import lentil_callbacks; lentil_callbacks.on_enable_changed(kwargs)',
        'script_callback_language': 'python'
    })
    lentil_folder.addParmTemplate(enable_parm)

    # Lens model menu - dynamically populated from lens database
    # Get lens database and generate menu
    try:
        import sys
        import os
        karmalentil_path = hou.getenv('KARMALENTIL')
        if karmalentil_path:
            python_path = os.path.join(karmalentil_path, 'python')
            if python_path not in sys.path:
                sys.path.insert(0, python_path)

        from lens_database import get_lens_database
        db = get_lens_database()
        menu_items, menu_labels = db.generate_menu_items()
    except Exception as e:
        print(f"KarmaLentil: Warning - Could not load lens database: {e}")
        # Fallback to default lens
        menu_items = ['double_gauss_50mm']
        menu_labels = ['Double Gauss 50mm f/2.8']

    # Lens model menu (with callback)
    lens_model_parm = hou.MenuParmTemplate(
        'lens_model',
        'Lens Model',
        menu_items=tuple(menu_items),
        menu_labels=tuple(menu_labels),
        default_value=0,
        help='Select lens model from database'
    )
    # Add callback to auto-update lens parameters when model changes
    lens_model_parm.setTags({
        'script_callback': 'import lentil_callbacks; lentil_callbacks.on_lens_model_changed(kwargs)',
        'script_callback_language': 'python'
    })
    lentil_folder.addParmTemplate(lens_model_parm)

    # Focal length (with callback)
    focal_parm = hou.FloatParmTemplate(
        'lentil_focal_length',
        'Focal Length (mm)',
        1,
        default_value=(50.0,),
        min=1.0,
        max=500.0,
        help='Lens focal length in millimeters'
    )
    focal_parm.setTags({
        'script_callback': 'import lentil_callbacks; lentil_callbacks.update_lens_parameters(kwargs)',
        'script_callback_language': 'python'
    })
    lentil_folder.addParmTemplate(focal_parm)

    # F-stop (with callback)
    fstop_parm = hou.FloatParmTemplate(
        'lentil_fstop',
        'F-Stop',
        1,
        default_value=(2.8,),
        min=0.5,
        max=64.0,
        help='Aperture f-stop (lower = more DOF)'
    )
    fstop_parm.setTags({
        'script_callback': 'import lentil_callbacks; lentil_callbacks.update_lens_parameters(kwargs)',
        'script_callback_language': 'python'
    })
    lentil_folder.addParmTemplate(fstop_parm)

    # Focus distance (with callback)
    focus_parm = hou.FloatParmTemplate(
        'lentil_focus_distance',
        'Focus Distance (mm)',
        1,
        default_value=(5000.0,),
        min=1.0,
        help='Focus distance in millimeters'
    )
    focus_parm.setTags({
        'script_callback': 'import lentil_callbacks; lentil_callbacks.update_lens_parameters(kwargs)',
        'script_callback_language': 'python'
    })
    lentil_folder.addParmTemplate(focus_parm)

    # Sensor width
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_sensor_width',
            'Sensor Width (mm)',
            1,
            default_value=(36.0,),
            min=1.0,
            max=100.0,
            help='Camera sensor width (36mm = full-frame)'
        )
    )

    # Sensor shift (like extra_sensor_shift in original lentil)
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_sensor_shift',
            'Sensor Shift',
            2,
            default_value=(0.0, 0.0),
            min=-10.0,
            max=10.0,
            naming_scheme=hou.parmNamingScheme.XYZW,
            help='Sensor shift in mm (for tilt-shift / perspective control)'
        )
    )

    # Wavelength (like original lentil)
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_wavelength',
            'Wavelength (nm)',
            1,
            default_value=(550.0,),
            min=390.0,
            max=700.0,
            help='Light wavelength in nanometers (390=violet, 550=green, 700=red)'
        )
    )

    # Chromatic aberration
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_chromatic_aberration',
            'Chromatic Aberration',
            1,
            default_value=(1.0,),
            min=0.0,
            max=2.0,
            help='Chromatic aberration intensity (0=off, 1=normal)'
        )
    )

    # Bokeh blades
    lentil_folder.addParmTemplate(
        hou.IntParmTemplate(
            'lentil_bokeh_blades',
            'Bokeh Blades',
            1,
            default_value=(0,),
            min=0,
            max=16,
            help='Number of aperture blades (0=circular)'
        )
    )

    # Bokeh rotation
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_bokeh_rotation',
            'Bokeh Rotation',
            1,
            default_value=(0.0,),
            min=0.0,
            max=360.0,
            help='Aperture rotation in degrees'
        )
    )

    # Aperture texture
    lentil_folder.addParmTemplate(
        hou.StringParmTemplate(
            'lentil_aperture_texture',
            'Aperture Texture',
            1,
            default_value=('',),
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
            'lentil_enable_bidirectional',
            'Enable Bidirectional',
            default_value=True,
            help='Enable bidirectional filtering for realistic bokeh highlights'
        )
    )

    # Bokeh intensity
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_bokeh_intensity',
            'Bokeh Intensity',
            1,
            default_value=(1.0,),
            min=0.0,
            max=3.0,
            help='Bokeh highlight intensity multiplier'
        )
    )

    # Simply append the lentil folder at the end
    # This is the safest approach - doesn't interfere with any existing folders
    ptg.append(lentil_folder)

    # Apply the modified parameter template group back to the node
    node.setParmTemplateGroup(ptg)

    print(f"KarmaLentil: Successfully added Lentil Lens tab to camera")


# DISABLED: OnCreated callback has been disabled to preserve Karma tab
# Use the "Add Lentil to Camera" shelf tool instead

# This is the main entry point - called automatically when camera node is created
# kwargs = globals().get('kwargs', {})
# node = kwargs.get('node')
#
# if node:
#     try:
#         add_lentil_spare_parameters(node)
#     except Exception as e:
#         # Don't break camera creation if something goes wrong
#         print(f"KarmaLentil: Warning - Could not add spare parameters: {e}")
#         import traceback
#         traceback.print_exc()

# The add_lentil_spare_parameters function is still available for the shelf tool to use
# Just import this file and call the function manually
