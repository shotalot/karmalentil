#!/usr/bin/env python
"""
Create Lentil Camera HDA for LOPs
This creates a complete camera HDA with all lentil parameters built-in
"""

import hou
import os


def create_lentil_camera_hda():
    """
    Create a LOP-level camera HDA with lentil parameters

    Returns:
        HDA definition
    """
    print("=" * 70)
    print("CREATING LENTIL CAMERA HDA")
    print("=" * 70)
    print()

    # Get karmalentil path
    karmalentil_path = hou.getenv("KARMALENTIL") or hou.getenv("KARMALENTIL_PATH")
    if not karmalentil_path:
        print("ERROR: KARMALENTIL path not set!")
        return None

    # OTL save path
    otls_dir = os.path.join(karmalentil_path, "otls")
    os.makedirs(otls_dir, exist_ok=True)
    hda_path = os.path.join(otls_dir, "karmalentil_camera.hda")

    print(f"HDA will be saved to: {hda_path}")
    print()

    # Create a temporary LOP network to build the HDA
    stage = hou.node('/stage')
    if not stage:
        stage = hou.node('/').createNode('stage')

    temp_lop = stage.createNode('lopnet', 'temp_lentil_builder')

    # Create a subnet to contain the camera (required for HDA)
    print("Creating subnet container...")
    subnet = temp_lop.createNode('subnet', 'lentil_camera_subnet')

    if not subnet:
        print("ERROR: Failed to create subnet!")
        temp_lop.destroy()
        return None

    # Create the camera node inside the subnet
    print("Creating camera LOP node...")
    camera = subnet.createNode('camera', 'lentil_camera_internal')

    if not camera:
        print("ERROR: Failed to create camera node!")
        temp_lop.destroy()
        return None

    print(f"✓ Camera node created: {camera.path()}")

    # Create output node in subnet
    output = subnet.createNode('output', 'output0')
    output.setInput(0, camera)
    output.setDisplayFlag(True)
    # Note: LOPs don't have render flags, only display flags

    # Layout subnet contents
    subnet.layoutChildren()

    print(f"✓ Subnet created: {subnet.path()}")

    # Add parameters to the subnet BEFORE creating HDA
    # This way they get baked into the HDA definition file
    print("Adding lentil parameters to subnet...")

    # Get the subnet's parameter template group
    parm_template_group = subnet.parmTemplateGroup()

    # Create Lentil Lens folder
    lentil_folder = hou.FolderParmTemplate('lentil_folder', 'Lentil Lens')

    # Enable toggle
    lentil_folder.addParmTemplate(
        hou.ToggleParmTemplate(
            'enable_lentil',
            'Enable Lentil',
            default_value=True,
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

    # Add folder to subnet's parameter template group
    parm_template_group.append(lentil_folder)

    # Apply parameters to the subnet (BEFORE creating HDA)
    subnet.setParmTemplateGroup(parm_template_group)

    print("✓ Added lentil parameters to subnet")
    print()

    # NOW create the HDA from the subnet with parameters
    print("Converting subnet to HDA...")

    # Select the subnet node
    subnet.setSelected(True, clear_all_selected=True)

    # Create HDA definition
    hda_node_type_name = "karmalentil::camera::1.0"
    hda_label = "KarmaLentil Camera"

    try:
        # Create the HDA from the subnet (parameters should be captured)
        hda_node = subnet.createDigitalAsset(
            name=hda_node_type_name,
            hda_file_name=hda_path,
            description=hda_label,
            min_num_inputs=0,
            max_num_inputs=1
        )

        print(f"✓ Created HDA: {hda_node_type_name}")
        print(f"✓ Saved to: {hda_path}")
        print()

        # DIAGNOSTIC: Check what was actually created
        print("Diagnostics:")
        print(f"  Created node: {hda_node}")
        print(f"  Type: {hda_node.type()}")
        print(f"  Type name: {hda_node.type().name()}")
        print(f"  Category: {hda_node.type().category().name()}")
        print()

        # Get the HDA definition
        hda_definition = hda_node.type().definition()
        print(f"HDA Definition:")
        print(f"  Node type name: {hda_definition.nodeTypeName()}")
        print(f"  Node type category: {hda_definition.nodeTypeCategory().name()}")
        print()

        # Set HDA metadata
        hda_definition.setIcon('NETWORKS_camera')
        hda_definition.setComment('KarmaLentil camera with polynomial optics for realistic lens aberrations')

        # Add help text
        help_text = """= KarmaLentil Camera =

A camera LOP with built-in polynomial optics for realistic lens aberrations.

== Features ==

* Physically-based lens aberration modeling
* Chromatic aberration with RGB wavelength sampling
* Customizable aperture shapes (circular and polygonal)
* Custom aperture textures for unique bokeh
* Bidirectional filtering for realistic bokeh highlights
* Real-time viewport integration with Karma

== Quick Start ==

1. Drop this node into a LOP network
2. Adjust basic camera parameters (position, focal length, f-stop)
3. Configure lentil parameters in the "Lentil Lens" tab
4. Render with Karma!

== Parameters ==

=== Lentil Lens ===

Enable Lentil:
    Toggle lentil polynomial optics on/off

Lens Model:
    Select from available lens models in database

Focal Length:
    Lens focal length in millimeters (e.g., 50mm)

F-Stop:
    Aperture f-stop. Lower values = shallower depth of field
    Typical range: f/1.4 to f/16

Focus Distance:
    Distance to focus plane in millimeters

Sensor Width:
    Camera sensor width in mm (36mm = full-frame)

Chromatic Aberration:
    Color fringing intensity (0=off, 1=normal, >1=exaggerated)

Bokeh Blades:
    Number of aperture blades. 0=circular, 6=hexagonal

Bokeh Rotation:
    Rotate the aperture shape in degrees

Aperture Texture:
    Optional image file for custom bokeh shapes

Enable Bidirectional:
    Enable bidirectional filtering for preserved highlights in bokeh

Bokeh Intensity:
    Intensity multiplier for bokeh highlights (1.0 = normal)

== Rendering ==

For best quality:
* Use Karma XPU (GPU) or CPU renderer
* Set pixel samples to at least 1024 (32x32) for smooth bokeh
* Enable "High Quality Lighting" in viewport for preview

== Support ==

Documentation: $KARMALENTIL/README.md
Original project: https://github.com/zpelgrims/lentil
"""

        hda_definition.addSection('Help', help_text)

        # Save the definition with metadata changes
        hda_definition.save(hda_path)

        print("✓ Added help text and metadata")
        print()

        # CRITICAL: After modifying and saving the definition, we need to reload it
        # The in-memory definition may not match the file on disk
        print("Reloading HDA from disk...")

        # Uninstall the current in-memory version
        if hda_definition.isInstalled():
            hda_definition.uninstall()

        # Reinstall from the file we just saved
        hou.hda.installFile(hda_path)

        print("✓ HDA reloaded from disk")
        print()

        # DON'T destroy temp network yet - it will invalidate the HDA
        # The caller should destroy it AFTER successfully creating an instance

        # DIAGNOSTIC: Verify the node type is actually available
        print("Verifying installation:")
        installed_defs = hou.hda.definitionsInFile(hda_path)
        for d in installed_defs:
            print(f"  Installed definition: {d.nodeTypeName()}")
            print(f"    Category: {d.nodeTypeCategory().name()}")
            print(f"    Is installed: {d.isInstalled()}")
        print()

        # Try to verify the node type exists in LOP category
        print("Checking if node type is available in LOP category:")
        try:
            lop_cat = hou.lopNodeTypeCategory()
            # Try the exact name we used
            node_type = lop_cat.nodeType("karmalentil::camera::1.0")
            if node_type:
                print(f"  ✓ SUCCESS: Node type found: {node_type}")
            else:
                print(f"  ✗ FAILED: nodeType() returned None")
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            # Try listing all available node types with 'karmalentil' in the name
            print("  Searching for any 'karmalentil' node types...")
            all_types = lop_cat.nodeTypes()
            karmalentil_types = [t for t in all_types.keys() if 'karmalentil' in t.lower()]
            if karmalentil_types:
                print(f"  Found: {karmalentil_types}")
            else:
                print(f"  No 'karmalentil' node types found in LOP category")
        print()

        print("=" * 70)
        print("HDA CREATION COMPLETE!")
        print("=" * 70)
        print()
        print(f"HDA Type: {hda_node_type_name}")
        print(f"Location: {hda_path}")
        print()
        print("The HDA is now available in the TAB menu in LOPs:")
        print("  1. Create a LOP network")
        print("  2. Press TAB")
        print("  3. Search for 'karmalentil' or 'lentil camera'")
        print("  4. Drop it in and start using!")
        print()

        # Return the freshly installed definition AND temp network
        # Caller should destroy temp_lop AFTER creating an instance
        installed_defs = hou.hda.definitionsInFile(hda_path)
        if installed_defs:
            return (installed_defs[0], temp_lop)
        return (None, temp_lop)

    except Exception as e:
        print(f"ERROR creating HDA: {e}")
        import traceback
        traceback.print_exc()

        # Clean up on error
        temp_lop.destroy()
        return (None, None)


if __name__ == '__main__':
    create_lentil_camera_hda()
