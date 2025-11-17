# KarmaLentil Quick Start

Get realistic lens aberrations in Karma in under 5 minutes!

## 1. Installation (1 minute)

### Automatic Installation

**Linux/macOS**:
```bash
cd /path/to/karmalentil
./install_karmalentil.sh
```

**Windows**:
```cmd
cd C:\path\to\karmalentil
install_karmalentil.bat
```

The installer:
- ✓ Detects your Houdini version automatically
- ✓ Configures all environment paths
- ✓ Sets up the plugin package
- ✓ Makes shelf tools available

See [PLUGIN_INSTALLATION.md](PLUGIN_INSTALLATION.md) for troubleshooting.

## 2. Launch Houdini (10 seconds)

```bash
houdini
```

After launching, verify installation in Python Shell:

```python
import hou
print(hou.getenv("KARMALENTIL"))  # Should show installation path
```

## 3. Create Lentil Camera (30 seconds)

**Using Shelf Tool (Easiest)**:

1. Find the **karmalentil** shelf at the top of Houdini
2. Click **"Lentil Camera"** button
3. Done! A complete LOP network is created with:
   - Lentil camera at `/cameras/lentil_camera`
   - Example scene geometry (spheres, ground plane)
   - Dome light for illumination
   - Karma render settings configured
   - Viewport set to Karma rendering

**Manual Python Setup** (Alternative):

In Houdini's Python Shell:

```python
import sys
sys.path.append('/path/to/karmalentil/python')
import setup_lentil_lops
lop_network, camera = setup_lentil_lops.main()
```

## 4. View in Viewport (Immediate)

The viewport automatically switches to Karma rendering in Solaris:

- ✓ Real-time lens aberrations
- ✓ Depth of field
- ✓ Bokeh effects
- ✓ Interactive parameter updates

## 5. Adjust Parameters (1 minute)

Select the camera LOP node in your network. In the Parameter panel, find the **"Lentil Lens"** tab:

### Basic Parameters:
- **Enable Lentil**: Toggle lens effects on/off
- **Lens Model**: Select from available lenses (e.g., "double_gauss_50mm")
- **Focal Length**: 50.0mm (standard lens)
- **F-Stop**: 2.8 (for visible DOF, use 1.4-2.8)
- **Focus Distance**: 5000.0mm (5 meters)

### Advanced Parameters:
- **Sensor Width**: 36.0mm (full-frame sensor)
- **Chromatic Aberration**: 1.0 (color fringing)
- **Bokeh Blades**: 6 (hexagonal bokeh, 0 = circular)
- **Bokeh Rotation**: 0.0° (rotate aperture shape)
- **Enable Bidirectional**: On (realistic bokeh highlights)
- **Bokeh Intensity**: 1.0 (highlight preservation)

## 6. Render! (30 seconds)

**Test Render**:
1. Click the **"render"** node at the end of your LOP network
2. Press the **Render** button in the parameter panel
3. Watch your scene render with realistic lens effects!

**Recommended Settings for Quality**:
- Pixel Samples: 1024 (32x32) for smooth bokeh
- Resolution: 1920x1080
- Renderer: Karma XPU (GPU) for speed, or CPU for maximum quality

## Expected Results

You should see:
- ✓ **Depth of field** with realistic blur falloff
- ✓ **Bokeh shapes** (hexagonal with 6 blades, circular with 0)
- ✓ **Chromatic aberration** (color fringing at high-contrast edges)
- ✓ **Preserved highlights** in out-of-focus areas (bidirectional filtering)
- ✓ **Real-time preview** in Karma viewport

## Example Settings for Dramatic Effects

### Portrait Mode (Shallow DOF):
```
F-Stop: 1.4
Focus Distance: 2000mm (2 meters)
Bokeh Blades: 0 (circular)
Chromatic Aberration: 0.5
```

### Architecture (Sharp Focus):
```
F-Stop: 8.0
Focus Distance: 10000mm (10 meters)
Bokeh Blades: 6
Chromatic Aberration: 0.3
```

### Cinematic (Anamorphic-style):
```
F-Stop: 2.0
Focus Distance: 3000mm
Bokeh Blades: 6
Bokeh Rotation: 90.0°
Chromatic Aberration: 1.5
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Shelf not visible | Right-click shelf area → Shelves → Check "karmalentil" |
| No DOF visible | Set f-stop to 2.8 or lower |
| KARMALENTIL not set | Re-run installer, restart Houdini |
| Noisy bokeh | Increase pixel samples to 1024 (32x32) |
| Slow viewport | Reduce viewport quality or disable bidirectional |

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for detailed diagnostics.

## Post-Processing (Optional)

For even higher-quality bokeh in final renders:

1. Render with Karma (beauty and depth passes)
2. Use shelf tool **"Apply Bidirectional Filter"**
3. Select rendered EXR file
4. Get enhanced bokeh with perfect highlight preservation

Or via command line:
```bash
cd /path/to/karmalentil
python python/bidirectional_filter.py \
    render/scene.exr render/scene_filtered.exr \
    --focus 5000 --fstop 2.8 --focal-length 50
```

See [BIDIRECTIONAL.md](BIDIRECTIONAL.md) for complete documentation.

## Next Steps

### Explore More:
- **[USAGE.md](USAGE.md)** - Complete parameter reference
- **[VIEWPORT_INTEGRATION.md](VIEWPORT_INTEGRATION.md)** - Real-time workflow guide
- **[BIDIRECTIONAL.md](BIDIRECTIONAL.md)** - Advanced bokeh techniques

### Import Real Lenses:
1. Clone the original lentil repository: https://github.com/zpelgrims/lentil
2. Use shelf tool **"Import Lens"** to add more lenses
3. Select from 20+ real-world lens models!

### Customize:
- Add custom aperture textures for unique bokeh shapes
- Adjust lens polynomials for specific aberrations
- Create your own lens models

## LOPs/Solaris Architecture

KarmaLentil works natively with:
- ✓ **LOPs/Solaris** - USD-based scene graph
- ✓ **Karma XPU** - GPU-accelerated rendering
- ✓ **Karma CPU** - Maximum quality rendering
- ✓ **Real-time viewport** - Interactive lens adjustments

**Note**: This plugin is specifically designed for LOPs/Solaris. It does not work with OBJ-level cameras, as Karma requires a USD-based workflow.

## Support

If you encounter issues:
1. Run diagnostic: Click **"Lentil Help"** shelf tool
2. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. Review console output on Houdini startup
4. Check GitHub issues

---

**Happy rendering with physically-accurate lens aberrations!** 📷✨
