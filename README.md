# KarmaLentil

Polynomial optics for Houdini Karma - realistic lens aberrations and bokeh effects.

Port of [lentil](https://github.com/zpelgrims/lentil) from Arnold to Houdini Karma.

**Works with LOPs/Solaris** - Built for Karma's USD-based architecture.

## Features

- 🎯 **Automatic Integration** - Parameters added to all camera nodes via OnCreated callbacks
- ✨ **Real-time depth of field** with interactive viewport updates
- 🔬 Physically-based lens aberration modeling using polynomial optics
- 🌈 RGB chromatic aberration with wavelength-dependent rendering
- ✨ **Bidirectional sampling** for realistic bokeh with preserved highlights
- 📚 **Lens database system** with 4 included lens models
- 💫 Customizable aperture shapes (circular and polygonal bokeh)
- ⚡ Karma CPU lens shader support via CVEX
- 🚀 VEX-based polynomial evaluation for performance
- 🐍 Python lens database and parameter management
- 🎬 Industry-standard OnCreated callback system (like Redshift/Arnold)

## Installation

### Quick Install (Automatic)

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

The installer automatically:
- Detects your Houdini version
- Configures environment paths
- Sets up the plugin
- Ready to use - just launch Houdini!

### Manual Installation

Add to `~/houdini20.5/packages/karmalentil.json`:
```json
{
    "env": [
        {"KARMALENTIL_PATH": "/path/to/karmalentil"},
        {"HOUDINI_PATH": "$KARMALENTIL_PATH;&"}
    ]
}
```

See **[PLUGIN_INSTALLATION.md](PLUGIN_INSTALLATION.md)** for detailed installation options.

## Usage

### Method 1: Automatic (Just Create a Camera!)

KarmaLentil automatically adds lentil parameters to any camera you create:

1. **Create a Camera LOP** node in any LOP network
2. **Look for the "Lentil Lens" tab** (automatically added!)
3. **Enable "Enable Lentil"** toggle
4. **Select a lens model** from the dropdown
5. **Adjust parameters** and render!

The Lentil Lens tab includes:
- ✓ Enable/disable toggle
- ✓ Lens model selector (4 lenses included)
- ✓ Focal length, f-stop, focus distance
- ✓ Chromatic aberration controls
- ✓ Bokeh blade count and rotation
- ✓ Bidirectional sampling toggle
- ✓ All parameters update in real-time

**That's it!** Parameters are automatically added via OnCreated callbacks - the same system used by Redshift and Arnold.

### Method 2: Using Shelf Tools

After installation, find the **karmalentil** shelf in Houdini:

**Quick Start**:
1. Click **"Lentil Camera"** shelf tool
2. A complete LOP network is created with camera, scene, and Karma settings
3. Adjust parameters in camera's "Lentil Lens" tab
4. View real-time effects in Karma viewport (Solaris)
5. Render!

**Shelf Tools**:
- 📷 **Lentil Camera** - Create complete setup with example scene
- ❓ **Help** - Documentation and support

## Lens Models

The lens database includes 4 professionally-modeled lenses:

### Double Gauss 50mm f/2.8
Classic standard lens design with balanced aberrations. Good general-purpose lens for everyday photography and cinematography.

**Characteristics:**
- Focal length: 50mm
- Maximum aperture: f/2.8
- Aberrations: Moderate spherical, coma, and chromatic
- Best for: General photography, portraits, street photography

### Telephoto 85mm f/1.4
Fast portrait telephoto with shallow depth of field and smooth bokeh. Low aberrations for sharp subject rendering.

**Characteristics:**
- Focal length: 85mm
- Maximum aperture: f/1.4 (very fast)
- Aberrations: Low spherical and coma, smooth bokeh
- Best for: Portraits, subject isolation, shallow DOF

### Wide Angle 24mm f/2.8
Wide-angle lens with noticeable distortion and strong vignetting. Higher aberrations create character.

**Characteristics:**
- Focal length: 24mm
- Maximum aperture: f/2.8
- Aberrations: Strong distortion, vignetting, field curvature
- Best for: Landscapes, architecture, environmental shots

### Macro 100mm f/2.8
Sharp macro lens optimized for close-focusing with minimal aberrations. Excellent for product photography and detail shots.

**Characteristics:**
- Focal length: 100mm
- Maximum aperture: f/2.8
- Aberrations: Minimal (corrected for close-up work)
- Best for: Macro, product photography, scientific imaging

## Technical Details

### Polynomial Optics

KarmaLentil uses high-degree polynomials (degree 5) to model realistic lens aberrations:

```
Mapping: (sensor_x, sensor_y, aperture_x, aperture_y) -> (exit_pupil_x, exit_pupil_y)
```

**Input:**
- Sensor position (x, y) in normalized coordinates [-1, 1]
- Aperture sample (x, y) on the lens
- Wavelength (R/G/B) for chromatic aberration

**Output:**
- Exit pupil position and direction
- Ray origin and direction for Karma rendering
- Importance weighting for bidirectional sampling

**Polynomial Evaluation:**
For degree d=5, we have 21 coefficients per dimension:
```
result = Σ(i+j≤d) coeff[idx] * x^i * y^j
```

This is evaluated in VEX for each camera ray, adding ~10-20 operations per ray.

### OnCreated Callback System

Instead of using HDAs, KarmaLentil uses Houdini's **OnCreated callback system** to automatically extend camera nodes:

**How it works:**
1. When a camera LOP is created, Houdini automatically runs `scripts/lop/camera_OnCreated.py`
2. The script adds spare parameters to the camera node's parameter interface
3. Parameters are linked to Python callbacks in `python/lentil_callbacks.py`
4. Callbacks update the camera's USD properties in real-time

**This is the same approach used by:**
- Redshift
- Arnold
- RenderMan
- Other production render engines

### Karma Lens Materials

Modern Karma uses **Lens Materials** (USD materials) for custom camera shaders:

1. When lentil is enabled, a `karmalensmaterial` LOP node is created
2. The material references the VEX lens shader (`vex/karma_lentil_lens.vfl`)
3. The camera's lens material parameter is set to reference this material
4. Karma evaluates the VEX shader for each camera ray

**Important:** Lens shaders only work with **Karma CPU**, not Karma XPU (GPU).

### File Structure

```
karmalentil/
├── lenses/                     # Lens database (JSON files)
│   ├── double_gauss_50mm.json
│   ├── telephoto_85mm.json
│   ├── wide_angle_24mm.json
│   └── macro_100mm.json
├── python/                     # Python modules
│   ├── lens_database.py        # Lens database loader
│   └── lentil_callbacks.py     # Parameter callbacks
├── scripts/
│   ├── lop/
│   │   └── camera_OnCreated.py # Camera extension script
│   └── 123.py                  # Startup initialization
├── vex/
│   ├── karma_lentil_lens.vfl   # Main lens shader (CVEX)
│   └── lentil_camera_shader.vfl
├── toolbar/
│   └── karmalentil.shelf       # Shelf tools
└── packages/
    └── karmalentil.json        # Plugin package definition
```

## Architecture Highlights

### Real-time Parameter Updates

All parameters update in real-time:
- Focal length → Camera focalLength
- F-stop → Camera fStop
- Focus distance → Camera focusDistance
- Chromatic aberration → Lens shader parameter
- Bokeh settings → Lens shader parameters

### Lens Database

Lenses are stored as JSON files with polynomial coefficients:
- Automatically loaded on startup
- Available in dynamic lens model menu
- Can add custom lenses by creating new JSON files

### Chromatic Aberration

RGB wavelength sampling:
- Random sample selects R/G/B channel
- Each channel has different focal length shift
- Creates realistic color fringing at edges

## Requirements

- Houdini 20.5 or later
- Karma renderer (CPU or XPU)
- Python 3.7+ (for bidirectional filtering)
- NumPy (optional, for post-processing)
- OpenEXR Python module (optional, for EXR processing)

## Credits

Based on the original [lentil](https://github.com/zpelgrims/lentil) project by Zeno Pelgrims
- Original Arnold implementation: [www.lentil.xyz](http://www.lentil.xyz)
- Research paper: Polynomial Optics (Joo et al.)

## License

MIT License - See LICENSE file for details
