#!/usr/bin/env python
"""
Complete Lentil Setup Script
Sets up everything needed for KarmaLentil with viewport integration
"""

import hou
import os
import sys


def setup_environment():
    """
    Setup environment variables and paths
    """
    # Get karmalentil root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    karmalentil_root = os.path.dirname(script_dir)

    # Set environment variable
    os.environ['KARMALENTIL'] = karmalentil_root

    # Add to Python path
    if karmalentil_root not in sys.path:
        sys.path.insert(0, karmalentil_root)

    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

    print(f"KarmaLentil root: {karmalentil_root}")

    return karmalentil_root


def initialize_lens_database():
    """
    Initialize and load lens database
    """
    from lens_database import LensDatabase

    db = LensDatabase()

    print(f"\nLoaded {len(db.lenses)} lens models:")
    for lens_name, info in db.lenses.items():
        print(f"  - {info['display_name']}")

    return db


def create_complete_lentil_camera(name='lentil_camera'):
    """
    Create a complete lentil camera with all features

    Args:
        name: Name for the camera node

    Returns:
        Camera node
    """
    print(f"\nCreating lentil camera: {name}")

    # Import HDA creator
    from create_lentil_hda import create_lentil_camera_hda

    # Create camera
    cam = create_lentil_camera_hda()
    cam.setName(name, unique_name=True)

    # Set default parameters for visible bokeh
    if cam.parm('fstop'):
        cam.parm('fstop').set(2.8)
    if cam.parm('focus_distance'):
        cam.parm('focus_distance').set(5000.0)  # 5m
    if cam.parm('bokeh_blades'):
        cam.parm('bokeh_blades').set(7)
    if cam.parm('enable_bidirectional'):
        cam.parm('enable_bidirectional').set(True)

    print(f"  Created: {cam.path()}")
    print(f"  Configured for visible bokeh effects")

    return cam


def setup_karma_rop(cam_node, rop_name='karma_lentil'):
    """
    Setup Karma ROP with lentil filtering

    Args:
        cam_node: Camera node to use
        rop_name: Name for ROP node

    Returns:
        Karma ROP node
    """
    print(f"\nSetting up Karma ROP: {rop_name}")

    from karma_lentil_filter import create_karma_rop_with_lentil_filter

    # Create ROP
    karma_rop = create_karma_rop_with_lentil_filter(rop_name)

    # Link camera
    if karma_rop.parm('camera'):
        karma_rop.parm('camera').set(cam_node.path())

    # Configure settings
    if karma_rop.parm('pixelsamples'):
        karma_rop.parm('pixelsamples').set(1024)  # 32x32

    # Set output path
    if karma_rop.parm('picture'):
        karma_rop.parm('picture').set('$HIP/render/$HIPNAME.$F4.exr')

    print(f"  Created: {karma_rop.path()}")
    print(f"  Linked to camera: {cam_node.path()}")
    print(f"  Pixel samples: 1024 (32x32)")

    return karma_rop


def create_example_scene():
    """
    Create a complete example scene with geometry
    """
    print("\nCreating example scene...")

    obj = hou.node('/obj')

    # Create foreground sphere (in focus)
    fg_sphere = obj.createNode('geo', 'sphere_foreground')
    sphere_node = fg_sphere.createNode('sphere')
    sphere_node.parm('type').set(1)  # Polygon
    sphere_node.parm('scale').set(0.5)
    sphere_node.setDisplayFlag(True)
    sphere_node.setRenderFlag(True)

    fg_sphere.parm('tx').set(0)
    fg_sphere.parm('ty').set(0)
    fg_sphere.parm('tz').set(-5)

    # Create background spheres (out of focus)
    positions = [
        (-2, 0, -8),
        (0, 0, -8),
        (2, 0, -8),
        (-1, 1, -9),
        (1, 1, -9),
    ]

    bg_spheres = []
    for i, (x, y, z) in enumerate(positions):
        bg = obj.createNode('geo', f'sphere_bg_{i}')
        sphere = bg.createNode('sphere')
        sphere.parm('type').set(1)
        sphere.parm('scale').set(0.3)
        sphere.setDisplayFlag(True)
        sphere.setRenderFlag(True)

        bg.parm('tx').set(x)
        bg.parm('ty').set(y)
        bg.parm('tz').set(z)

        bg_spheres.append(bg)

    # Create ground plane
    ground = obj.createNode('geo', 'ground')
    grid_node = ground.createNode('grid')
    grid_node.parm('sizex').set(20)
    grid_node.parm('sizey').set(20)
    grid_node.parm('rows').set(20)
    grid_node.parm('cols').set(20)
    grid_node.setDisplayFlag(True)
    grid_node.setRenderFlag(True)

    ground.parm('ty').set(-1)

    # Create lights
    key_light = obj.createNode('hlight::2.0', 'key_light')
    key_light.parm('light_type').set(2)  # Distant
    key_light.parm('light_intensity').set(1.5)
    key_light.parm('rx').set(-30)
    key_light.parm('ry').set(45)

    fill_light = obj.createNode('hlight::2.0', 'fill_light')
    fill_light.parm('light_type').set(0)  # Point
    fill_light.parm('light_intensity').set(0.5)
    fill_light.parm('tx').set(-3)
    fill_light.parm('ty').set(2)
    fill_light.parm('tz').set(0)

    # Layout
    obj.layoutChildren()

    print("  Created example geometry")
    print(f"    - {len(bg_spheres) + 1} spheres")
    print(f"    - Ground plane")
    print(f"    - 2 lights")

    return fg_sphere, bg_spheres, ground


