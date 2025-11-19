"""
Houdini Shelf Tools for POTK Lens Shaders

These functions can be added as shelf tools in Houdini for quick access.

To add to shelf:
1. Right-click shelf → New Tool
2. Copy function code into Script tab
3. Set icon and label
4. Save
"""

import hou

def apply_lens_to_camera():
    """
    Apply POTK lens shader to selected camera

    Shelf Tool: "Apply POTK Lens"
    Icon: NETWORKS_camera
    """
    # Get selected node
    selected = hou.selectedNodes()

    if not selected:
        hou.ui.displayMessage("Please select a camera node")
        return

    cam = selected[0]

    # Verify it's a camera
    if cam.type().name() != 'cam':
        hou.ui.displayMessage(f"Selected node is not a camera: {cam.type().name()}")
        return

    # Get available lens shaders
    import os
    vex_path = os.environ.get('HOUDINI_VEX_PATH', '').split(';')[0]

    if not vex_path or not os.path.exists(vex_path):
        hou.ui.displayMessage(
            "HOUDINI_VEX_PATH not set or directory not found.\n\n"
            "Please set it in houdini.env:\n"
            "HOUDINI_VEX_PATH = \"/path/to/karmalentil/vex/generated;&\""
        )
        return

    # List available shaders
    try:
        shaders = [f.replace('.vfl', '') for f in os.listdir(vex_path)
                  if f.endswith('.vfl')]
    except:
        shaders = []

    if not shaders:
        hou.ui.displayMessage(
            f"No VEX shaders found in:\n{vex_path}\n\n"
            "Generate shaders first using:\n"
            "python3 tools/generate_vex.py"
        )
        return

    # Let user choose shader
    choice = hou.ui.selectFromList(
        shaders,
        title="Select Lens Shader",
        message="Choose a POTK lens shader to apply:",
        column_header="Available Lenses",
        num_visible_rows=10
    )

    if not choice:
        return  # User canceled

    shader_name = shaders[choice[0]]

    # Apply shader to camera
    try:
        # Try different parameter names (varies by Houdini version)
        if cam.parm('vm_lensshader'):
            cam.parm('vm_lensshader').set(shader_name)
        elif cam.parm('lensshader'):
            cam.parm('lensshader').set(shader_name)
        else:
            # Create custom parameter if needed
            ptg = cam.parmTemplateGroup()
            folder = ptg.findFolder("Rendering")
            if folder:
                pt = hou.StringParmTemplate(
                    'potk_lensshader', 'POTK Lens Shader', 1,
                    string_type=hou.stringParmType.Regular
                )
                ptg.appendToFolder(folder, pt)
                cam.setParmTemplateGroup(ptg)
                cam.parm('potk_lensshader').set(shader_name)

        hou.ui.displayMessage(
            f"✓ Applied lens shader to camera\n\n"
            f"Camera: {cam.path()}\n"
            f"Shader: {shader_name}\n\n"
            f"Render with Karma to see lens effects."
        )

    except Exception as e:
        hou.ui.displayMessage(
            f"Error applying shader:\n{str(e)}\n\n"
            f"Try setting manually:\n"
            f"Camera → Rendering → Lens Shader → {shader_name}"
        )


def create_lens_camera():
    """
    Create new camera with POTK lens shader

    Shelf Tool: "Create Lens Camera"
    Icon: SOP_camera
    """
    # Get parameters from user
    result = hou.ui.readMultiInput(
        message="Create POTK Lens Camera",
        input_labels=["Camera Name", "Lens Shader Name", "Focal Length (mm)", "F-Stop"],
        initial_contents=["lens_cam1", "test_simple", "50", "2.0"],
        title="POTK Lens Camera"
    )

    if result[0] == 0:  # OK clicked
        cam_name, shader_name, focal, fstop = result[1]

        try:
            focal = float(focal)
            fstop = float(fstop)
        except:
            hou.ui.displayMessage("Focal length and F-Stop must be numbers")
            return

        # Create camera
        obj = hou.node('/obj')
        cam = obj.createNode('cam', cam_name)

        # Set parameters
        cam.parmTuple('res').set((1920, 1080))
        cam.parm('focal').set(focal)
        cam.parm('fstop').set(fstop)
        cam.parm('focus').set(5.0)

        # Apply lens shader
        try:
            if cam.parm('vm_lensshader'):
                cam.parm('vm_lensshader').set(shader_name)
            elif cam.parm('lensshader'):
                cam.parm('lensshader').set(shader_name)
        except:
            pass

        # Frame in network view
        cam.setSelected(True, clear_all_selected=True)

        hou.ui.displayMessage(
            f"✓ Created POTK lens camera\n\n"
            f"Path: {cam.path()}\n"
            f"Lens: {shader_name}\n"
            f"Focal Length: {focal}mm\n"
            f"F-Stop: f/{fstop}"
        )


