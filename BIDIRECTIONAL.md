# Bidirectional Filtering in KarmaLentil

## Overview

Bidirectional filtering is an advanced rendering technique that creates more accurate bokeh effects, especially for out-of-focus highlights. Instead of just blurring pixels uniformly, it redistributes samples based on their circle of confusion (CoC), creating the characteristic "bokeh balls" seen in real camera lenses.

## How It Works

### Traditional Forward Rendering

1. Generate camera ray for each pixel
2. Trace through scene
3. Shade the hit point
4. Return color to pixel

**Problem**: Out-of-focus bright spots get averaged with surrounding pixels, creating washed-out bokeh.

### Bidirectional Filtering

1. Generate camera ray for each pixel
2. Trace through scene and shade
3. **Trace backward** from hit point through lens to sensor
4. Compute circle of confusion (CoC) based on depth
5. **Redistribute** the sample to multiple pixels based on CoC
6. Bright out-of-focus points spread to create bokeh shapes

**Result**: Realistic bokeh with preserved highlight intensity.

## Implementation in KarmaLentil

KarmaLentil implements bidirectional filtering in two stages:

### Stage 1: Render with Depth

Karma renders the scene normally, outputting:
- **Beauty (Cf)**: RGB color
- **Depth (P.z)**: Camera-space depth for CoC calculation
- *Optional*: Position, Normal for advanced filtering

### Stage 2: Post-Process Redistribution

A post-process filter redistributes samples based on CoC:

**Method A: Python Script** (Recommended)
- Reads EXR with color and depth
- Computes CoC for each pixel
- Redistributes samples with Gaussian weights
- Boosts bright out-of-focus areas for bokeh
- Outputs filtered EXR

**Method B: COP Network**
- Real-time interactive filtering in Houdini
- Depth-dependent blur approximation
- Good for previews, less accurate than Python method

**Method C: VEX Filter** (Advanced)
- Custom VEX operator for COPs or Karma
- Highest quality, most flexible
- Requires VEX programming

## Setup Instructions

### Quick Setup

Run the Python setup script in Houdini:

```python
import sys
sys.path.append('/path/to/karmalentil/examples')
import setup_bidirectional_render
setup_bidirectional_render.create_bidirectional_example_scene()
```

This creates:
- Camera with lentil parameters
- Karma ROP with depth output
- COP network for post-processing

### Manual Setup

#### 1. Configure Camera

Set up a lentil camera with parameters optimized for visible bokeh:

```
focal_length = 50.0 or 85.0  (longer = stronger bokeh)
fstop = 1.4 to 2.8  (wide aperture)
focus_distance = 1000-5000  (depends on scene)
chromatic_aberration = 1.0
bokeh_blades = 6 or 7  (hexagonal/heptagonal)
```

#### 2. Configure Karma ROP

In your Karma render node:

- **Enable Depth Output**: Karma automatically includes P.z AOV
- **Set High Sample Count**: 32x32 (1024 samples) or higher
- **Output Format**: EXR with depth
- **Deep Output** (Optional): For advanced compositing

Example render settings:
```
picture = $HIP/render/$HIPNAME.$F4.exr
pixelsamples = 1024  # 32x32
```

#### 3. Render

Render your scene. Output will include:
- `render/scene.0001.exr` with beauty and depth

#### 4. Apply Bidirectional Filter

**Using Python Script**:

```bash
cd /path/to/karmalentil
python python/bidirectional_filter.py \
    render/scene.0001.exr \
    render/scene_filtered.0001.exr \
    --focus 5000 \
    --fstop 2.8 \
    --focal-length 50 \
    --bokeh-intensity 1.5
```

**Using COP Network**:

1. Open the COP network created by setup script
2. Load rendered EXR in File node
3. Adjust lentil parameters
4. View filtered result
5. Render out final frames

## Parameters

### Bidirectional Filter Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `focus` | Focus distance in mm | 1000.0 | 1-100000 |
| `focal-length` | Lens focal length in mm | 50.0 | 14-200 |
| `fstop` | Aperture f-stop | 2.8 | 0.5-22 |
| `sensor-width` | Sensor width in mm | 36.0 | 12-100 |
| `bokeh-intensity` | Highlight boost factor | 1.0 | 0.0-3.0 |

### Bokeh Intensity

Controls how much bright out-of-focus areas are boosted:

- **0.0**: No boost (linear redistribution)
- **1.0**: Realistic bokeh with moderate highlights
- **1.5-2.0**: Stylized bokeh with prominent highlights
- **>2.0**: Exaggerated bokeh (artistic effect)

Higher values create more prominent "bokeh balls" but may look unrealistic.

## Comparison: With vs Without Bidirectional Filtering

### Without Bidirectional (Standard Forward Rendering)

```
Camera → Scene → Pixel
```

**Bokeh characteristics**:
- Soft, diffuse out-of-focus areas
- Highlights blend with surroundings
- Even blur distribution
- Faster render

**Use when**:
- Subtle DOF is sufficient
- Performance is critical
- No bright out-of-focus highlights

### With Bidirectional Filtering

```
Camera → Scene → CoC Computation → Sample Redistribution → Pixel
```

**Bokeh characteristics**:
- Distinct bokeh shapes (hexagons, circles)
- Bright highlights preserved and spread
- Realistic lens behavior
- Characteristic "bokeh balls"

**Use when**:
- Prominent bokeh is desired
- Out-of-focus highlights are important
- Realistic camera look is needed
- Rendering portraits, macro, product shots

## Performance Considerations

### Render Time

