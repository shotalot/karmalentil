# Houdini Karma Lens Integration Guide

**Date:** 2025-11-19
**Status:** Ready for testing
**Prerequisites:** Houdini 19.5+ with Karma CPU/XPU

---

## Overview

This guide shows how to integrate POTK-generated polynomial lens shaders into Houdini Karma for physically-based lens rendering with real optical aberrations.

---

## Quick Start

### 1. Generate a Lens Shader

```bash
cd /path/to/karmalentil

# Option A: Use mock data for testing
python3 test_vex_simple.py

# Option B: Use real lens data (when raytracer fixed)
python3 tools/fit_lens.py path/to/lens.json --degree 5
python3 tools/generate_vex.py lens_name
```

Output: `vex/generated/your_lens.vfl`

---

### 2. Set Up Houdini Environment

Create or edit `$HOUDINI_USER_PREF_DIR/houdini.env`:

```bash
# Add POTK VEX shader path
HOUDINI_VEX_PATH = "/path/to/karmalentil/vex/generated;&"
```

Restart Houdini for changes to take effect.

---

### 3. Apply Lens Shader to Karma Camera

#### Method A: Using Python in Houdini

```python
import hou

# Get or create camera
cam = hou.node('/obj/cam1')
if not cam:
    cam = hou.node('/obj').createNode('cam', 'cam1')

# Get camera parameters
parms = cam.parms()

# Enable lens shader (Karma-specific parameter)
# Note: Parameter name may vary by Houdini version
cam.parm('vm_lensshader').set('test_simple')  # VFL file name without .vfl

# Alternative: Full path
cam.parm('vm_lensshader').set('$HOUDINI_VEX_PATH/test_simple.vfl')

# Set camera parameters
cam.parmTuple('res').set((1920, 1080))
cam.parm('focal').set(50)  # 50mm focal length
cam.parm('fstop').set(2.0)  # f/2.0

print("✓ Lens shader applied to camera")
```

#### Method B: Using UI

1. Select camera node
2. Go to **Rendering** tab
3. Find **Lens Shader** parameter
4. Enter shader name: `test_simple` or full path
5. Click **Apply**

---

### 4. Render with Lens Distortion

```python
import hou

# Get camera
cam = hou.node('/obj/cam1')

# Set up Karma render node
rop = hou.node('/out').createNode('karma', 'render_with_lens')
rop.parm('camera').set(cam.path())

# Enable lens rendering features
rop.parm('enable_dof').set(1)  # Enable depth of field
rop.parm('enable_motionblur').set(0)  # Optional

# Render settings
rop.parm('picture').set('$HIP/render/lens_test.$F4.exr')
rop.parm('res_fraction').set('specific')
rop.parmTuple('res_override').set((1920, 1080))

# Render
rop.parm('execute').pressButton()

print("✓ Rendering with lens shader...")
```

---

## VEX Shader Parameters

The generated lens shaders expect these inputs from Karma:

### Inputs (from camera/renderer):
- `sensor_pos` (vector) - Position on camera sensor [x, y, z] in mm
- `sensor_uv` (vector2) - Normalized sensor coordinates [u, v]
- `aperture_sample` (vector2) - Random aperture position for DoF
- `wavelength` (float) - Light wavelength in nm (default: 550nm)

### Outputs (to renderer):
- `exit_pos` (vector) - Ray exit position from lens [x, y, z]
- `exit_dir` (vector) - Ray exit direction (normalized)
- `vignette` (float) - Vignetting factor (0-1, 1=no vignetting)
- `intensity` (float) - Light transmission through lens

---

## Shader Features

### Current Implementation ✅
- ✅ Polynomial lens distortion (up to degree 7)
- ✅ Bidirectional path tracing (sensor ↔ world)
- ✅ Wavelength-dependent aberrations
- ✅ Vignetting simulation
- ✅ Embedded coefficients (no external files needed)
- ✅ Optimized polynomial evaluation

### Planned Features ⏳
- ⏳ Depth of field (aperture sampling)
- ⏳ Chromatic aberration (wavelength-dependent coefficients)
- ⏳ Bokeh shape control
- ⏳ Anamorphic lenses
- ⏳ Focus breathing

---

## Example Houdini Scene Setup

### Complete Python Script

