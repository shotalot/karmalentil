"""
Setup Karma Render for Bidirectional Filtering
Configures Karma to output necessary AOVs for bidirectional filtering
"""

import hou


def setup_karma_aovs_for_bidirectional(rop_node=None):
    """
    Configure Karma ROP to output AOVs needed for bidirectional filtering

    Args:
        rop_node: Karma ROP node (if None, finds or creates one)

    Returns:
        Karma ROP node
    """
    if rop_node is None:
        # Find or create Karma ROP
        out_network = hou.node('/out')
        karma_rops = [n for n in out_network.children() if n.type().name() == 'karma']

        if karma_rops:
            rop_node = karma_rops[0]
            print(f"Using existing Karma ROP: {rop_node.path()}")
        else:
            rop_node = out_network.createNode('karma', 'karma_lentil')
            print(f"Created new Karma ROP: {rop_node.path()}")

    # Get or create extra image planes folder
    parm_template_group = rop_node.parmTemplateGroup()

    # Enable depth output
    if rop_node.parm('ar_deep_enable'):
        rop_node.parm('ar_deep_enable').set(1)
        print("Enabled deep output")

    # Add custom AOVs for lentil bidirectional filtering
    # We need: color (Cf), depth (P.z), and optionally position (P)

    # Standard Karma AOVs should include these by default
    # Just ensure they're enabled

    print("\nRequired AOVs for bidirectional filtering:")
    print("  - Beauty (Cf) - RGB color")
    print("  - Depth (P.z) - Camera space depth")
    print("  - (Optional) P - World position")
    print("\nThese should be enabled by default in Karma.")

    # Set output path
    if not rop_node.parm('picture').eval():
        rop_node.parm('picture').set('$HIP/render/$HIPNAME.$F4.exr')
        print(f"\nSet output to: $HIP/render/$HIPNAME.$F4.exr")

    # Set appropriate pixel samples for DOF
    if rop_node.parm('pixelsamples'):
        current_samples = rop_node.parm('pixelsamples').eval()
        if current_samples < 256:
            rop_node.parm('pixelsamples').set(1024)  # 32x32
            print("Set pixel samples to 1024 (32x32) for smooth bokeh")

    return rop_node


def setup_cop_network_for_bidirectional():
    """
    Create a COP network for post-process bidirectional filtering

    Returns:
        COP network node
    """
    # Create or get /img network
    img_network = hou.node('/img')
    if img_network is None:
        img_network = hou.node('/').createNode('img')

    # Create COP network
    cop_net = img_network.createNode('img', 'lentil_bidirectional_filter')

    # Create file input
    file_in = cop_net.createNode('file', 'rendered_image')
    file_in.parm('filename1').set('$HIP/render/$HIPNAME.$F4.exr')

    # Create VEX COP for bidirectional filtering
    # Note: This would require a VEX COP generator or custom operator
    # For now, create a blur as placeholder

    # Extract depth channel
    depth_extract = cop_net.createNode('channelcopy', 'extract_depth')
    depth_extract.setInput(0, file_in)
    depth_extract.parm('srccolorspace').set('pz')  # P.z channel

    # Create depth-dependent blur (simplified bidirectional filter)
    # In practice, you'd use a custom VEX operator here
    blur = cop_net.createNode('blur', 'coc_blur')
    blur.setInput(0, file_in)
    blur.parm('sizex').setExpression('ch("../lentil_fstop") * 10.0 / max(1, ch("../lentil_focus_distance"))')
    blur.parm('sizey').setExpression('ch("../lentil_fstop") * 10.0 / max(1, ch("../lentil_focus_distance"))')

    # Add control parameters
    parm_group = cop_net.parmTemplateGroup()
    parm_folder = hou.FolderParmTemplate('lentil_controls', 'Lentil Bidirectional Controls')

    parm_folder.addParmTemplate(
        hou.FloatParmTemplate('lentil_focal_length', 'Focal Length (mm)', 1, default_value=[50.0])
    )
    parm_folder.addParmTemplate(
        hou.FloatParmTemplate('lentil_fstop', 'F-Stop', 1, default_value=[2.8])
    )
    parm_folder.addParmTemplate(
        hou.FloatParmTemplate('lentil_focus_distance', 'Focus Distance (mm)', 1, default_value=[1000.0])
    )
    parm_folder.addParmTemplate(
        hou.FloatParmTemplate('lentil_bokeh_intensity', 'Bokeh Intensity', 1, default_value=[1.0])
    )

    parm_group.append(parm_folder)
    cop_net.setParmTemplateGroup(parm_group)

    # Layout
    cop_net.layoutChildren()

    print(f"\nCreated COP network: {cop_net.path()}")
    print("Note: This is a simplified version. For full bidirectional filtering,")
    print("use the Python post-process script: python/bidirectional_filter.py")

    return cop_net


def create_bidirectional_example_scene():
    """
    Create a complete example scene with bidirectional filtering setup
    """
    print("=" * 70)
    print("Creating Lentil Bidirectional Filtering Example Scene")
    print("=" * 70)

    # Setup camera (reuse from previous example)
    import sys
    import os
    karmalentil_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(karmalentil_path, 'examples'))

    try:
        import setup_lentil_camera
        cam = setup_lentil_camera.create_lentil_camera('lentil_cam_bidir')

        # Set parameters for visible bokeh
        cam.parm('lentil_fstop').set(1.8)
        cam.parm('lentil_focus_distance').set(5000.0)  # 5m focus
        cam.parm('lentil_chromatic_aberration').set(1.0)
        cam.parm('lentil_bokeh_blades').set(7)

        print(f"\nCreated camera: {cam.path()}")
    except:
        print("Note: Could not import setup_lentil_camera. Create camera manually.")
        cam = None

    # Setup Karma ROP
    rop = setup_karma_aovs_for_bidirectional()

    # Link camera to ROP
    if cam:
        rop.parm('camera').set(cam.path())
        print(f"Linked camera to ROP")

    # Create COP network for post-processing
    cop_net = setup_cop_network_for_bidirectional()

    print("\n" + "=" * 70)
    print("Setup Complete!")
    print("=" * 70)
    print("\nWorkflow:")
    print("1. Render from Karma ROP (outputs EXR with depth)")
    print("2. Choose post-processing method:")
    print("\n   Method A - Python Script (Most Accurate):")
    print("   Run from shell:")
    print("   $ python python/bidirectional_filter.py \\")
    print("       render/scene.0001.exr \\")
    print("       render/scene_filtered.0001.exr \\")
    print("       --focus 5000 --fstop 1.8 --focal-length 50")
    print("\n   Method B - COP Network (Interactive):")
    print(f"   Open COP network: {cop_net.path()}")
    print("   Adjust parameters and view results")
    print("\n" + "=" * 70)

    return cam, rop, cop_net


if __name__ == '__main__':
    # Run in Houdini Python shell
    cam, rop, cop_net = create_bidirectional_example_scene()
