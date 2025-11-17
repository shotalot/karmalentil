#!/usr/bin/env python
"""
Setup Lentil Camera in LOPs/Solaris for Karma
Complete LOP-based workflow for Karma rendering
"""

import hou


def create_lentil_lop_network(name='lentil_stage'):
    """
    Create a complete LOP network with lentil camera for Karma

    Args:
        name: Name for the LOP network

    Returns:
        Tuple of (lop_network, camera_node)
    """
    print("=" * 70)
    print("Creating Lentil Camera in LOPs/Solaris")
    print("=" * 70)
    print()

    # Create LOP network at stage level
    stage = hou.node('/stage')
    if not stage:
        stage = hou.node('/').createNode('stage')

    # Create LOP network
    lop_network = stage.createNode('lopnet', name)

    # Create nodes inside LOP network
    # 1. Camera
    camera = lop_network.createNode('camera', 'lentil_camera')

    # Set camera parameters for lentil
    camera.parm('resx').set(1920)
    camera.parm('resy').set(1080)
    camera.parm('focal').set(50.0)  # 50mm
    camera.parm('aperture').set(41.4214)  # Full frame horizontal aperture
    camera.parm('focus').set(5.0)  # 5 meters focus distance
    camera.parm('fstop').set(2.8)  # f/2.8

    # Transform
    camera.parm('tx').set(0)
    camera.parm('ty').set(1)
    camera.parm('tz').set(5)

    # 2. Create scene content (example geometry)
    # Sphere 1 (foreground)
    sphere1 = lop_network.createNode('sphere', 'sphere_foreground')
    sphere1.setInput(0, camera)
    sphere1.parm('primpath').set('/geo/sphere_fg')
    sphere1.parm('radius').set(0.5)
    sphere1.parm('tx').set(0)
    sphere1.parm('ty').set(0)
    sphere1.parm('tz').set(0)

    # Sphere 2 (background)
    sphere2 = lop_network.createNode('sphere', 'sphere_background')
    sphere2.setInput(0, sphere1)
    sphere2.parm('primpath').set('/geo/sphere_bg')
    sphere2.parm('radius').set(0.3)
    sphere2.parm('tx').set(0)
    sphere2.parm('ty').set(0)
    sphere2.parm('tz').set(-3)

    # 3. Ground plane
    grid = lop_network.createNode('grid', 'ground')
    grid.setInput(0, sphere2)
    grid.parm('primpath').set('/geo/ground')
    grid.parm('scale').set(10)
    grid.parm('ty').set(-1)

    # 4. Lights
    dome_light = lop_network.createNode('domelight', 'dome_light')
    dome_light.setInput(0, grid)
    dome_light.parm('primpath').set('/lights/dome')
    dome_light.parm('intensity').set(1.0)

    # 5. Karma render settings
    render_settings = lop_network.createNode('karmarenderproperties', 'karma_settings')
    render_settings.setInput(0, dome_light)

    # Configure Karma settings
    render_settings.parm('camera').set('/cameras/lentil_camera')
    render_settings.parm('res_overrideres').set(1)
    render_settings.parm('res_resx').set(1920)
    render_settings.parm('res_resy').set(1080)

    # Sampling
    render_settings.parm('pixelsamples').set(1024)  # 32x32 for smooth bokeh

    # 6. Configure Karma LOP
    karma_node = lop_network.createNode('karma', 'render')
    karma_node.setInput(0, render_settings)

    # Set render camera
    karma_node.parm('camera').set('/cameras/lentil_camera')

    # Output
    karma_node.parm('picture').set('$HIP/render/$HIPNAME.$F4.exr')

    # 7. Set display flags
    karma_node.setDisplayFlag(True)
    karma_node.setRenderFlag(True)

    # Layout
    lop_network.layoutChildren()

    print(f"✓ Created LOP network: {lop_network.path()}")
    print(f"✓ Camera: /cameras/lentil_camera")
    print(f"✓ Karma render node: {karma_node.path()}")
    print()

    # Configure viewport
    try:
        desktop = hou.ui.curDesktop()
        scene_viewer = desktop.paneTabOfType(hou.paneTabType.SceneViewer)

        if scene_viewer:
            # Set LOP network as current
            scene_viewer.setPwd(lop_network)

            # Set viewport to Karma
            viewport = scene_viewer.curViewport()
            viewport.settings().setDisplayMode(hou.displayMode.RenderViewport)

            print("✓ Viewport configured for Karma")
    except Exception as e:
        print(f"⚠ Could not configure viewport: {e}")

    print()
    print("=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. The viewport should now show Karma rendering")
    print("2. Select the camera node to adjust lentil parameters")
    print("3. Add lentil parameters to camera (see below)")
    print()
    print("To add lentil parameters:")
    print("  - Select the camera node in LOPs")
    print("  - Add spare parameters for:")
    print("    - enable_lentil (toggle)")
    print("    - lens_model (string)")
    print("    - lentil_focal_length (float)")
    print("    - lentil_fstop (float)")
    print("    - lentil_focus_distance (float)")
    print("    - chromatic_aberration (float)")
    print("    - bokeh_blades (int)")
    print()

    return lop_network, camera


