# KarmaLentil

Polynomial optics for Houdini Karma - realistic lens aberrations and bokeh effects.

Port of [lentil](https://github.com/zpelgrims/lentil) from Arnold to Houdini Karma.

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

### Quick Start

1. Set `HOUDINI_PATH` to include this repository:
   ```bash
   export HOUDINI_PATH="/path/to/karmalentil:&"
   ```

2. Launch Houdini 20.5+

3. Run the complete setup script in Python Shell:
   ```python
   import sys
   sys.path.append('$KARMALENTIL/python')
   import setup_complete_lentil
   setup_complete_lentil.main()
   ```

This creates a complete scene with lentil camera, Karma ROP, example geometry, and configures your viewport for real-time preview!

## Usage

### Basic Rendering

1. Create a Karma camera in your scene
2. In the camera parameters, navigate to the "Lentil" tab
3. Select a lens model from the dropdown
4. Adjust focus distance and f-stop
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

- **[VIEWPORT_INTEGRATION.md](VIEWPORT_INTEGRATION.md)** - 🆕 Real-time viewport setup and usage
- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[INSTALL.md](INSTALL.md)** - Detailed installation instructions
- **[USAGE.md](USAGE.md)** - Complete parameter reference
- **[BIDIRECTIONAL.md](BIDIRECTIONAL.md)** - Bidirectional filtering guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - How to contribute

## New in This Version

### Viewport Integration
- ✨ **Real-time preview** in Karma viewport with all lens effects
- 🎯 **Interactive parameter adjustment** with immediate visual feedback
- ⚡ **GPU-accelerated** rendering with Karma XPU
- 🎨 **Live bidirectional filtering** for accurate bokeh in viewport

### Complete System
- 📦 **HDA-based camera** - One-click setup with all parameters
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
