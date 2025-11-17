# KarmaLentil

Polynomial optics for Houdini Karma - realistic lens aberrations and bokeh effects.

Port of [lentil](https://github.com/zpelgrims/lentil) from Arnold to Houdini Karma.

**Works with LOPs/Solaris** - Built for Karma's USD-based architecture.

## Features

- ✨ **Real-time viewport integration** with Karma renderer
- 🎯 Physically-based lens aberration modeling using polynomial optics
- 🌈 Chromatic aberration support with RGB wavelength sampling
- ✨ **Bidirectional filtering** for realistic bokeh with preserved highlights (real-time and post-process)
- 📚 **Lens database system** with automatic lens loading
- 🎨 **Custom aperture textures** for unique bokeh shapes (hearts, stars, logos, etc.)
- 🎥 Real-world lens models based on patent data
- 🔧 **Houdini Digital Asset (HDA)** for easy setup
- 💫 Customizable aperture shapes (circular and polygonal bokeh)
- ⚡ Integration with Karma XPU (GPU) and CPU renderers
- 🚀 VEX-based implementation for performance
- 🐍 Python tools for advanced workflows and batch processing

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

### Using the Plugin

After installation, find the **karmalentil** shelf in Houdini:

**Quick Start**:
1. Click **"Lentil Camera"** shelf tool
2. A complete LOP network is created with camera, scene, and Karma settings
3. Adjust parameters in camera's "Lentil Lens" tab
4. View real-time effects in Karma viewport (Solaris)
5. Render!

**Shelf Tools**:
- 📷 **Lentil Camera** - Create complete setup
- 🎨 **Apply Bidirectional Filter** - Post-process renders
- 📦 **Import Lens** - Add lenses from lentil repository
- ❓ **Help** - Documentation and support

### Manual Setup (Advanced)

You can also set up lentil manually in LOPs:

1. Create a LOP network at `/stage`
2. Add a Camera LOP node
3. Run the Python setup script in Houdini's Python Shell:
   ```python
   import sys
   sys.path.append('/path/to/karmalentil/python')
   import setup_lentil_lops
   lop_network, camera = setup_lentil_lops.main()
   ```
4. Adjust camera parameters in the "Lentil Lens" tab
5. Render with Karma

### Bidirectional Filtering (Advanced Bokeh)

For more realistic bokeh with preserved highlights:

1. Render scene with Karma (includes depth output)
2. Apply bidirectional filter:
   ```bash
   python python/bidirectional_filter.py \
       render/scene.exr render/scene_filtered.exr \
       --focus 1000 --fstop 2.8 --focal-length 50
   ```

See [BIDIRECTIONAL.md](BIDIRECTIONAL.md) for complete documentation.

## Lens Models

Currently included sample lenses:
- Double Gauss 50mm f/2.8
- (More lenses coming soon)

## Technical Details

KarmaLentil uses sparse high-degree polynomials (degree 9-15) to model lens aberrations:
- Input: sensor position (x, y), aperture direction (dx, dy), wavelength (λ)
- Output: outer pupil position and direction with transmittance
- Evaluated in VEX for each camera ray in Karma

## Documentation

- **[PLUGIN_INSTALLATION.md](PLUGIN_INSTALLATION.md)** - 🆕 Easy plugin installation guide
- **[VIEWPORT_INTEGRATION.md](VIEWPORT_INTEGRATION.md)** - Real-time viewport setup and usage
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute tutorial
- **[USAGE.md](USAGE.md)** - Complete parameter reference
- **[BIDIRECTIONAL.md](BIDIRECTIONAL.md)** - Bidirectional filtering guide
- **[INSTALL.md](INSTALL.md)** - Advanced installation options
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute

## New in This Version

### LOPs/Solaris Architecture
- 🎯 **Native USD integration** - Built for Karma's Solaris workflow
- 🎬 **LOP network creation** - Complete stage setup with one click
- ⚡ **Karma-optimized** - Works with both Karma XPU (GPU) and CPU

### Viewport Integration
- ✨ **Real-time preview** in Karma viewport with all lens effects
- 🎯 **Interactive parameter adjustment** with immediate visual feedback
- ⚡ **GPU-accelerated** rendering with Karma XPU
- 🎨 **Live bidirectional filtering** for accurate bokeh in viewport

### Complete System
- 📦 **One-click setup** - Creates complete LOP network with camera, lights, and render settings
- 📚 **Lens database** - Automatic loading of all available lenses
- 🎨 **Aperture textures** - Custom bokeh shapes (hearts, stars, logos)
- 🐍 **Python automation** - Complete setup and batch processing scripts
- 📊 **AOV outputs** - CoC, sensor position, wavelength for advanced workflows

### No Post-Processing Required
Bidirectional filtering now works **in real-time during rendering** (with optional high-quality post-process for finals)!

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
