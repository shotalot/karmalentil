# Installation Guide for KarmaLentil

## Quick Installation

### 1. Set HOUDINI_PATH

Add this repository to your Houdini path:

```bash
# Linux/macOS
export HOUDINI_PATH="/path/to/karmalentil:&"

# Windows (PowerShell)
$env:HOUDINI_PATH = "C:\path\to\karmalentil;&"
```

Or add to `houdini20.5/houdini.env`:
```
HOUDINI_PATH = "/path/to/karmalentil:&"
```

### 2. Launch Houdini

```bash
houdini
```

### 3. Verify Installation

The VEX camera shader should be available at:
- `$HIP/vex/camera/lentil_camera.vfl`

## Manual Setup in Karma

Since this is a VEX-based implementation, you'll need to manually integrate the shader into your Karma camera setup:

### Method 1: Using VOP Camera (Recommended)

1. Create a Karma camera in your scene
2. Inside the camera, create a "Camera VOP" network
3. Create a "Inline Code" VOP node
4. Copy the contents of `vex/camera/lentil_camera.vfl` into the Inline Code
5. Wire up the outputs (P, I, weight) to the camera shader output

### Method 2: Using VEX Operator

1. Create a camera
2. In camera parameters, add a spare parameter folder called "Lentil"
3. Add parameters:
   - Enable Lentil (toggle)
   - Lens Model (string)
   - Focal Length (float, default 50.0)
   - F-Stop (float, default 2.8)
   - Focus Distance (float, default 1000.0)
   - Sensor Width (float, default 36.0)
   - Chromatic Aberration (float, default 1.0)
   - Bokeh Blades (integer, default 0)
   - Bokeh Rotation (float, default 0.0)

4. Create a parameter expression that includes the VEX shader

## Importing Lens Data

To import additional lens data from the original lentil repository:

### 1. Clone the lentil repository

```bash
git clone https://github.com/zpelgrims/lentil.git
cd lentil
git submodule update --init --recursive
```

### 2. Build the polynomial-optics tools (Optional)

This is only needed if you want to fit new lenses. Pre-generated lens data is available in the database.

```bash
cd polynomial-optics
./build.sh  # Linux/macOS
```

### 3. Import a lens to karmalentil

```bash
cd /path/to/karmalentil
python python/import_lens.py \
    /path/to/lentil/polynomial-optics/database/lenses/1953-angenieux-double-gauss/49mm \
    angenieux_double_gauss_49mm
```

This will create a new lens directory at `lenses/angenieux_double_gauss_49mm/` with VEX-compatible code.

### 4. Update the camera shader

Edit `vex/camera/lentil_camera.vfl` to include the new lens files:

```c
// Add at the top with other includes
#include "../../lenses/angenieux_double_gauss_49mm/lens_constants.h"
#include "../../lenses/angenieux_double_gauss_49mm/pt_evaluate.h"
```

## Troubleshooting

### VEX Compilation Errors

If you encounter VEX compilation errors:

1. Check that all include paths are correct
2. Verify that the lens data files were imported correctly
3. Look for C-specific syntax that wasn't converted to VEX:
   - `pow()` should be `lens_ipow()` for integer exponents
   - `static inline` should be `function`

### Performance Issues

If rendering is slow:

1. Disable chromatic aberration (set to 0) for 3x speedup
2. Use a simpler lens model
3. Reduce aperture samples in Karma render settings
4. Use Karma XPU for GPU acceleration

### Missing Lens Data

If lens data is missing:

1. Check that the lens files exist in `lenses/[lens_name]/`
2. Verify include paths in the VEX shader
3. Make sure `lens_constants.h`, `pt_evaluate.h` are present

## Advanced Configuration

### Creating Custom Lens Models

To create a custom lens:

1. Use the lentil polynomial-optics tools to fit your lens design
2. Run `gencode` to generate C code
3. Use `python/import_lens.py` to convert to VEX
4. Update the camera shader includes

### Optimizing Polynomial Evaluation

For better performance:

1. Reduce polynomial degree (fewer terms = faster evaluation)
2. Use SIMD operations in VEX where possible
3. Pre-compute constant terms
4. Consider baking common lens configurations

## Next Steps

- See `USAGE.md` for detailed usage instructions
- See `examples/` for sample scenes
- See original lentil documentation: https://github.com/zpelgrims/lentil
