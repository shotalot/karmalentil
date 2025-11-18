"""
Debug script to check camera parameter structure

Run this in Houdini Python Shell to see what folders exist on a camera node:

1. Create a camera LOP node
2. Select it
3. Run this script

It will show all parameter folders before and after lentil parameters are added.
"""

import hou

# Get selected node
node = hou.selectedNodes()[0]

if node.type().name() != 'camera':
    print("ERROR: Selected node is not a camera")
    print(f"Selected: {node.type().name()}")
else:
    print("=" * 70)
    print("Camera Parameter Structure Analysis")
    print("=" * 70)

    # Get parameter template group
    ptg = node.parmTemplateGroup()

    print(f"\nCamera node: {node.path()}")
    print(f"Type: {node.type().name()}")

    # List all top-level entries
    print(f"\nTotal entries: {len(ptg.entries())}")
    print("\nAll parameter folders:")

    for i, pt in enumerate(ptg.entries()):
        if isinstance(pt, hou.FolderParmTemplate):
            print(f"  [{i}] FOLDER: '{pt.name()}' - Label: '{pt.label()}' - Type: {pt.folderType()}")
        else:
            print(f"  [{i}] PARAM: '{pt.name()}' - Label: '{pt.label()}'")

    # Check for specific folders
    print("\nLooking for specific folders:")

    for folder_name in ['karma', 'Karma', 'lentil_folder', 'xformOp', 'xform']:
        if ptg.find(folder_name):
            print(f"  ✓ Found: '{folder_name}'")
        else:
            print(f"  ✗ Not found: '{folder_name}'")

    # Check if lentil parameters exist
    print("\nLentil parameters:")
    if ptg.find('enable_lentil'):
        print("  ✓ Lentil parameters are present")
    else:
        print("  ✗ Lentil parameters NOT found")

    print("\n" + "=" * 70)
