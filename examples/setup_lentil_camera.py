"""
Example: Setup a Lentil Camera in Houdini
This script creates a camera with lentil parameters for use with Karma
"""

import hou


def create_lentil_camera(name='lentil_camera'):
    """
    Create a camera node with lentil parameters

    Args:
        name: Name for the camera node

    Returns:
        Camera node
    """
    # Create camera
    obj_network = hou.node('/obj')
    cam = obj_network.createNode('cam', name)

    # Get parameter template group
    parm_template_group = cam.parmTemplateGroup()

    # Create lentil folder
    lentil_folder = hou.FolderParmTemplate('lentil_folder', 'Lentil Lens')

    # Add enable toggle
    lentil_folder.addParmTemplate(
        hou.ToggleParmTemplate(
            'enable_lentil',
            'Enable Lentil',
            default_value=True,
            help='Enable polynomial optics lens simulation'
        )
    )

    # Add lens model selector
    lentil_folder.addParmTemplate(
        hou.StringParmTemplate(
            'lens_model',
            'Lens Model',
            1,
            default_value=['double_gauss_50mm'],
            string_type=hou.stringParmType.Regular,
            help='Lens model to use for polynomial evaluation'
        )
    )

    # Add focal length
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_focal_length',
            'Focal Length',
            1,
            default_value=[50.0],
            min=1.0,
            max=500.0,
            help='Lens focal length in millimeters'
        )
    )

    # Add f-stop
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_fstop',
            'F-Stop',
            1,
            default_value=[2.8],
            min=0.0,
            max=64.0,
            help='Aperture f-stop (0 = wide open)'
        )
    )

    # Add focus distance
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_focus_distance',
            'Focus Distance',
            1,
            default_value=[1000.0],
            min=0.1,
            help='Focus distance in millimeters'
        )
    )

    # Add sensor width
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_sensor_width',
            'Sensor Width',
            1,
            default_value=[36.0],
            min=1.0,
            max=100.0,
            help='Sensor width in millimeters (36mm = full frame)'
        )
    )

    # Add chromatic aberration
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_chromatic_aberration',
            'Chromatic Aberration',
            1,
            default_value=[1.0],
            min=0.0,
            max=2.0,
            help='Chromatic aberration strength (0 = disabled, 1 = realistic)'
        )
    )

    # Add bokeh blades
    lentil_folder.addParmTemplate(
        hou.IntParmTemplate(
            'lentil_bokeh_blades',
            'Bokeh Blades',
            1,
            default_value=[0],
            min=0,
            max=16,
            help='Number of aperture blades (0-3 = circular, 4+ = polygonal)'
        )
    )

    # Add bokeh rotation
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_bokeh_rotation',
            'Bokeh Rotation',
            1,
            default_value=[0.0],
            min=0.0,
            max=6.283185,  # 2*pi
            help='Aperture blade rotation in radians'
        )
    )

    # Add the folder to the camera
    parm_template_group.append(lentil_folder)
    cam.setParmTemplateGroup(parm_template_group)

    # Set some reasonable defaults
    cam.parm('focal').set(50)  # 50mm focal length in Houdini units
    cam.parm('aperture').set(36)  # Full frame sensor

    # Layout the node
    cam.moveToGoodPosition()

    return cam


def setup_example_scene():
    """
    Create a complete example scene with lentil camera
    """
    # Clear the scene (optional - comment out if you don't want to clear)
    # hou.hipFile.clear(suppress_save_prompt=True)

    # Create lentil camera
    cam = create_lentil_camera('lentil_cam')

    # Position camera
    cam.parm('tx').set(0)
    cam.parm('ty').set(1)
    cam.parm('tz').set(5)

    # Create a test geometry
    obj = hou.node('/obj')

    # Create a sphere
    sphere = obj.createNode('geo', 'sphere_foreground')
    sphere_node = sphere.createNode('sphere')
    sphere_node.setDisplayFlag(True)
    sphere_node.setRenderFlag(True)
    sphere.parm('tx').set(0)
    sphere.parm('ty').set(0)
    sphere.parm('tz').set(0)

    # Create background spheres
    for i in range(3):
        bg_sphere = obj.createNode('geo', f'sphere_bg_{i}')
        sphere_node = bg_sphere.createNode('sphere')
        sphere_node.setDisplayFlag(True)
        sphere_node.setRenderFlag(True)
        bg_sphere.parm('tx').set(-2 + i * 2)
        bg_sphere.parm('ty').set(0)
        bg_sphere.parm('tz').set(-3)
        bg_sphere.parm('scale').set(0.5)

    # Create a light
    light = obj.createNode('hlight', 'key_light')
    light.parm('light_type').set('point')
    light.parm('tx').set(2)
    light.parm('ty').set(3)
    light.parm('tz').set(2)

    # Layout nodes
    obj.layoutChildren()

    # Set the camera as the viewport camera
    scene_viewer = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer)
    if scene_viewer:
        viewport = scene_viewer.curViewport()
        viewport.setCamera(cam)

    print("=" * 60)
    print("Lentil Camera Example Scene Created")
    print("=" * 60)
    print(f"Camera: {cam.path()}")
    print("\nNext steps:")
    print("1. Set up Karma rendering in the camera")
    print("2. Configure lentil parameters in the 'Lentil Lens' folder")
    print("3. Render with Karma to see depth of field and bokeh effects")
    print("\nRecommended settings for visible DOF:")
    print("  - F-Stop: 2.8 or lower")
    print("  - Focus Distance: 5000 (focused on foreground sphere)")
    print("  - Chromatic Aberration: 1.0")
    print("  - Bokeh Blades: 6 (hexagonal)")
    print("=" * 60)

    return cam


if __name__ == '__main__':
    # Run this script in Houdini's Python shell
    camera = setup_example_scene()
