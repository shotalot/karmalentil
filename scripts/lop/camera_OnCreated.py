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

    # Create Lentil Lens folder
    lentil_folder = hou.FolderParmTemplate('lentil_folder', 'Lentil Lens', folder_type=hou.folderType.Tabs)

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
            menu_items=('double_gauss_50mm',),
            menu_labels=('Double Gauss 50mm f/2.8',),
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
            default_value=(50.0,),
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
            default_value=(2.8,),
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
            default_value=(5000.0,),
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
            default_value=(36.0,),
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
            default_value=(1.0,),
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
            default_value=(0,),
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
            default_value=(0.0,),
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
            default_value=(1.0,),
            min=0.0,
            max=3.0,
            help='Bokeh highlight intensity multiplier'
        )
    )

    # Add the folder to the node's parameter template group
    ptg.append(lentil_folder)

    # Apply the modified parameter template group back to the node
    node.setParmTemplateGroup(ptg)


# This is the main entry point - called automatically when camera node is created
kwargs = globals().get('kwargs', {})
node = kwargs.get('node')

if node:
    try:
        add_lentil_spare_parameters(node)
    except Exception as e:
        # Silent failure - don't break camera creation if something goes wrong
        print(f"KarmaLentil: Warning - Could not add spare parameters: {e}")
