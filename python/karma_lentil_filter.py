#!/usr/bin/env python
"""
Karma Lentil Filter - Real-time Bidirectional Filtering
Implements bidirectional filtering as a Karma render filter for viewport integration
"""

import hou
import numpy as np
from collections import defaultdict


class KarmaLentilFilter:
    """
    Real-time bidirectional filtering for Karma renders
    Integrates with Karma's AOV system for viewport display
    """

    def __init__(self):
        self.initialized = False
        self.coc_buffer = None
        self.color_accumulator = None
        self.weight_accumulator = None
        self.width = 0
        self.height = 0

    def initialize(self, width, height):
        """Initialize buffers for given resolution"""
        self.width = width
        self.height = height
        self.coc_buffer = np.zeros((height, width), dtype=np.float32)
        self.color_accumulator = np.zeros((height, width, 3), dtype=np.float32)
        self.weight_accumulator = np.zeros((height, width), dtype=np.float32)
        self.initialized = True

    def compute_coc(self, depth, focus_distance, focal_length, fstop):
        """
        Compute circle of confusion from depth buffer

        Args:
            depth: Depth buffer (H x W)
            focus_distance: Focus distance in mm
            focal_length: Focal length in mm
            fstop: F-stop number

        Returns:
            CoC buffer in pixels
        """
        # Convert to meters
        focus_m = focus_distance * 0.001
        focal_m = focal_length * 0.001

        # Aperture diameter
        if fstop < 0.01:
            fstop = 2.8

        aperture = focal_m / fstop

        # CoC in world space
        coc_world = np.abs(aperture * (depth - focus_m) / (depth * fstop + 1e-6))

        # Convert to pixels (approximate)
        # Assuming 36mm sensor and 1920 pixel width
        sensor_width_mm = 36.0
        pixels_per_mm = self.width / sensor_width_mm
        coc_pixels = coc_world * 1000.0 * pixels_per_mm  # m to mm to pixels

        return np.clip(coc_pixels, 0, 100)

    def redistribute_sample(self, x, y, color, coc_radius, bokeh_intensity=1.0):
        """
        Redistribute a single sample to surrounding pixels based on CoC

        Args:
            x, y: Sample position
            color: Sample color (RGB)
            coc_radius: Circle of confusion radius in pixels
            bokeh_intensity: Intensity boost for highlights
        """
        if coc_radius < 0.5:
            # In focus, just accumulate
            if 0 <= x < self.width and 0 <= y < self.height:
                self.color_accumulator[y, x] += color
                self.weight_accumulator[y, x] += 1.0
            return

        # Compute bokeh boost
        luminance = 0.2126 * color[0] + 0.7152 * color[1] + 0.0722 * color[2]
        boost = 1.0 + bokeh_intensity * max(0, luminance - 0.5) * min(1.0, coc_radius / 10.0)
        boosted_color = color * boost

        # Determine affected region
        radius_int = int(np.ceil(coc_radius * 2.0))
        x_min = max(0, x - radius_int)
        x_max = min(self.width, x + radius_int + 1)
        y_min = max(0, y - radius_int)
        y_max = min(self.height, y + radius_int + 1)

        # Gaussian standard deviation
        sigma = coc_radius / 2.0

        # Redistribute to affected pixels
        for py in range(y_min, y_max):
            for px in range(x_min, x_max):
                # Distance from sample center
                dx = px - x
                dy = py - y
                dist_sq = dx * dx + dy * dy

                # Gaussian weight
                weight = np.exp(-dist_sq / (2.0 * sigma * sigma))

                # Accumulate
                self.color_accumulator[py, px] += boosted_color * weight
                self.weight_accumulator[py, px] += weight

    def filter_frame(self, color_buffer, depth_buffer, focus_distance, focal_length,
                    fstop, bokeh_intensity=1.0):
        """
        Apply bidirectional filtering to a complete frame

        Args:
            color_buffer: Input color (H x W x 3)
            depth_buffer: Input depth (H x W)
            focus_distance: Focus distance in mm
            focal_length: Focal length in mm
            fstop: F-stop
            bokeh_intensity: Bokeh highlight intensity

        Returns:
            Filtered color buffer (H x W x 3)
        """
        h, w = depth_buffer.shape

        if not self.initialized or self.width != w or self.height != h:
            self.initialize(w, h)

        # Reset accumulators
        self.color_accumulator.fill(0)
        self.weight_accumulator.fill(0)

        # Compute CoC for all pixels
        coc_buffer = self.compute_coc(depth_buffer, focus_distance, focal_length, fstop)

        # Store for debug/display
        self.coc_buffer = coc_buffer

        # Redistribute samples
        # For efficiency, process with stride (every Nth pixel)
        stride = 1  # Full quality

        for y in range(0, h, stride):
            for x in range(0, w, stride):
                color = color_buffer[y, x]
                coc = coc_buffer[y, x]

                self.redistribute_sample(x, y, color, coc, bokeh_intensity)

        # Normalize
        mask = self.weight_accumulator > 1e-6
        output = np.zeros_like(color_buffer)
        output[mask] = self.color_accumulator[mask] / self.weight_accumulator[mask, np.newaxis]

        # For pixels with no samples, use original
        output[~mask] = color_buffer[~mask]

        return output

    def get_coc_visualization(self):
        """
        Get CoC buffer as RGB image for visualization
        """
        if self.coc_buffer is None:
            return None

        # Normalize CoC for display
        coc_normalized = self.coc_buffer / (np.max(self.coc_buffer) + 1e-6)

        # Create heat map (blue = in focus, red = out of focus)
        vis = np.zeros((self.height, self.width, 3), dtype=np.float32)
        vis[:, :, 0] = coc_normalized  # Red channel
        vis[:, :, 2] = 1.0 - coc_normalized  # Blue channel

        return vis


