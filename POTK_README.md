# POTK - Polynomial Optics to Karma

## What is POTK?

POTK (Polynomial Optics to Karma) is a proper, research-based implementation of polynomial lens modeling for Houdini's Karma renderer. It integrates the original **polynomial-optics** C++ library from the lentil project, providing the same mathematical rigor and optical accuracy as POTA (Polynomial Optics to Arnold).

## Why Build POTK Properly?

The current simplified implementation works for rendering with pre-calculated lens data, but lacks:

1. **Lens Creation** - Can't import new lens designs or fit polynomials
2. **Validation** - No way to verify optical accuracy
3. **Advanced Features** - Missing anamorphic, aspherical, proper vignetting
4. **Research Capabilities** - Can't experiment with custom optical designs

A proper POTK implementation provides:

✅ **Patent Import** - Read lens designs from optical patents
✅ **Polynomial Fitting** - Fit high-degree polynomials to optical systems
✅ **Validation** - Raytracing comparison and RMS error measurement
✅ **Code Generation** - Auto-generate optimized VEX shaders per lens
✅ **Anamorphic Support** - Full cylindrical projection
✅ **Aspherical Elements** - Non-spherical lens surfaces
✅ **Vignetting** - Proper lens housing simulation
✅ **Professional Quality** - Research-grade optical accuracy

## Architecture Comparison

### Current Simplified System
```
JSON files (manually created)
    ↓
Python loader
    ↓
Generic VEX shader
    ↓
Karma rendering
```

**Limitations:**
- Fixed lens database
- No validation
- Simplified optics
- Manual lens creation

### Proper POTK System
```
Lens patents/designs
    ↓
polynomial-optics (C++ library)
    ├── Import optical design
    ├── Fit polynomials
    ├── Validate with raytracing
    └── Generate optimized VEX
    ↓
Per-lens VEX shaders
    ↓
Karma rendering (optimal performance)
```

**Benefits:**
- Automated workflow
- Validated accuracy
- Full optical features
- Easy lens creation

## Implementation Status

### Phase 1: Library Integration (In Progress)
- [x] Implementation plan created
- [ ] Clone polynomial-optics library
- [ ] Set up build system (CMake)
- [ ] Python bindings (pybind11)
- [ ] Basic functionality test

### Phase 2: Lens Database & Import (Planned)
- [ ] Patent import system
- [ ] Lens database management
- [ ] Polynomial fitting interface
- [ ] Validation tools
- [ ] Houdini HDA tools

### Phase 3: VEX Code Generation (Planned)
- [ ] VEX code generator
- [ ] Per-lens optimization
- [ ] Template-based generation
- [ ] Coefficient embedding

### Phase 4: Houdini Integration (Planned)
- [ ] HDK plugin (optional)
- [ ] Python shelf tools
- [ ] Camera parameter UI
- [ ] Real-time updates

### Phase 5: Advanced Features (Planned)
- [ ] Anamorphic lens support
- [ ] Lens housing/vignetting
- [ ] Aspherical elements
- [ ] Chromatic aberration (wavelength-dependent)
- [ ] Bokeh AOV outputs

## Technical Stack

**C++ Libraries:**
- polynomial-optics (core algorithms)
- Eigen (linear algebra)
- pybind11 (Python bindings)

**Build Tools:**
- CMake (cross-platform build)
- C++11 compiler
- Python 3.7+ (Houdini bundled)

**Houdini Integration:**
- Python API (hou module)
- VEX (shader language)
- HDK (optional, for performance)

## Workflow Example

```python
# 1. Import lens design from patent
from potk import LensImporter
lens = LensImporter.from_patent('1927-zeiss-biotar')

# 2. Fit polynomials
from potk import PolyFitter
fitter = PolyFitter(degree=7)
coeffs = fitter.fit(lens, samples=10000)

# 3. Validate accuracy
error = fitter.validate(lens, coeffs)
print(f"RMS error: {error}mm")

# 4. Generate optimized VEX shader
from potk import VEXGenerator
shader = VEXGenerator.generate(lens, coeffs)

# 5. Save to database
lens.save('database/fitted/zeiss_biotar_1927.lens')
shader.save('vex/generated/zeiss_biotar_1927.vfl')

# 6. Use in Houdini
# Select lens in camera parameter
# Render with Karma CPU
```

## File Structure

```
karmalentil/
├── ext/
│   └── lentil/                   # Original lentil repository
│       └── polynomial-optics/    # C++ library (the brain)
├── src/
│   ├── python_bindings.cpp       # Python → C++ bridge
│   └── vex_generator.cpp         # VEX code generator
├── python/
│   └── potk/                     # Python API
│       ├── __init__.py
│       ├── lens_importer.py      # Import lens designs
│       ├── poly_fitter.py        # Fit polynomials
│       └── vex_generator.py      # Generate VEX
├── tools/
│   ├── import_patent.py          # CLI tool: import
│   ├── fit_lens.py               # CLI tool: fit
│   └── generate_shader.py        # CLI tool: generate
├── vex/
│   ├── templates/                # VEX templates
│   └── generated/                # Generated shaders
├── database/
│   ├── optical_designs/          # Raw lens designs
│   ├── fitted/                   # Fitted data
│   └── validation/               # Validation reports
└── hda/
    ├── LensImporter.hda          # Houdini tool
    └── LensFitter.hda            # Houdini tool
```

## Benefits Over Current System

| Feature | Current | POTK | Improvement |
|---------|---------|------|-------------|
| **Create New Lenses** | ❌ Manual | ✅ Automated | Workflow |
| **Validate Accuracy** | ❌ Unknown | ✅ Measured | Quality |
| **Anamorphic** | ❌ No | ✅ Yes | Features |
| **Aspherical** | ❌ No | ✅ Yes | Features |
| **Vignetting** | ❌ No | ✅ Yes | Realism |
| **VEX Performance** | ⚠️ Generic | ✅ Optimized | Speed |
| **Optical Accuracy** | ⚠️ Approximate | ✅ Validated | Quality |

## Timeline

**Estimated Development Time:**
- Phase 1 (Integration): 2-3 days
- Phase 2 (Import/Fit): 3-4 days
- Phase 3 (VEX Gen): 2-3 days
- Phase 4 (Houdini): 2-3 days
- Phase 5 (Advanced): 3-5 days

**Total: 2-3 weeks** for complete professional-grade system

## Migration from Current System

Existing scenes will continue to work. New features:
1. Import custom lenses from patents
2. Validate lens accuracy
3. Generate optimized shaders
4. Access advanced optical features

## References

- **Original Research:** "Sparse high-degree polynomials for wide-angle lenses"
- **POTA (Arnold):** https://github.com/zpelgrims/pota
- **Polynomial-optics:** https://github.com/zpelgrims/lentil/tree/dev/polynomial-optics
- **Author:** Zeno Pelgrims

## License

Following the original lentil project:
- MIT License
- Copyright (c) 2023 Zeno Pelgrims

## Status

🚧 **In Active Development** 🚧

Currently integrating the polynomial-optics library.
See `POTK_IMPLEMENTATION_PLAN.md` for detailed roadmap.