def generate_lens_from_patent():
    """
    Generate new lens shader from patent database

    Shelf Tool: "Generate Lens Shader"
    Icon: ROP_geometry
    """
    # This would integrate with the POTK Python tools
    # For now, show instructions

    message = """
To generate a new lens shader:

1. Prepare lens data:
   - Import from patent database
   - Or create custom lens JSON

2. Run POTK fitting:
   cd /path/to/karmalentil
   python3 tools/fit_lens.py lens_data.json --degree 5

3. Generate VEX shader:
   python3 tools/generate_vex.py lens_name

4. Refresh shelf tool to see new shader

See HOUDINI_INTEGRATION_GUIDE.md for details.
"""

    hou.ui.displayMessage(message, title="Generate Lens Shader")


def list_available_lenses():
    """
    Show list of available POTK lens shaders

    Shelf Tool: "List POTK Lenses"
    Icon: COMMON_list
    """
    import os
    import json
    from pathlib import Path

    # Try to find karmalentil directory
    vex_path = os.environ.get('HOUDINI_VEX_PATH', '').split(';')[0]

    if not vex_path:
        hou.ui.displayMessage(
            "HOUDINI_VEX_PATH not set.\n\n"
            "Set it in houdini.env to use POTK lenses."
        )
        return

    # List VEX shaders
    try:
        shaders = [f for f in os.listdir(vex_path) if f.endswith('.vfl')]
    except:
        shaders = []

    if not shaders:
        hou.ui.displayMessage(f"No lenses found in:\n{vex_path}")
        return

    # Build list with details
    lens_info = []
    for shader in shaders:
        shader_path = os.path.join(vex_path, shader)

        # Try to extract info from VEX file
        focal_length = "Unknown"
        fstop = "Unknown"
        degree = "Unknown"

        try:
            with open(shader_path, 'r') as f:
                content = f.read(500)  # Read first 500 chars
                for line in content.split('\n'):
                    if 'Focal length:' in line:
                        focal_length = line.split(':')[1].strip()
                    elif 'Max f-stop:' in line:
                        fstop = line.split(':')[1].strip()
                    elif 'Polynomial degree:' in line:
                        degree = line.split(':')[1].strip()
        except:
            pass

        lens_info.append(
            f"{shader.replace('.vfl', '')}\n"
            f"  Focal: {focal_length}, F-stop: {fstop}, Degree: {degree}"
        )

    message = "Available POTK Lens Shaders:\n\n" + "\n\n".join(lens_info)

    hou.ui.displayMessage(message, title=f"POTK Lenses ({len(shaders)} found)")


# Example: Add to shelf
def add_to_shelf():
    """
    Example of how to programmatically add tools to shelf
    Run this once to set up the POTK shelf
    """
    # Get or create POTK shelf
    shelves = hou.shelves.shelves()

    potk_shelf = None
    for shelf_name, shelf in shelves.items():
        if shelf.label() == "POTK":
            potk_shelf = shelf
            break

    if not potk_shelf:
        # Create new shelf
        potk_shelf = hou.shelves.newShelf(
            file_path=hou.homeHoudiniDirectory() + "/toolbar/potk.shelf",
            name="potk",
            label="POTK"
        )

    # Add tools
    tools = [
        {
            'name': 'apply_lens',
            'label': 'Apply Lens',
            'script': inspect.getsource(apply_lens_to_camera),
            'icon': 'NETWORKS_camera'
        },
        {
            'name': 'create_lens_camera',
            'label': 'Lens Camera',
            'script': inspect.getsource(create_lens_camera),
            'icon': 'SOP_camera'
        },
        {
            'name': 'list_lenses',
            'label': 'List Lenses',
            'script': inspect.getsource(list_available_lenses),
            'icon': 'COMMON_list'
        }
    ]

    for tool_def in tools:
        tool = hou.shelves.newTool(
            file_path=potk_shelf.filePath(),
            name=tool_def['name'],
            label=tool_def['label'],
            script=tool_def['script']
        )
        tool.setIcon(tool_def['icon'])
        potk_shelf.setTools(potk_shelf.tools() + (tool,))

    print("✓ POTK shelf tools installed")
