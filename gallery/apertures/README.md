# Aperture Texture Gallery

Custom bokeh shapes for lentil camera.

## Usage

Set the `aperture_texture` parameter on the lentil camera to one of these textures:

```
$KARMALENTIL/gallery/apertures/hexagon.png
$KARMALENTIL/gallery/apertures/heart.png
$KARMALENTIL/gallery/apertures/star.png
```

## Creating Your Own

**Requirements**:
- Square image (512×512 or 1024×1024 recommended)
- Black background (#000000)
- White/gray aperture shape
- Supported formats: PNG, JPG, TIFF, EXR

**Process**:
1. Create image in your favorite editor (Photoshop, GIMP, etc.)
2. Draw white shape on black background
3. Save as PNG or EXR
4. Reference in lentil camera

**Tips**:
- Smooth edges for soft bokeh
- Hard edges for defined shapes
- Grayscale values = partial transparency
- Center the shape for best results

## Available Textures

### hexagon.png
Classic hexagonal bokeh (7-blade aperture simulation)

### pentagon.png
5-pointed star effect

### heart.png
Romantic heart-shaped bokeh

### star.png
Star-burst effect

### cat.png
Fun cat silhouette bokeh

### circular.png
Smooth circular aperture (reference)

## Examples

See `examples/aperture_texture_demo.hip` for demonstration.

## Contributing

To add textures to the gallery:
1. Create your texture
2. Test with lentil camera
3. Add to this directory
4. Update this README
5. Submit pull request