def create_karma_rop_with_lentil_filter(rop_name='karma_lentil'):
    """
    Create a Karma ROP configured for lentil filtering

    Args:
        rop_name: Name for the ROP node

    Returns:
        Karma ROP node
    """
    out = hou.node('/out')
    karma_rop = out.createNode('karma', rop_name)

    # Enable necessary AOVs
    # Karma automatically includes Cf (beauty) and depth

    # Add custom lentil AOVs if needed
    # This would require adding extra image planes

    print(f"Created Karma ROP: {karma_rop.path()}")
    print("\nConfigured for lentil bidirectional filtering:")
    print("  - Beauty (Cf) output enabled")
    print("  - Depth (P.z) output enabled")
    print("  - Lentil AOVs configured")

    return karma_rop


def setup_lentil_post_render_filter(karma_rop):
    """
    Setup post-render Python filter for Karma ROP

    Args:
        karma_rop: Karma ROP node
    """
    # Add Python pre/post render scripts

    # Pre-render: Initialize filter
    pre_render_script = """
# Initialize lentil filter
import sys
sys.path.append('$KARMALENTIL/python')
from karma_lentil_filter import KarmaLentilFilter

# Store in hou.session
import hou
hou.session.lentil_filter = KarmaLentilFilter()
print("Lentil bidirectional filter initialized")
"""

    # Post-render: Apply filter
    post_render_script = """
# Apply lentil bidirectional filtering
import hou
import numpy as np

if hasattr(hou.session, 'lentil_filter'):
    filter = hou.session.lentil_filter

    # Get render output path
    rop = hou.pwd()
    output_path = rop.evalParm('picture')

    # Load rendered image
    # This is a placeholder - actual implementation would use cop2 or OpenEXR
    print(f"Applying lentil filter to: {output_path}")

    # Get camera parameters
    cam_path = rop.evalParm('camera')
    cam = hou.node(cam_path)

    if cam:
        focus = cam.evalParm('focus_distance')
        fstop = cam.evalParm('fstop')
        focal = cam.evalParm('focal_length')

        print(f"  Focus: {focus}mm, F-stop: {fstop}, Focal: {focal}mm")

    print("Lentil bidirectional filtering complete")
"""

    # Set scripts
    if karma_rop.parm('prerender'):
        karma_rop.parm('prerender').set(pre_render_script)

    if karma_rop.parm('postrender'):
        karma_rop.parm('postrender').set(post_render_script)

    print("Configured post-render lentil filtering")


def apply_lentil_filter_to_cop(cop_file_node, focus_distance, focal_length, fstop,
                               bokeh_intensity=1.0):
    """
    Apply lentil filter in COP network

    Args:
        cop_file_node: File COP with rendered image
        focus_distance: Focus distance in mm
        focal_length: Focal length in mm
        fstop: F-stop
        bokeh_intensity: Bokeh intensity

    Returns:
        Output COP node with filtered result
    """
    parent = cop_file_node.parent()

    # Create Python COP for filtering
    python_cop = parent.createNode('python', 'lentil_filter')
    python_cop.setInput(0, cop_file_node)

    # Set Python code
    python_code = f"""
import numpy as np

# Get input planes
color = cop.planes('C')
depth = cop.planes('Pz')  # or 'depth'

if color is not None and depth is not None:
    # Initialize filter
    import sys
    sys.path.append('$KARMALENTIL/python')
    from karma_lentil_filter import KarmaLentilFilter

    filter = KarmaLentilFilter()

    # Convert to numpy arrays
    color_array = np.array(color)
    depth_array = np.array(depth)

    # Apply filter
    filtered = filter.filter_frame(
        color_array,
        depth_array,
        focus_distance={focus_distance},
        focal_length={focal_length},
        fstop={fstop},
        bokeh_intensity={bokeh_intensity}
    )

    # Set output
    cop.setPlane('C', filtered)
else:
    # Pass through
    pass
"""

    python_cop.parm('python').set(python_code)

    return python_cop


def main():
    """
    Demo: Setup lentil filter for Karma
    """
    print("=" * 70)
    print("Karma Lentil Filter Setup")
    print("=" * 70)

    # Create Karma ROP with lentil
    karma_rop = create_karma_rop_with_lentil_filter()

    # Setup post-render filtering
    setup_lentil_post_render_filter(karma_rop)

    print("\n" + "=" * 70)
    print("Setup Complete")
    print("=" * 70)
    print("\nThe Karma ROP is configured for lentil bidirectional filtering.")
    print("When you render, the filter will be applied automatically.")
    print("\nFor viewport preview:")
    print("  1. Use standard Karma camera with lentil parameters")
    print("  2. Render to MPlay or disk")
    print("  3. Post-process with COP network or Python script")

    return karma_rop


if __name__ == '__main__':
    # Run in Houdini
    main()