- **Forward rendering**: Base time
- **Bidirectional post-process**: +5-15% (depends on CoC size)

The post-process is relatively fast since it operates on rendered images.

### Memory

Bidirectional filtering requires:
- Beauty image (3 channels × float32)
- Depth image (1 channel × float32)
- Working buffer (3 channels × float32)

For 1920×1080: ~24 MB per frame

### Optimization Tips

1. **Render at lower resolution**: Upscale beauty, use full-res depth
2. **Reduce bokeh intensity**: Lower values = faster processing
3. **Limit CoC radius**: Clamp maximum blur radius
4. **Use GPU acceleration**: NumPy operations are vectorized

## Advanced Techniques

### Chromatic Aberration + Bidirectional

For maximum realism, combine both:

1. Render with `chromatic_aberration = 1.0`
2. Apply bidirectional filter per-channel
3. Result: Colored bokeh fringing

### Deep Compositing

For multi-layer scenes:

1. Render deep images from Karma
2. Apply bidirectional filter per depth layer
3. Composite with depth-aware blending
4. Result: Correct bokeh occlusion

### Aperture Textures

Custom bokeh shapes:

1. Render with `bokeh_blades = 0` (circular)
2. In post-process, apply custom kernel shape
3. Result: Heart-shaped, star-shaped, custom bokeh

## Troubleshooting

### Issue: No visible bokeh effect

**Causes**:
- F-stop too high (stopped down)
- Focus distance same as object distance
- CoC radius below pixel size

**Solutions**:
- Set fstop to 2.8 or lower
- Adjust focus distance to create depth separation
- Use longer focal length (85mm+)
- Increase `bokeh-intensity` parameter

### Issue: Bokeh too strong/unrealistic

**Causes**:
- `bokeh-intensity` too high
- F-stop too low
- Incorrect depth values

**Solutions**:
- Reduce `bokeh-intensity` to 1.0 or less
- Increase fstop to 2.0-2.8 range
- Verify depth AOV is correct (check units)

### Issue: Blocky/pixelated bokeh

**Causes**:
- Insufficient pixel samples in render
- Filter radius too small
- Depth quantization

**Solutions**:
- Increase Karma pixel samples to 32×32 or higher
- Check depth AOV for precision issues
- Render at higher resolution

### Issue: Slow post-processing

**Causes**:
- Large CoC radius (many pixels affected)
- High resolution images
- Complex redistribution

**Solutions**:
- Use Python script with NumPy (optimized)
- Process in batches for sequences
- Consider GPU-accelerated implementation

## Technical Details

### Circle of Confusion Formula

```
CoC = (A × |S₂ - S₁|) / (S₂ × N)
```

Where:
- `A` = Aperture diameter = focal_length / fstop
- `S₁` = Focus distance
- `S₂` = Object distance (from depth buffer)
- `N` = F-stop number

### Gaussian Weight Function

```
weight(r) = exp(-r² / (2σ²))
```

Where:
- `r` = Distance from pixel center
- `σ` = CoC radius / 2 (standard deviation)

### Sample Redistribution

For each pixel with CoC radius R:
1. Determine affected pixels within radius R
2. Compute Gaussian weight for each
3. Distribute pixel color weighted by Gaussian
4. Accumulate in output buffer
5. Normalize by total weight

## Examples

### Example 1: Portrait with Bokeh

**Render settings**:
```python
focal_length = 85.0
fstop = 1.8
focus_distance = 2000.0  # 2 meters to subject
bokeh_blades = 7
chromatic_aberration = 0.8
```

**Post-process**:
```bash
python bidirectional_filter.py \
    portrait.exr portrait_filtered.exr \
    --focus 2000 --fstop 1.8 --focal-length 85 \
    --bokeh-intensity 1.2
```

**Result**: Smooth bokeh background with distinct heptagonal highlights.

### Example 2: Macro Photography

**Render settings**:
```python
focal_length = 100.0
fstop = 2.8
focus_distance = 300.0  # 30cm (very close)
bokeh_blades = 9
chromatic_aberration = 1.0
```

**Post-process**:
```bash
python bidirectional_filter.py \
    macro.exr macro_filtered.exr \
    --focus 300 --fstop 2.8 --focal-length 100 \
    --bokeh-intensity 1.5
```

**Result**: Extreme shallow DOF with creamy bokeh.

### Example 3: Architectural (Minimal Bokeh)

**Render settings**:
```python
focal_length = 24.0
fstop = 8.0
focus_distance = 5000.0
bokeh_blades = 0
chromatic_aberration = 0.5
```

**Post-process**:
```bash
python bidirectional_filter.py \
    arch.exr arch_filtered.exr \
    --focus 5000 --fstop 8.0 --focal-length 24 \
    --bokeh-intensity 0.5
```

**Result**: Deep DOF with subtle lens character.

## References

- Original lentil implementation: https://github.com/zpelgrims/lentil
- "Polynomial Optics" paper (Hullin et al.)
- "Stochastic Rasterization" (McGuire et al.) - bidirectional filtering concepts

## Future Enhancements

Planned features for bidirectional filtering:

1. **GPU acceleration**: CUDA/OpenCL for real-time filtering
2. **Karma integration**: Native Karma filter node
3. **Deep image support**: Multi-layer bokeh with proper occlusion
4. **Animated bokeh**: Motion blur + bokeh interaction
5. **HDR bokeh**: Proper handling of HDR highlights
6. **Aperture textures**: Custom bokeh shape from images

## Contributing

See CONTRIBUTING.md for information on improving the bidirectional filtering system.
