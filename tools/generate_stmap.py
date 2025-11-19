#!/usr/bin/env python3
"""
POTK ST-Map Generator

Generates lens distortion ST-Maps (UV displacement textures) that can be
used in Houdini Karma, Nuke, or any compositing software.

ST-Maps are the industry-standard way to apply lens distortion.
"""

import numpy as np
from pathlib import Path
import sys

# Try to import OpenImageIO for EXR output
try:
    import OpenImageIO as oiio
    HAS_OIIO = True
except ImportError:
    HAS_OIIO = False
    print("⚠️  OpenImageIO not available, will save as NumPy array")


def evaluate_polynomial_2d(coeffs_x, coeffs_y, x, y, degree=5):
    """
    Evaluate 2D polynomial at given coordinates

    Args:
        coeffs_x: Coefficients for x displacement
        coeffs_y: Coefficients for y displacement
        x, y: Input coordinates (can be arrays)
        degree: Polynomial degree

    Returns:
        (distorted_x, distorted_y)
    """
    result_x = 0.0
    result_y = 0.0
    idx = 0

    # Evaluate polynomial: sum of c_ij * x^i * y^j
    for total_deg in range(degree + 1):
        for i in range(total_deg + 1):
            j = total_deg - i

            x_pow = np.power(x, i)
            y_pow = np.power(y, j)

            result_x += coeffs_x[idx] * x_pow * y_pow
            result_y += coeffs_y[idx] * x_pow * y_pow

            idx += 1

    return result_x, result_y


def generate_lens_stmap(coefficients, resolution=(2048, 2048), degree=5):
    """
    Generate ST-Map for lens distortion

    ST-Map: Each pixel stores the UV coordinates that should be sampled
    from the source image to create the distorted result.

    Args:
        coefficients: Dict with 'exit_pupil_x', 'exit_pupil_y' arrays
        resolution: Output resolution (width, height)
        degree: Polynomial degree

    Returns:
        numpy array of shape (height, width, 2) with UV coordinates
    """
    width, height = resolution

    # Create normalized coordinate grid (0 to 1)
    y_coords, x_coords = np.mgrid[0:height, 0:width]
    x_norm = x_coords.astype(np.float32) / (width - 1)
    y_norm = y_coords.astype(np.float32) / (height - 1)

    # Center coordinates (-0.5 to 0.5 for polynomial evaluation)
    x_centered = x_norm - 0.5
    y_centered = y_norm - 0.5

    # Apply polynomial distortion
    x_distorted, y_distorted = evaluate_polynomial_2d(
        coefficients['exit_pupil_x'],
        coefficients['exit_pupil_y'],
        x_centered,
        y_centered,
        degree=degree
    )

    # Convert back to 0-1 range
    x_distorted = x_distorted + 0.5
    y_distorted = y_distorted + 0.5

    # Clamp to valid range
    x_distorted = np.clip(x_distorted, 0.0, 1.0)
    y_distorted = np.clip(y_distorted, 0.0, 1.0)

    # Create ST-Map (RG channels store UV coordinates)
    stmap = np.zeros((height, width, 3), dtype=np.float32)
    stmap[:, :, 0] = x_distorted  # Red = U
    stmap[:, :, 1] = y_distorted  # Green = V
    stmap[:, :, 2] = 0.0          # Blue = unused

    return stmap


def save_stmap_exr(stmap, output_path):
    """Save ST-Map as EXR file"""
    if not HAS_OIIO:
        print("❌ OpenImageIO not available - cannot save EXR")
        print("   Install with: pip install OpenImageIO")
        return False

    height, width = stmap.shape[:2]

    # Create image spec
    spec = oiio.ImageSpec(width, height, 3, oiio.FLOAT)
    spec.attribute("compression", "zip")

    # Create output
    out = oiio.ImageOutput.create(str(output_path))
    if not out:
        print(f"❌ Could not create {output_path}")
        return False

    # Write image
    out.open(str(output_path), spec)
    out.write_image(stmap)
    out.close()

    return True


def save_stmap_npy(stmap, output_path):
    """Save ST-Map as NumPy array"""
    np.save(output_path, stmap)
    return True