def configure_viewport(cam_node):
    """
    Configure viewport to use lentil camera

    Args:
        cam_node: Camera to set as active
    """
    print("\nConfiguring viewport...")

    try:
        # Get scene viewer
        desktop = hou.ui.curDesktop()
        scene_viewer = desktop.paneTabOfType(hou.paneTabType.SceneViewer)

        if scene_viewer:
            # Set camera
            viewport = scene_viewer.curViewport()
            viewport.setCamera(cam_node)

            # Set to Karma renderer
            viewport.settings().setDisplayMode(hou.displayMode.RenderViewport)

            print(f"  Viewport camera: {cam_node.path()}")
            print(f"  Display mode: Karma")
        else:
            print("  Warning: No scene viewer found")

    except Exception as e:
        print(f"  Note: Could not configure viewport automatically: {e}")
        print(f"  Please manually set viewport camera to: {cam_node.path()}")


def print_usage_instructions(cam_node, karma_rop):
    """
    Print usage instructions for the user
    """
    print("\n" + "=" * 70)
    print("SETUP COMPLETE!")
    print("=" * 70)

    print(f"\nCamera: {cam_node.path()}")
    print(f"Render Node: {karma_rop.path()}")

    print("\n" + "-" * 70)
    print("NEXT STEPS:")
    print("-" * 70)

    print("\n1. Viewport Preview:")
    print("   - Viewport should now show Karma rendering")
    print("   - Adjust camera parameters in 'Lentil Lens' tab")
    print("   - See real-time lens aberrations and bokeh")

    print("\n2. Adjust Parameters for Visible Bokeh:")
    print("   Navigate to camera parameters:")
    print("   - Lentil Lens → F-Stop: 1.8-2.8 (wide aperture)")
    print("   - Lentil Lens → Focus Distance: 5000mm (5m)")
    print("   - Bokeh → Bokeh Blades: 7 (heptagonal)")
    print("   - Bidirectional → Enable: ON")
    print("   - Bidirectional → Bokeh Intensity: 1.0-1.5")

    print("\n3. Test Render:")
    print(f"   - Open: {karma_rop.path()}")
    print("   - Click 'Render to MPlay' or 'Render to Disk'")
    print("   - Output: $HIP/render/$HIPNAME.$F4.exr")

    print("\n4. Apply Bidirectional Filter (for best quality):")
    print("   After rendering:")
    print("   $ python python/bidirectional_filter.py \\")
    print("       render/scene.0001.exr \\")
    print("       render/scene_filtered.0001.exr \\")
    print("       --focus 5000 --fstop 2.8 --focal-length 50")

    print("\n" + "-" * 70)
    print("FEATURES:")
    print("-" * 70)
    print("  ✓ Polynomial lens aberrations")
    print("  ✓ Chromatic aberration")
    print("  ✓ Customizable bokeh (blades & textures)")
    print("  ✓ Real-time bidirectional filtering")
    print("  ✓ Lens database system")
    print("  ✓ Viewport integration")
    print("  ✓ Full Karma compatibility")

    print("\n" + "-" * 70)
    print("DOCUMENTATION:")
    print("-" * 70)
    print("  - VIEWPORT_INTEGRATION.md - Complete viewport guide")
    print("  - USAGE.md - Parameter reference")
    print("  - BIDIRECTIONAL.md - Bidirectional filtering details")
    print("  - QUICKSTART.md - Quick start guide")

    print("\n" + "=" * 70)


def main():
    """
    Main setup function
    """
    print("=" * 70)
    print("KARMALENTIL COMPLETE SETUP")
    print("Polynomial Optics for Houdini Karma with Viewport Integration")
    print("=" * 70)

    try:
        # Step 1: Setup environment
        karmalentil_root = setup_environment()

        # Step 2: Initialize lens database
        lens_db = initialize_lens_database()

        # Step 3: Create lentil camera
        cam = create_complete_lentil_camera('lentil_cam')

        # Step 4: Setup Karma ROP
        karma_rop = setup_karma_rop(cam, 'karma_lentil')

        # Step 5: Create example scene
        fg_sphere, bg_spheres, ground = create_example_scene()

        # Step 6: Configure viewport
        configure_viewport(cam)

        # Step 7: Print instructions
        print_usage_instructions(cam, karma_rop)

        return cam, karma_rop

    except Exception as e:
        print(f"\n ERROR: Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == '__main__':
    # Run complete setup
    cam, rop = main()
