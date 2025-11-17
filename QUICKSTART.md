# KarmaLentil Quick Start

## 5-Minute Setup

### 1. Installation (30 seconds)

```bash
# Clone or download this repository
cd /path/to/karmalentil

# Add to Houdini path (Linux/macOS)
export HOUDINI_PATH="/path/to/karmalentil:&"

# Or add to houdini.env:
echo 'HOUDINI_PATH = "/path/to/karmalentil:&"' >> ~/houdini20.5/houdini.env
```

### 2. Launch Houdini (10 seconds)

```bash
houdini
```

### 3. Create Lentil Camera (2 minutes)

**Method A: Python Script (Easiest)**

In Houdini's Python Shell (Windows → Shell → Python):

```python
import sys
sys.path.append('/path/to/karmalentil/examples')
import setup_lentil_camera
setup_lentil_camera.setup_example_scene()
```

This creates a camera with lentil parameters pre-configured.

**Method B: Manual Setup**

1. Create a camera: `/obj/cam1`
2. Add spare parameters (right-click → Edit Parameter Interface → From Folders → Add Folder):
   - Folder name: "Lentil"
   - Add these parameters:
     - `enable_lentil` (Toggle, default: On)
     - `lens_model` (String, default: "double_gauss_50mm")
     - `lentil_focal_length` (Float, default: 50.0)
     - `lentil_fstop` (Float, default: 2.8)
     - `lentil_focus_distance` (Float, default: 1000.0)
     - `lentil_sensor_width` (Float, default: 36.0)
     - `lentil_chromatic_aberration` (Float, default: 1.0)
     - `lentil_bokeh_blades` (Integer, default: 0)
     - `lentil_bokeh_rotation` (Float, default: 0.0)

### 4. Integrate VEX Shader (2 minutes)

**Important**: Currently, you need to manually integrate the VEX shader into your Karma camera. This will be simplified in future releases with an HDA.

**Option A: Inline VEX in Camera**

1. Inside your camera object, create a "Karma Lens Shader" node
2. Set the VEX code to reference the lentil shader
3. Point the camera to use this lens shader

**Option B: VOP Network**

1. Create a VOP network inside the camera
2. Add an "Inline Code" VOP
3. Copy the contents of `vex/camera/lentil_camera.vfl` into it
4. Wire outputs to camera outputs

### 5. Test Render (30 seconds)

1. Configure Karma render settings:
   - Render Engine: Karma CPU or XPU
   - Pixel Samples: 16x16 minimum (32x32 recommended)

2. Set lentil parameters for visible depth of field:
   ```
   lentil_fstop = 2.0  # Wide aperture
   lentil_focus_distance = 1000.0  # Focus at 1 meter
   lentil_chromatic_aberration = 1.0
   lentil_bokeh_blades = 6  # Hexagonal bokeh
   ```

3. Render!

## Expected Results

You should see:
- ✓ Depth of field effect (blur in out-of-focus areas)
- ✓ Bokeh shapes (hexagonal if blades = 6)
- ✓ Chromatic aberration (color fringing at edges)
- ✓ Realistic lens characteristics

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No DOF visible | Set f-stop to 2.8 or lower |
| VEX errors | Check include paths in lentil_camera.vfl |
| Slow renders | Set chromatic_aberration to 0.0 |
| Noisy bokeh | Increase Karma pixel samples to 32x32 |

## Next Steps

- **See USAGE.md** for detailed parameter explanations
- **See INSTALL.md** for importing additional lenses
- **See examples/** for Python setup scripts

## Current Limitations

This initial implementation:
- Requires manual VEX shader integration (HDA coming soon)
- Includes one sample lens (Double Gauss 50mm)
- Uses placeholder polynomials (replace with real fitted data)

To get real lens data:
1. Clone https://github.com/zpelgrims/lentil
2. Use `python/import_lens.py` to convert lens data
3. See INSTALL.md for details

## Support

For issues or questions:
- Check USAGE.md for detailed documentation
- Review original lentil docs: https://github.com/zpelgrims/lentil
- Open an issue on GitHub

---

**Happy rendering with realistic lens aberrations!**
