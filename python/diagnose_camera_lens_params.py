"""
Diagnostic script to find lens shader parameters on LOP camera nodes
Run this in Houdini's Python shell
"""

import hou

# Create a test camera to inspect its parameters
stage = hou.node('/stage') or hou.node('/').createNode('stage')
test_lop = stage.createNode('lopnet', 'test_diagnostic')
test_cam = test_lop.createNode('camera', 'test_camera')

print("=" * 60)
print("LOP Camera Parameters - Looking for Lens Shader Assignment")
print("=" * 60)

# Search for lens-related parameters
all_parms = test_cam.parms()
lens_parms = [p for p in all_parms if any(keyword in p.name().lower() for keyword in ['lens', 'shader', 'karma'])]

if lens_parms:
    print("\nFound lens/shader/karma-related parameters:")
    for p in lens_parms:
        print(f"  - {p.name()}: {p.parmTemplate().type()}")
        print(f"      Label: {p.description()}")
        print(f"      Type: {p.parmTemplate().dataType()}")
        print()
else:
    print("\nNo lens/shader parameters found directly on camera node.")
    print("\nLens shaders might be assigned through:")
    print("  1. Karma Render Properties LOP node")
    print("  2. Material assignment")
    print("  3. Camera-specific USD attributes")

# Check for camera-specific tabs/folders
ptg = test_cam.parmTemplateGroup()
folders = [pt for pt in ptg.entries() if isinstance(pt, hou.FolderParmTemplate)]

print("\nParameter folders on camera:")
for folder in folders:
    print(f"  - {folder.label()} ({folder.name()})")

# Clean up
test_lop.destroy()

print("\n" + "=" * 60)
print("Run this script in Houdini to see camera parameters")
print("=" * 60)
