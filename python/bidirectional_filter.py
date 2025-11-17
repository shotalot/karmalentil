#!/usr/bin/env python
"""
Bidirectional Filtering for Karma/COPs
Implements sample redistribution based on circle of confusion

This can be used as:
1. A post-process in COPs on rendered images
2. A deep image compositing operation
3. A Python-based filter for EXR sequences
"""

import numpy as np
import os
import sys


def compute_coc(depth, focus_distance, focal_length_mm, fstop):
    """
    Compute circle of confusion from depth

    Args:
        depth: Depth in meters (array or scalar)
        focus_distance: Focus distance in mm
        focal_length_mm: Focal length in mm
        fstop: F-stop number

    Returns:
        CoC radius in mm (on sensor)
    """
    # Convert to meters
    focus_m = focus_distance * 0.001
    focal_m = focal_length_mm * 0.001

    # Aperture diameter
    if fstop < 0.01:
        fstop = 2.8  # Default

    aperture = focal_m / fstop

    # CoC formula
    coc = np.abs(aperture * (depth - focus_m) / (depth * fstop))

    # Convert to mm
    return coc * 1000.0


def coc_to_pixels(coc_mm, sensor_width_mm, image_width):
    """
    Convert CoC from mm (on sensor) to pixels

    Args:
        coc_mm: CoC in mm
        sensor_width_mm: Sensor width in mm
        image_width: Image width in pixels

    Returns:
        CoC radius in pixels
    """
    mm_per_pixel = sensor_width_mm / image_width
    return coc_mm / mm_per_pixel


def gaussian_kernel(radius, sigma=None):
    """
    Generate a Gaussian kernel for convolution

    Args:
        radius: Kernel radius in pixels
        sigma: Standard deviation (defaults to radius/2)

    Returns:
        2D numpy array
    """
    if sigma is None:
        sigma = radius / 2.0

    size = int(radius * 2) + 1
    center = radius

    y, x = np.ogrid[-center:size-center, -center:size-center]
    kernel = np.exp(-(x*x + y*y) / (2.0 * sigma * sigma))

    # Normalize
    kernel /= kernel.sum()

    return kernel


def redistribute_samples(image, depth_image, focus_distance, focal_length, fstop,
                        sensor_width=36.0, bokeh_intensity=1.0):
    """
    Apply bidirectional filtering to redistribute samples based on CoC

    Args:
        image: Input RGB image (H x W x 3)
        depth_image: Depth map in meters (H x W)
        focus_distance: Focus distance in mm
        focal_length: Focal length in mm
        fstop: F-stop number
        sensor_width: Sensor width in mm
        bokeh_intensity: Intensity boost for bokeh highlights

    Returns:
        Filtered RGB image (H x W x 3)
    """
    height, width = depth_image.shape

    # Compute CoC for each pixel
    coc_mm = compute_coc(depth_image, focus_distance, focal_length, fstop)
    coc_pixels = coc_to_pixels(coc_mm, sensor_width, width)

    # Initialize output
    output = np.zeros_like(image)
    weight_sum = np.zeros((height, width), dtype=np.float32)

    # Process each pixel
    # This is a simplified version - full implementation would use proper splatting
    from scipy.ndimage import gaussian_filter

    # For each pixel, determine how much it contributes to neighbors
    for c in range(3):  # RGB channels
        # Apply variable Gaussian blur based on CoC
        # This is an approximation of true bidirectional filtering

        # Create weighted image (brighten based on CoC for bokeh effect)
        luma = 0.2126 * image[:,:,0] + 0.7152 * image[:,:,1] + 0.0722 * image[:,:,2]
        bokeh_weight = 1.0 + bokeh_intensity * np.maximum(0, luma - 0.5) * np.minimum(1.0, coc_pixels / 10.0)

        weighted_image = image[:,:,c] * bokeh_weight

        # Apply variable blur (simplified - should be per-pixel)
        # Use max CoC for blur radius
        max_coc = np.max(coc_pixels)
        if max_coc > 0.5:
            sigma = max_coc / 2.0
            output[:,:,c] = gaussian_filter(weighted_image, sigma=sigma)
        else:
            output[:,:,c] = image[:,:,c]

    return output


