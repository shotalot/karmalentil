# Usage Guide for KarmaLentil

## Basic Workflow

### 1. Setting Up a Lentil Camera

**Option A: Manual VEX Integration** (Current Implementation)

1. Create a Karma camera (`/obj/cam1`)

2. Navigate to the camera's shop network or create a SHOP network

3. Create a VEX operator or Camera VOP that references the lentil shader

4. Set up the shader parameters:
   ```
   enable_lentil = 1
   lens_model = "double_gauss_50mm"
   focal_length = 50.0
   fstop = 2.8
   focus_distance = 1000.0
   sensor_width = 36.0
   chromatic_aberration = 1.0
   bokeh_blades = 6
   bokeh_rotation = 0.0
   ```

5. Assign the shader to your camera

**Option B: Using Python/HScript** (For automation)

```python
import hou

# Create camera
cam = hou.node('/obj').createNode('cam', 'lentil_camera')

# Add lentil parameters
parm_template_group = cam.parmTemplateGroup()
parm_folder = hou.FolderParmTemplate('lentil', 'Lentil Lens')

# Add parameters
parm_folder.addParmTemplate(hou.ToggleParmTemplate('enable_lentil', 'Enable Lentil', default_value=1))
parm_folder.addParmTemplate(hou.StringParmTemplate('lens_model', 'Lens Model', 1, default_value=['double_gauss_50mm']))
parm_folder.addParmTemplate(hou.FloatParmTemplate('lentil_focal_length', 'Focal Length (mm)', 1, default_value=[50.0]))
parm_folder.addParmTemplate(hou.FloatParmTemplate('lentil_fstop', 'F-Stop', 1, default_value=[2.8], min=0.0, max=22.0))
parm_folder.addParmTemplate(hou.FloatParmTemplate('lentil_focus', 'Focus Distance', 1, default_value=[1000.0], min=0.1))
parm_folder.addParmTemplate(hou.FloatParmTemplate('lentil_sensor_width', 'Sensor Width (mm)', 1, default_value=[36.0]))
parm_folder.addParmTemplate(hou.FloatParmTemplate('lentil_chromatic_aberration', 'Chromatic Aberration', 1, default_value=[1.0], min=0.0, max=2.0))
parm_folder.addParmTemplate(hou.IntParmTemplate('lentil_bokeh_blades', 'Bokeh Blades', 1, default_value=[0], min=0, max=16))
parm_folder.addParmTemplate(hou.FloatParmTemplate('lentil_bokeh_rotation', 'Bokeh Rotation', 1, default_value=[0.0]))

parm_template_group.append(parm_folder)
cam.setParmTemplateGroup(parm_template_group)

print(f"Created lentil camera: {cam.path()}")
```

### 2. Configuring Lens Parameters

#### Focal Length
- **Purpose**: Sets the lens focal length in millimeters
- **Range**: Typically 14mm (ultra-wide) to 200mm (telephoto)
- **Default**: 50mm (standard lens)
- **Notes**: Must match the lens model's designed focal length for accurate results

#### F-Stop
- **Purpose**: Controls aperture size (depth of field and bokeh)
- **Range**: 0.0 (wide open) to 22.0 (stopped down)
- **Default**: 2.8
- **Notes**:
  - 0.0 uses the lens's minimum f-stop (widest aperture)
  - Smaller numbers = shallower depth of field, more bokeh
  - Larger numbers = deeper depth of field, less bokeh

#### Focus Distance
- **Purpose**: Distance to the focus plane
- **Range**: 0.1mm to infinity
- **Default**: 1000mm (1 meter)
- **Units**: Millimeters
- **Notes**: Objects at this distance will be in sharp focus

#### Sensor Width
- **Purpose**: Physical sensor width
- **Range**: Typically 12mm (small sensor) to 36mm (full frame)
- **Default**: 36mm (full frame 35mm sensor)
- **Common values**:
  - Super 35: 24.89mm
  - APS-C: 23.6mm
  - Full Frame: 36mm
  - Medium Format: 53.7mm

#### Chromatic Aberration
- **Purpose**: Strength of chromatic aberration effect
- **Range**: 0.0 (disabled) to 2.0 (exaggerated)
- **Default**: 1.0 (realistic)
- **Notes**:
  - 0.0 = monochromatic rendering (faster, no CA)
  - 1.0 = physically accurate chromatic aberration
  - >1.0 = artistic/exaggerated effect
  - Disabling saves ~66% render time (single wavelength vs RGB)