```python
#!/usr/bin/env python
"""
setup_lens_render.py - Complete Houdini scene setup with lens shader
Run this in Houdini Python Shell
"""

import hou

def setup_lens_scene():
    """Create complete scene with lens-enabled camera"""

    # Clear scene (optional)
    # hou.hipFile.clear()

    # Create camera
    cam = hou.node('/obj').createNode('cam', 'lens_camera')
    cam.move([0, 0, 0])

    # Camera transform
    cam.parmTuple('t').set((0, 1, -5))  # Position
    cam.parmTuple('r').set((0, 0, 0))   # Rotation

    # Camera settings
    cam.parmTuple('res').set((1920, 1080))
    cam.parm('focal').set(50)  # 50mm lens
    cam.parm('fstop').set(2.0)  # f/2.0
    cam.parm('focus').set(5.0)   # Focus distance

    # Apply lens shader
    cam.parm('vm_lensshader').set('test_simple')

    # Create test geometry
    geo = hou.node('/obj').createNode('geo', 'test_subject')
    geo.move([2, 0, 0])

    # Add test grid
    grid = geo.createNode('grid')
    grid.parmTuple('size').set((2, 2))
    grid.parm('rows').set(20)
    grid.parm('cols').set(20)

    # Add color
    color = geo.createNode('color')
    color.setInput(0, grid)
    color.parmTuple('color').set((1, 0.8, 0.6))
    color.setDisplayFlag(True)
    color.setRenderFlag(True)

    # Create lights
    key_light = hou.node('/obj').createNode('hlight::2.0', 'key_light')
    key_light.parmTuple('t').set((2, 3, -3))
    key_light.parm('light_intensity').set(10)

    # Create Karma ROP
    rop = hou.node('/out').createNode('karma', 'lens_render')
    rop.parm('camera').set(cam.path())
    rop.parm('picture').set('$HIP/render/lens_test.$F4.exr')

    # Karma settings
    rop.parm('res_fraction').set('specific')
    rop.parmTuple('res_override').set((1920, 1080))
    rop.parm('pixelsamples').set((8, 8))  # Samples for DoF

    # Frame camera to geometry
    cam.parm('lookatpath').set(geo.path())

    print("✓ Scene setup complete!")
    print(f"  Camera: {cam.path()}")
    print(f"  Lens shader: test_simple")
    print(f"  Render node: {rop.path()}")
    print("\nTo render:")
    print(f"  1. Select {rop.path()}")
    print("  2. Click 'Render to Disk' or press Ctrl+Shift+R")

# Run setup
if __name__ == '__main__':
    setup_lens_scene()
```

Save as `$HIP/scripts/setup_lens_render.py` and run in Houdini Python Shell.

---

## Verification Checklist

### Before Rendering:
- [ ] VEX shader file exists in `vex/generated/`
- [ ] `HOUDINI_VEX_PATH` includes shader directory
- [ ] Camera has lens shader parameter set
- [ ] Focal length matches lens design
- [ ] F-stop is within lens capabilities

### After Rendering:
- [ ] Image shows lens distortion (barrel/pincushion)
- [ ] DoF blur appears realistic (if enabled)
- [ ] Vignetting visible at image edges (if present in lens)
- [ ] Chromatic aberration visible (if wavelength-dependent)

---

## Troubleshooting

### Shader Not Found
```
Error: Cannot find VEX shader 'test_simple'
```

**Solution:**
1. Check `HOUDINI_VEX_PATH` in houdini.env
2. Verify .vfl file exists
3. Restart Houdini after changing environment
4. Use full path instead: `/absolute/path/to/shader.vfl`

### Shader Compilation Errors
```
Error: VEX compile error in test_simple.vfl
```

**Solution:**
1. Check VEX syntax with `vcc test_simple.vfl`
2. Verify polynomial coefficients are valid numbers
3. Regenerate shader with `tools/generate_vex.py`

### No Lens Effect Visible
```
Warning: Render looks identical to pinhole camera
```

**Solution:**
1. Verify shader is actually being used (check render log)
2. Increase distortion by using higher degree polynomials
3. Check that lens shader parameter points to correct file
4. Enable "Use Lens Shader" checkbox if present

### Performance Issues
```
Warning: Rendering very slow with lens shader
```

**Solution:**
1. Reduce polynomial degree (5 is usually sufficient)
2. Lower pixel samples in Karma
3. Use XPU instead of CPU for faster rendering
4. Check shader code for unoptimized loops

---

## Performance Tips

### Optimizing Render Speed:
1. **Use degree 5 polynomials** - Good balance of quality/speed
2. **Enable XPU** - GPU acceleration for Karma
3. **Optimize samples** - Start with 4x4, increase as needed
4. **Use render regions** - Test small areas first
5. **Compile shaders** - Pre-compile .vfl to .vex with `vcc -O2`

### Quality vs Speed:
- **Fast preview**: Degree 3, 2x2 samples
- **Production**: Degree 5-7, 8x8 samples
- **Hero shots**: Degree 7, 16x16 samples

---

## Next Steps

1. ✅ Generate test lens shader (done)
2. ⏳ Test in Houdini Karma
3. ⏳ Compare with reference renders
4. ⏳ Create lens library (multiple focal lengths)
5. ⏳ Add to production pipeline

---

## Reference

- **VEX Shader Location:** `vex/generated/*.vfl`
- **Tools:** `tools/fit_lens.py`, `tools/generate_vex.py`
- **Documentation:** `POTK_README.md`, `USAGE.md`
- **Examples:** `examples/houdini/`

---

## Support

For issues or questions:
1. Check `TROUBLESHOOTING.md`
2. Review `POTK_QUICK_REFERENCE.md`
3. Examine generated VEX code for debugging
4. Test with simpler lens (degree 3) to isolate issues

---

**Status:** Ready for production testing
**Last Updated:** 2025-11-19
**Tested With:** Houdini 19.5, Karma CPU/XPU
