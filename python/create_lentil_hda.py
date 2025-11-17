#!/usr/bin/env python
"""
Create Lentil Camera HDA
Builds a complete Houdini Digital Asset for lentil camera integration
"""

import hou
import os


def create_lentil_camera_hda():
    """
    Create a complete lentil camera HDA with integrated features
    """
    # Create camera at OBJ level
    obj = hou.node('/obj')

    # Create base camera
    cam_subnet = obj.createNode('subnet', 'lentil_camera_setup')

    # Create camera inside
    cam = cam_subnet.createNode('cam', 'lentil_cam')

    # Add render node
    null_out = cam_subnet.createNode('null', 'OUT')
    null_out.setInput(0, cam)
    null_out.setDisplayFlag(True)
    null_out.setRenderFlag(True)

    # Set camera as output
    cam_subnet.setDisplayFlag(False)

    # Build parameter interface
    parm_template_group = cam_subnet.parmTemplateGroup()

    # Clear default parameters
    parm_template_group.clear()

    # Transform folder (from camera)
    transform_folder = hou.FolderParmTemplate('xform', 'Transform')
    transform_folder.addParmTemplate(hou.FloatParmTemplate('tx', 'Translate X', 1, default_value=[0]))
    transform_folder.addParmTemplate(hou.FloatParmTemplate('ty', 'Translate Y', 1, default_value=[1]))
    transform_folder.addParmTemplate(hou.FloatParmTemplate('tz', 'Translate Z', 1, default_value=[5]))
    transform_folder.addParmTemplate(hou.FloatParmTemplate('rx', 'Rotate X', 1, default_value=[0]))
    transform_folder.addParmTemplate(hou.FloatParmTemplate('ry', 'Rotate Y', 1, default_value=[0]))
    transform_folder.addParmTemplate(hou.FloatParmTemplate('rz', 'Rotate Z', 1, default_value=[0]))

    parm_template_group.append(transform_folder)

    # Lentil Lens folder
    lentil_folder = hou.FolderParmTemplate('lentil', 'Lentil Lens')

    # Enable toggle
    lentil_folder.addParmTemplate(
        hou.ToggleParmTemplate(
            'enable_lentil',
            'Enable Lentil',
            default_value=True,
            help='Enable polynomial optics lens simulation'
        )
    )

    # Lens model selector
    lens_menu = hou.MenuParmTemplate(
        'lens_model',
        'Lens Model',
        menu_items=(['double_gauss_50mm', 'double_gauss_35mm', 'telephoto_85mm']),
        menu_labels=(['Double Gauss 50mm f/2.8', 'Double Gauss 35mm (Placeholder)', 'Telephoto 85mm (Placeholder)']),
        default_value=0,
        help='Lens model to use'
    )
    lentil_folder.addParmTemplate(lens_menu)

    # Focal length
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'focal_length',
            'Focal Length',
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
            'fstop',
            'F-Stop',
            1,
            default_value=[2.8],
            min=0.0,
            max=64.0,
            help='Aperture f-stop (0 = wide open)',
            naming_scheme=hou.parmNamingScheme.Base1
        )
    )

    # Focus distance
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'focus_distance',
            'Focus Distance',
            1,
            default_value=[1000.0],
            min=0.1,
            help='Focus distance in millimeters'
        )
    )

    # Sensor width
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'sensor_width',
            'Sensor Width',
            1,
            default_value=[36.0],
            min=1.0,
            max=100.0,
            help='Sensor width in millimeters (36mm = full frame)'
        )
    )

    parm_template_group.append(lentil_folder)

    # Aberrations folder
    aberrations_folder = hou.FolderParmTemplate('aberrations', 'Aberrations & Effects')

    # Chromatic aberration
    aberrations_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'chromatic_aberration',
            'Chromatic Aberration',
            1,
            default_value=[1.0],
            min=0.0,
            max=2.0,
            help='Chromatic aberration strength (0 = disabled)'
        )
    )

    parm_template_group.append(aberrations_folder)

    # Bokeh folder
    bokeh_folder = hou.FolderParmTemplate('bokeh', 'Bokeh')

    # Bokeh blades
    bokeh_folder.addParmTemplate(
        hou.IntParmTemplate(
            'bokeh_blades',
            'Bokeh Blades',
            1,
            default_value=[0],
            min=0,
            max=16,
            help='Number of aperture blades (0-3 = circular, 4+ = polygonal)'
        )
    )

    # Bokeh rotation
    bokeh_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'bokeh_rotation',
            'Bokeh Rotation',
            1,
            default_value=[0.0],
            min=0.0,
            max=360.0,
            help='Aperture blade rotation in degrees'
        )
    )

    # Aperture texture
    bokeh_folder.addParmTemplate(
        hou.StringParmTemplate(
            'aperture_texture',
            'Aperture Texture',
            1,
            default_value=[''],
            string_type=hou.stringParmType.FileReference,
            file_type=hou.fileType.Image,
            help='Custom aperture texture for bokeh shape (leave empty for default)'
        )
    )

    bokeh_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'aperture_rotation',
            'Aperture Texture Rotation',
            1,
            default_value=[0.0],
            min=0.0,
            max=360.0,
            help='Rotation of aperture texture in degrees'
        )
    )

    parm_template_group.append(bokeh_folder)

    # Bidirectional folder
    bidir_folder = hou.FolderParmTemplate('bidirectional', 'Bidirectional Filtering')

    bidir_folder.addParmTemplate(
        hou.ToggleParmTemplate(
            'enable_bidirectional',
            'Enable Bidirectional',
            default_value=True,
            help='Enable bidirectional filtering for realistic bokeh'
        )
    )

    bidir_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'bidirectional_quality',
            'Filter Quality',
            1,
            default_value=[1.0],
            min=0.1,
            max=2.0,
            help='Bidirectional filter quality (higher = smoother bokeh, slower)'
        )
    )

    bidir_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'bokeh_intensity',
            'Bokeh Intensity',
            1,
            default_value=[1.0],
            min=0.0,
            max=3.0,
            help='Intensity boost for bokeh highlights'
        )
    )

    parm_template_group.append(bidir_folder)

    # Set parameter template group
    cam_subnet.setParmTemplateGroup(parm_template_group)

    # Link parameters from subnet to internal camera
    # Transform
    cam.parm('tx').setExpression('ch("../tx")')
    cam.parm('ty').setExpression('ch("../ty")')
    cam.parm('tz').setExpression('ch("../tz")')
    cam.parm('rx').setExpression('ch("../rx")')
    cam.parm('ry').setExpression('ch("../ry")')
    cam.parm('rz').setExpression('ch("../rz")')

    # Camera settings
    cam.parm('focal').setExpression('ch("../focal_length")')
    cam.parm('aperture').setExpression('ch("../sensor_width")')
    cam.parm('focus').setExpression('ch("../focus_distance") * 0.001')  # Convert mm to m
    cam.parm('fstop').setExpression('ch("../fstop")')

    # Layout
    cam_subnet.layoutChildren()

    print(f"Created lentil camera setup: {cam_subnet.path()}")
    print("\nTo create HDA:")
    print("1. Right-click the node → 'Create Digital Asset...'")
    print("2. Set operator name: 'lentil_camera'")
    print("3. Set operator label: 'Lentil Camera'")
    print("4. Set save location: $HIP/otls/lentil_camera.hda")
    print("5. Click 'Accept'")

    return cam_subnet


def setup_karma_material_for_camera(cam_node):
    """
    Setup Karma material network for lentil camera
    """
    # This would create a material network with the VEX camera shader
    # For now, provide instructions

    print("\nKarma Material Setup:")
    print("1. Create /shop/vopmaterial network")
    print("2. Inside, create Camera VOP")
    print("3. Add Inline Code VOP")
    print("4. Load vex/camera/lentil_camera_integrated.vfl")
    print("5. Assign to camera")

    pass


def main():
    """
    Main function to create lentil camera HDA
    """
    print("=" * 70)
    print("Creating Lentil Camera HDA")
    print("=" * 70)

    try:
        cam_subnet = create_lentil_camera_hda()

        print("\n" + "=" * 70)
        print("Next Steps:")
        print("=" * 70)
        print("\n1. Convert to HDA:")
        print("   Right-click node → Create Digital Asset")
        print("   Save to: $KARMALENTIL/otls/lentil_camera.hda")
        print("\n2. Setup Karma integration:")
        print("   - Create camera shader material")
        print("   - Assign to camera")
        print("   - Configure render settings")
        print("\n3. Test in viewport and render")

        return cam_subnet

    except Exception as e:
        print(f"Error creating HDA: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    main()