#### Bokeh Blades
- **Purpose**: Number of aperture blades (affects bokeh shape)
- **Range**: 0-16
- **Default**: 0 (circular aperture)
- **Notes**:
  - 0-3: Circular bokeh
  - 4+: Polygonal bokeh (4=square, 5=pentagon, 6=hexagon, etc.)
  - More blades = rounder bokeh
  - Common values: 5-9 blades

#### Bokeh Rotation
- **Purpose**: Rotation angle of aperture blades
- **Range**: 0.0 to 2π radians
- **Default**: 0.0
- **Notes**: Only affects polygonal bokeh (blade count ≥ 4)

## Advanced Usage

### Depth of Field and Bokeh

To achieve pronounced depth of field effects:

1. **Use a wide aperture** (low f-stop): 1.4, 2.0, 2.8
2. **Get close to subject**: Reduce focus distance
3. **Increase background separation**: Position subject far from background
4. **Use longer focal length**: 85mm, 135mm for stronger compression

Example settings for portrait with bokeh:
```
focal_length = 85.0
fstop = 1.8
focus_distance = 1500.0  # 1.5m to subject
bokeh_blades = 7
chromatic_aberration = 0.8
```

### Chromatic Aberration Control

Chromatic aberration appears as color fringing, especially:
- At high-contrast edges
- Towards frame edges
- In out-of-focus areas

To emphasize CA for artistic effect:
```
chromatic_aberration = 1.5  # Exaggerated
focal_length = 24.0  # Wide angle shows more CA
fstop = 2.0  # Wide aperture
```

To minimize CA:
```
chromatic_aberration = 0.0  # Disabled
fstop = 8.0  # Stopped down (less aberration)
```

### Custom Bokeh Shapes

Create unique bokeh patterns:

**Hexagonal Bokeh** (common in modern lenses):
```
bokeh_blades = 6
bokeh_rotation = 0.0
```

**Star-like Bokeh**:
```
bokeh_blades = 5
bokeh_rotation = 0.0
```

**Anamorphic-style Bokeh** (requires custom implementation):
```
bokeh_blades = 0  # Circular
# Add bokeh_squeeze parameter (not in base implementation)
```

## Bidirectional Filtering

Bidirectional filtering creates more realistic bokeh by redistributing samples based on their circle of confusion. This is especially important for out-of-focus highlights.

### When to Use Bidirectional Filtering

**Use bidirectional filtering when**:
- You have prominent out-of-focus highlights (bokeh balls)
- Rendering portraits, macro, or product shots
- Realistic camera look is critical
- Depth of field is a key visual element

**Skip bidirectional filtering when**:
- Subtle DOF is sufficient
- No bright out-of-focus elements
- Performance is critical
- Quick preview renders

### Workflow

#### 1. Render with Karma

Render normally with lentil camera. Karma automatically outputs depth (P.z AOV):

```python
# In Karma ROP settings
picture = $HIP/render/scene.$F4.exr
pixelsamples = 1024  # 32x32 for smooth bokeh
```

#### 2. Apply Bidirectional Filter

Use the Python post-process tool:

```bash
python python/bidirectional_filter.py \
    render/scene.0001.exr \
    render/scene_filtered.0001.exr \
    --focus 1000 \
    --fstop 2.8 \
    --focal-length 50 \
    --bokeh-intensity 1.0
```

**Parameters**:
- `--focus`: Focus distance in mm (must match camera setting)
- `--fstop`: F-stop (must match camera setting)
- `--focal-length`: Focal length in mm
- `--bokeh-intensity`: Highlight boost (0.0-3.0, default 1.0)
- `--sensor-width`: Sensor width in mm (default 36.0)

#### 3. Compare Results

**Without bidirectional**: Soft, diffuse bokeh, highlights blend with surroundings
**With bidirectional**: Distinct bokeh shapes, bright highlights preserved, "bokeh balls"

### Bokeh Intensity Parameter

Controls how much bright out-of-focus areas are emphasized:

- **0.0**: Linear redistribution (no boost)
- **1.0**: Realistic bokeh (recommended)
- **1.5**: Prominent bokeh highlights
- **2.0+**: Stylized/exaggerated effect

Higher values create more dramatic bokeh but may look unrealistic.

### Batch Processing

For animation sequences:

```bash
# Process frame range
for i in {1..100}; do
    python python/bidirectional_filter.py \
        render/scene.$(printf "%04d" $i).exr \
        render/scene_filtered.$(printf "%04d" $i).exr \
        --focus 1000 --fstop 2.8 --focal-length 50
done
```

### Interactive Preview (COP Network)

For interactive adjustment:

```python
# In Houdini Python shell
import setup_bidirectional_render
setup_bidirectional_render.setup_cop_network_for_bidirectional()
```

