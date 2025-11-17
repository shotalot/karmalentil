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

        # TESTING: Skip all metadata to see if that's the issue
        # Just use the HDA as-is from createDigitalAsset()
        print("Skipping metadata modifications for debugging...")
        print()

        # DON'T modify, save, or reload - just use what createDigitalAsset() created
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

        # CRITICAL TEST: Try creating an instance HERE in the builder
        print("Testing instance creation inside builder...")
        try:
            test_lop = stage.createNode('lopnet', 'test_instance')
            test_camera = test_lop.createNode('karmalentil::camera::1.0', 'test')
            print(f"  ✓ SUCCESS: Created test instance: {test_camera.path()}")
            print(f"  ✓ Test instance type: {test_camera.type().name()}")
            # Clean up test
            test_lop.destroy()
        except Exception as e:
            print(f"  ✗ FAILED to create instance: {e}")
            import traceback
            traceback.print_exc()
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
