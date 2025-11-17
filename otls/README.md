# KarmaLentil HDAs

This directory contains Houdini Digital Assets (HDAs) for KarmaLentil.

## Building the HDA

To build/rebuild the KarmaLentil Camera HDA:

```python
# In Houdini Python Shell
import sys
sys.path.append('/path/to/karmalentil/python')
import create_lentil_camera_hda
create_lentil_camera_hda.create_lentil_camera_hda()
```

This will create `karmalentil_camera.hda` in this directory.

## Using the HDA

Once the HDA is built and Houdini is restarted (or the HDA is installed):

1. Create a LOP network
2. Press **TAB** inside the network
3. Search for **"karmalentil"** or **"lentil camera"**
4. Place the camera node
5. Adjust parameters in the "Lentil Lens" tab
6. Render with Karma!

## HDA Contents

The HDA includes:
- Complete camera with standard parameters
- Lentil Lens tab with all aberration controls
- Lens model selection
- Chromatic aberration
- Custom bokeh shapes
- Bidirectional filtering controls
- Help documentation

## Automatic Loading

The package configuration automatically adds this directory to `HOUDINI_OTLSCAN_PATH`, so any `.hda` or `.otl` files here will be loaded when Houdini starts.