Then adjust parameters in the COP network to see results in real-time.

### Technical Notes

- Post-processing adds ~5-15% to total render time
- Memory usage: ~24MB per 1920×1080 frame
- Requires NumPy for optimal performance
- Can be parallelized for multi-frame processing

See [BIDIRECTIONAL.md](BIDIRECTIONAL.md) for complete technical documentation.

## Render Settings

### Karma Pixel Samples

Polynomial optics requires adequate sampling for smooth bokeh:

- **Minimum**: 16x16 samples (256 samples per pixel)
- **Recommended**: 32x32 samples (1024 samples per pixel)
- **High Quality**: 64x64 samples (4096 samples per pixel)

Lower samples will show noise in out-of-focus areas.

### Performance Tips

**For faster test renders**:
```
chromatic_aberration = 0.0  # 3x speedup (single wavelength)
bokeh_blades = 0  # Slightly faster than polygonal
# Reduce Karma pixel samples to 8x8
```

**For final quality renders**:
```
chromatic_aberration = 1.0  # Full CA
# Increase Karma pixel samples to 32x32 or higher
# Enable denoising in Karma
```

### Memory Considerations

Polynomial evaluation is computationally intensive but memory-light. Each ray requires:
- ~100-500 floating point operations (depending on polynomial degree)
- Minimal memory overhead

GPU rendering (Karma XPU) is recommended for complex scenes.

## Troubleshooting

### Issue: No visible depth of field

**Solutions**:
- Check that `enable_lentil = 1`
- Verify f-stop is < 8.0 (wide aperture)
- Ensure focus distance is set correctly
- Check that bokeh isn't too subtle (try fstop = 2.0)

### Issue: Harsh/sharp bokeh edges

**Solutions**:
- Increase Karma pixel samples (32x32 minimum)
- Enable Karma denoising
- Check that aperture samples are sufficient

### Issue: Incorrect colors/chromatic aberration

**Solutions**:
- Verify wavelength sampling is enabled
- Check that Karma is in RGB mode (not spectral)
- Adjust chromatic_aberration parameter (try 0.5-1.5 range)

### Issue: Slow render performance

**Solutions**:
- Disable chromatic aberration (`chromatic_aberration = 0`)
- Use Karma XPU (GPU) instead of CPU
- Reduce pixel samples for test renders
- Simplify polynomial (use fewer terms in pt_evaluate.h)

### Issue: VEX compilation errors

**Solutions**:
- Check that all include paths are correct
- Verify lens data files exist
- Review VEX syntax (ensure C code was properly converted)
- Check for missing `lens_ipow()` function definition

## Examples

### Example 1: Cinematic Portrait

```
lens_model = "double_gauss_50mm"
focal_length = 85.0
fstop = 1.4
focus_distance = 2000.0
sensor_width = 36.0
chromatic_aberration = 0.5
bokeh_blades = 9
bokeh_rotation = 0.0
```

### Example 2: Wide Angle Architecture

```
lens_model = "double_gauss_50mm"  # Use appropriate wide lens
focal_length = 24.0
fstop = 8.0
focus_distance = 5000.0
sensor_width = 36.0
chromatic_aberration = 1.0
bokeh_blades = 7
bokeh_rotation = 0.0
```

### Example 3: Macro Photography

```
lens_model = "double_gauss_50mm"
focal_length = 100.0
fstop = 2.8
focus_distance = 300.0  # 30cm
sensor_width = 36.0
chromatic_aberration = 1.2
bokeh_blades = 8
bokeh_rotation = 0.0
```

### Example 4: Fast Test Render

```
enable_lentil = 1
lens_model = "double_gauss_50mm"
focal_length = 50.0
fstop = 5.6
focus_distance = 1000.0
sensor_width = 36.0
chromatic_aberration = 0.0  # Disabled for speed
bokeh_blades = 0
```

## Comparison with Standard Karma DOF

| Feature | Standard Karma DOF | KarmaLentil |
|---------|-------------------|-------------|
| Depth of Field | ✓ | ✓ |
| Bokeh Shape | Limited | Customizable (blades) |
| Chromatic Aberration | ✗ | ✓ |
| Lens Aberrations | ✗ | ✓ (spherical, coma, etc.) |
| Physically Accurate | Thin lens approximation | Polynomial optics |
| Performance | Faster | Slower (3x for CA) |
| Real Lens Models | ✗ | ✓ |

## Further Reading

- Original lentil documentation: https://github.com/zpelgrims/lentil
- Polynomial Optics paper: "Polynomial Optics" (Joo et al.)
- Lens design resources: www.lentil.xyz
- Houdini Karma documentation: SideFX Karma User Guide