def add_lentil_parameters_to_camera(camera_node):
    """
    Add lentil-specific parameters to a LOP camera

    Args:
        camera_node: Camera LOP node
    """
    print("Adding lentil parameters to camera...")

    parm_template_group = camera_node.parmTemplateGroup()

    # Create lentil folder
    lentil_folder = hou.FolderParmTemplate('lentil_folder', 'Lentil Lens')

    # Enable toggle
    lentil_folder.addParmTemplate(
        hou.ToggleParmTemplate(
            'enable_lentil',
            'Enable Lentil',
            default_value=True
        )
    )

    # Lens model
    lentil_folder.addParmTemplate(
        hou.StringParmTemplate(
            'lens_model',
            'Lens Model',
            1,
            default_value=['double_gauss_50mm']
        )
    )

    # Focal length (mm)
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_focal_length',
            'Focal Length (mm)',
            1,
            default_value=[50.0],
            min=1.0,
            max=500.0
        )
    )

    # F-stop
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_fstop',
            'F-Stop',
            1,
            default_value=[2.8],
            min=0.0,
            max=64.0
        )
    )

    # Focus distance (mm)
    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'lentil_focus_distance',
            'Focus Distance (mm)',
            1,
            default_value=[5000.0],
            min=0.1
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
            max=100.0
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
            max=2.0
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
            max=16
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
            max=360.0
        )
    )

    # Bidirectional
    lentil_folder.addParmTemplate(
        hou.ToggleParmTemplate(
            'enable_bidirectional',
            'Enable Bidirectional',
            default_value=True
        )
    )

    lentil_folder.addParmTemplate(
        hou.FloatParmTemplate(
            'bokeh_intensity',
            'Bokeh Intensity',
            1,
            default_value=[1.0],
            min=0.0,
            max=3.0
        )
    )

    parm_template_group.append(lentil_folder)
    camera_node.setParmTemplateGroup(parm_template_group)

    print(f"✓ Added lentil parameters to {camera_node.path()}")


def main():
    """
    Main setup function
    """
    # Create LOP network with camera
    lop_network, camera = create_lentil_lop_network()

    # Add lentil parameters
    add_lentil_parameters_to_camera(camera)

    print()
    print("=" * 70)
    print("LENTIL IN LOPS - READY!")
    print("=" * 70)
    print()
    print(f"LOP Network: {lop_network.path()}")
    print(f"Camera: {camera.path()}")
    print()
    print("The viewport should now show Karma rendering.")
    print("Adjust lentil parameters in the camera's 'Lentil Lens' tab.")
    print()

    return lop_network, camera


if __name__ == '__main__':
    main()
