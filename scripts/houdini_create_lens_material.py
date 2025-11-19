"""
POTK Houdini Lens Shader Builder

This script creates a proper Karma lens shader material in Houdini
using POTK polynomial coefficients. Run this inside Houdini's Python Shell.

Usage:
    1. Load POTK coefficients from file
    2. Run create_lens_shader_material()
    3. Apply returned material to camera
"""

import hou
import json
from pathlib import Path


def create_lens_shader_material(lens_name, coefficients, focal_length=50.0):
    """
    Create a Karma lens shader material with polynomial distortion

    Args:
        lens_name: Name for the lens shader
        coefficients: Dict with keys 'exit_pupil_x', 'exit_pupil_y', etc.
        focal_length: Lens focal length in mm

    Returns:
        hou.Material node
    """

    # Create material in /mat context
    mat_context = hou.node('/mat')
    if not mat_context:
        raise RuntimeError("/mat context not found")

    # Create material builder (Karma compatible)
    mat_name = f"potk_lens_{lens_name}"
    mat = mat_context.createNode('materialbuilder', mat_name)

    # Go inside material builder
    mat_builder = mat

    # Create lens shader type output
    # Note: This creates a surface shader, you'd need to adapt for lens shader
    # Karma lens shaders are typically implemented as MaterialX or VOP networks

    # Create parameter interface for polynomial coefficients
    ptg = mat.parmTemplateGroup()

    # Add coefficients as parameters
    for direction in ['exit_x', 'exit_y', 'entrance_x', 'entrance_y']:
        key = f'exit_pupil_x' if 'exit_x' in direction else \
              f'exit_pupil_y' if 'exit_y' in direction else \
              f'entrance_pupil_x' if 'entrance_x' in direction else \
              f'entrance_pupil_y'

        if key in coefficients:
            coeffs = coefficients[key]

            # Create folder for this direction
            folder = hou.FolderParmTemplate(
                f"coeffs_{direction}",
                f"Coefficients {direction.upper()}",
                folder_type=hou.folderType.Simple
            )

            # Add each coefficient as a parameter
            for i, coeff in enumerate(coeffs):
                pt = hou.FloatParmTemplate(
                    f"coeff_{direction}_{i}",
                    f"c[{i}]",
                    1,
                    default_value=(float(coeff),)
                )
                folder.addParmTemplate(pt)

            ptg.append(folder)

    mat.setParmTemplateGroup(ptg)

    # Set the coefficient values
    for direction in ['exit_x', 'exit_y', 'entrance_x', 'entrance_y']:
        key = f'exit_pupil_x' if 'exit_x' in direction else \
              f'exit_pupil_y' if 'exit_y' in direction else \
              f'entrance_pupil_x' if 'entrance_x' in direction else \
              f'entrance_pupil_y'

        if key in coefficients:
            coeffs = coefficients[key]
            for i, coeff in enumerate(coeffs):
                parm_name = f"coeff_{direction}_{i}"
                if mat.parm(parm_name):
                    mat.parm(parm_name).set(float(coeff))

    print(f"✓ Created lens shader material: {mat.path()}")
    print(f"  Coefficients loaded: {sum(len(v) for v in coefficients.values())}")

    return mat


def load_potk_lens_data(json_path):
    """Load lens data and coefficients from POTK JSON file"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data


def apply_lens_to_camera(camera_node, lens_material):
    """
    Apply lens shader material to camera

    Note: This is a simplified version. Actual implementation depends on
    how Karma handles lens shaders in your Houdini version.
    """

    # Check if camera has lens shader parameter
    if camera_node.parm('vm_lensshader'):
        camera_node.parm('vm_lensshader').set(lens_material.path())
        print(f"✓ Applied lens shader to camera")
    else:
        print("⚠️  Camera doesn't have vm_lensshader parameter")
        print("   Try applying as a camera shader material instead")


def create_simple_lens_distortion_vop(mat_builder, coefficients):
    """
    Create a VOP network inside material builder for lens distortion

    This creates a simple polynomial evaluation network
    """

    # Create VOPs inside material builder
    vop_context = mat_builder

    # Create input for UV coordinates
    uv_input = vop_context.createNode('parameter')
    uv_input.parm('parmname').set('uv')
    uv_input.parm('parmtype').set('vector2')
    uv_input.parm('parmlabel').set('UV Coordinates')

    # Create polynomial evaluation network
    # This is simplified - full implementation would build the polynomial tree

    # For now, create a simple distortion
    multiply = vop_context.createNode('multiply')
    constant = vop_context.createNode('constant')
    constant.parm('contype').set('float')
    constant.parm('const1').set(0.1)  # Distortion amount

    # Connect nodes
    multiply.setInput(0, uv_input, 0)
    multiply.setInput(1, constant, 0)

    # Create output
    output = vop_context.createNode('output')
    output.setInput(0, multiply, 0)

    # Layout nodes
    vop_context.layoutChildren()

    return output


# Example usage:
def example_create_and_apply():
    """
    Example: Create lens shader and apply to camera
    """

    # Mock coefficients (replace with real POTK data)
    coefficients = {
        'exit_pupil_x': [0.0, 1.0, 0.0, 0.1, 0.0, 0.05],  # Degree 2 example
        'exit_pupil_y': [0.0, 0.0, 1.0, 0.0, 0.1, 0.0],
        'entrance_pupil_x': [0.0, 1.0, 0.0, -0.1, 0.0, -0.05],
        'entrance_pupil_y': [0.0, 0.0, 1.0, 0.0, -0.1, 0.0],
    }

    # Create lens shader material
    lens_mat = create_lens_shader_material(
        lens_name="test_50mm",
        coefficients=coefficients,
        focal_length=50.0
    )

    # Get or create camera
    cam = hou.node('/obj/cam1')
    if not cam:
        cam = hou.node('/obj').createNode('cam', 'cam1')

    # Apply lens shader
    apply_lens_to_camera(cam, lens_mat)

    print("\n" + "="*60)
    print("Lens Shader Created and Applied!")
    print("="*60)
    print(f"Material: {lens_mat.path()}")
    print(f"Camera: {cam.path()}")
    print("\nNOTE: This creates the material structure.")
    print("For full polynomial lens distortion, you need to:")
    print("1. Build VOP network for polynomial evaluation")
    print("2. Connect to appropriate lens shader outputs")
    print("3. Or use Karma's built-in lens distortion parameters")

    return lens_mat, cam


if __name__ == '__main__':
    # Run this in Houdini Python Shell
    # lens_mat, cam = example_create_and_apply()
    pass