def visualize_stmap(stmap, output_path=None):
    """
    Create visualization of ST-Map distortion
    Shows the distortion as a color-coded displacement field
    """
    height, width = stmap.shape[:2]

    # Create undistorted grid
    y_coords, x_coords = np.mgrid[0:height, 0:width]
    x_undistorted = x_coords.astype(np.float32) / (width - 1)
    y_undistorted = y_coords.astype(np.float32) / (height - 1)

    # Calculate displacement
    dx = stmap[:, :, 0] - x_undistorted
    dy = stmap[:, :, 1] - y_undistorted

    # Convert to visualization
    displacement_mag = np.sqrt(dx**2 + dy**2)
    displacement_vis = displacement_mag / np.max(displacement_mag)

    # Create RGB visualization
    vis = np.zeros((height, width, 3), dtype=np.float32)
    vis[:, :, 0] = dx * 10 + 0.5  # Red = horizontal displacement
    vis[:, :, 1] = dy * 10 + 0.5  # Green = vertical displacement
    vis[:, :, 2] = displacement_vis  # Blue = magnitude

    vis = np.clip(vis, 0, 1)

    if output_path and HAS_OIIO:
        # Save visualization
        spec = oiio.ImageSpec(width, height, 3, oiio.FLOAT)
        out = oiio.ImageOutput.create(str(output_path))
        out.open(str(output_path), spec)
        out.write_image(vis)
        out.close()

    return vis


# Example usage
if __name__ == '__main__':
    print("=" * 60)
    print("POTK ST-Map Generator")
    print("=" * 60)

    # Create mock coefficients (replace with real POTK data)
    degree = 5
    num_coeffs = (degree + 1) * (degree + 2) // 2

    coefficients = {
        'exit_pupil_x': np.random.randn(num_coeffs) * 0.02,
        'exit_pupil_y': np.random.randn(num_coeffs) * 0.02,
    }

    # Set linear terms to 1.0 (pass-through)
    coefficients['exit_pupil_x'][1] = 1.0  # x term
    coefficients['exit_pupil_y'][2] = 1.0  # y term

    # Add some barrel distortion
    coefficients['exit_pupil_x'][3] = 0.1  # x^2 term
    coefficients['exit_pupil_y'][5] = 0.1  # y^2 term

    print(f"\n1. Generating ST-Map (degree {degree})...")
    stmap = generate_lens_stmap(coefficients, resolution=(2048, 2048), degree=degree)

    print(f"✓ ST-Map generated:")
    print(f"  Resolution: {stmap.shape[1]}x{stmap.shape[0]}")
    print(f"  Channels: {stmap.shape[2]} (RG=UV, B=unused)")
    print(f"  Data type: {stmap.dtype}")

    # Save ST-Map
    output_dir = Path('vex/stmaps')
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n2. Saving ST-Map...")

    if HAS_OIIO:
        output_path = output_dir / 'lens_distortion_stmap.exr'
        if save_stmap_exr(stmap, output_path):
            print(f"✓ Saved EXR: {output_path}")
            print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

        # Save visualization
        vis_path = output_dir / 'lens_distortion_visualization.exr'
        visualize_stmap(stmap, vis_path)
        print(f"✓ Saved visualization: {vis_path}")
    else:
        output_path = output_dir / 'lens_distortion_stmap.npy'
        save_stmap_npy(stmap, output_path)
        print(f"✓ Saved NumPy array: {output_path}")
        print(f"  (Install OpenImageIO to save as EXR)")

    print("\n" + "=" * 60)
    print("ST-Map Generation Complete!")
    print("=" * 60)
    print(f"""
How to use in Houdini:

1. In COPs (Compositing):
   - Load your render
   - Add "Lens Distortion" COP
   - Or use "UV Map" COP with the ST-Map texture
   - Apply displacement

2. In Karma (as texture):
   - Load ST-Map as texture
   - Use in shader to distort UVs
   - Apply to camera frustum

3. In Nuke (industry standard):
   - STMap node
   - Connect ST-Map to 'map' input
   - Connect render to 'source'
   - Done!

Note: This example uses mock distortion.
      For production, load real POTK polynomial coefficients.
""")