def apply_bidirectional_filter_to_exr(input_path, output_path,
                                     focus_distance=1000.0,
                                     focal_length=50.0,
                                     fstop=2.8,
                                     sensor_width=36.0,
                                     bokeh_intensity=1.0):
    """
    Apply bidirectional filtering to an EXR image with depth

    Requires OpenEXR and Imath packages:
        pip install OpenEXR Imath

    Args:
        input_path: Path to input EXR with Cf (color) and P.z or depth AOV
        output_path: Path to output EXR
        focus_distance: Focus distance in mm
        focal_length: Focal length in mm
        fstop: F-stop
        sensor_width: Sensor width in mm
        bokeh_intensity: Bokeh highlight intensity
    """
    try:
        import OpenEXR
        import Imath
    except ImportError:
        print("Error: OpenEXR module not found. Install with: pip install OpenEXR Imath")
        return False

    # Open input EXR
    exr_file = OpenEXR.InputFile(input_path)
    header = exr_file.header()

    dw = header['dataWindow']
    width = dw.max.x - dw.min.x + 1
    height = dw.max.y - dw.min.y + 1

    # Read color channels
    FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)

    r_str = exr_file.channel('R', FLOAT)
    g_str = exr_file.channel('G', FLOAT)
    b_str = exr_file.channel('B', FLOAT)

    r = np.frombuffer(r_str, dtype=np.float32).reshape(height, width)
    g = np.frombuffer(g_str, dtype=np.float32).reshape(height, width)
    b = np.frombuffer(b_str, dtype=np.float32).reshape(height, width)

    image = np.stack([r, g, b], axis=2)

    # Read depth (try multiple AOV names)
    depth = None
    for depth_channel in ['P.z', 'depth', 'Z', 'Pz']:
        if depth_channel in header['channels']:
            depth_str = exr_file.channel(depth_channel, FLOAT)
            depth = np.frombuffer(depth_str, dtype=np.float32).reshape(height, width)
            print(f"Found depth in channel: {depth_channel}")
            break

    if depth is None:
        print("Error: No depth channel found in EXR (tried: P.z, depth, Z, Pz)")
        return False

    # Convert depth to meters if needed (assume negative Z for camera space)
    depth = np.abs(depth)

    # Apply bidirectional filtering
    print(f"Applying bidirectional filter:")
    print(f"  Focus distance: {focus_distance}mm")
    print(f"  Focal length: {focal_length}mm")
    print(f"  F-stop: {fstop}")
    print(f"  Image size: {width}x{height}")

    filtered = redistribute_samples(
        image, depth, focus_distance, focal_length, fstop,
        sensor_width, bokeh_intensity
    )

    # Write output EXR
    header = OpenEXR.Header(width, height)
    header['channels'] = {
        'R': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT)),
        'G': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT)),
        'B': Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT)),
    }

    out_file = OpenEXR.OutputFile(output_path, header)
    out_file.writePixels({
        'R': filtered[:,:,0].tobytes(),
        'G': filtered[:,:,1].tobytes(),
        'B': filtered[:,:,2].tobytes(),
    })
    out_file.close()

    print(f"Saved filtered image to: {output_path}")
    return True


def main():
    """
    Command-line interface for bidirectional filtering
    """
    import argparse

    parser = argparse.ArgumentParser(
        description='Apply bidirectional filtering to EXR images with depth'
    )
    parser.add_argument('input', help='Input EXR file path')
    parser.add_argument('output', help='Output EXR file path')
    parser.add_argument('--focus', type=float, default=1000.0,
                       help='Focus distance in mm (default: 1000)')
    parser.add_argument('--focal-length', type=float, default=50.0,
                       help='Focal length in mm (default: 50)')
    parser.add_argument('--fstop', type=float, default=2.8,
                       help='F-stop (default: 2.8)')
    parser.add_argument('--sensor-width', type=float, default=36.0,
                       help='Sensor width in mm (default: 36)')
    parser.add_argument('--bokeh-intensity', type=float, default=1.0,
                       help='Bokeh highlight intensity (default: 1.0)')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        return 1

    success = apply_bidirectional_filter_to_exr(
        args.input, args.output,
        focus_distance=args.focus,
        focal_length=args.focal_length,
        fstop=args.fstop,
        sensor_width=args.sensor_width,
        bokeh_intensity=args.bokeh_intensity
    )

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
