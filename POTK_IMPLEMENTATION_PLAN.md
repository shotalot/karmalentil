# POTK - Polynomial Optics to Karma Implementation Plan

## Overview

Building a proper Karma integration that matches the original lentil/POTA architecture by integrating the polynomial-optics C++ library.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    POTK Architecture                         │
└─────────────────────────────────────────────────────────────┘

polynomial-optics (C++ library)
├── Lens database (optical designs)
├── Polynomial fitting algorithms
├── Raytracing validation
└── Code generation

         ↓

POTK Integration Layer
├── Build system (CMake)
├── Python bindings (pybind11 or similar)
├── VEX code generator
└── Houdini integration

         ↓

Karma Rendering
├── VEX lens shader (generated)
├── Karma Lens Material
└── USD camera integration
```

## Implementation Phases

### Phase 1: Library Integration ✓

**Goal:** Get polynomial-optics building and accessible from Houdini Python

**Tasks:**
1. Clone polynomial-optics as submodule
2. Set up CMake build system
3. Link against Eigen library
4. Build Python bindings with pybind11
5. Test basic functionality

**Deliverables:**
- `ext/polynomial-optics/` - C++ library
- `build/` - Build directory
- `python/polynomial_optics_wrapper.py` - Python interface

### Phase 2: Lens Database & Import Tools

**Goal:** Import lens designs and fit polynomials

**Tasks:**
1. Patent import system (read optical designs)
2. Lens database management (JSON + binary)
3. Polynomial fitting interface
4. Validation and testing tools
5. HDA for lens import workflow

**Deliverables:**
- `tools/lens_importer.py` - Patent import tool
- `tools/lens_fitter.py` - Polynomial fitting tool
- `hda/LensImporter.hda` - Houdini tool
- `database/fitted/` - Fitted lens data

### Phase 3: VEX Code Generation

**Goal:** Auto-generate optimized VEX shaders from polynomial data

**Tasks:**
1. VEX code generator (C++ or Python)
2. Per-lens optimized shaders
3. Template-based code generation
4. Coefficient embedding
5. Performance optimization

**Deliverables:**
- `tools/vex_generator.py` - Code generator
- `vex/generated/` - Generated shaders
- `vex/templates/` - VEX templates

### Phase 4: Houdini Integration

**Goal:** Seamless Houdini workflow

**Tasks:**
1. HDK plugin (if needed for performance)
2. Python shelf tools
3. Camera parameter UI
4. Real-time updates
5. Karma integration

**Deliverables:**
- `hdk/` - HDK plugin source (optional)
- `toolbar/` - Shelf tools
- `scripts/` - Python integration

### Phase 5: Advanced Features

**Goal:** Full feature parity with original

**Tasks:**
1. Anamorphic lens support
2. Lens housing/vignetting
3. Aspherical elements
4. Chromatic aberration (wavelength-dependent)
5. Bokeh AOV outputs

**Deliverables:**
- Full feature set matching POTA
- Advanced optical effects
- Production-ready quality

## Technical Details

### Dependencies

**Required:**
- Eigen (linear algebra) - header-only, easy
- CMake (build system) - standard
- Python 3.7+ (Houdini bundled)

**Optional:**
- pybind11 (Python bindings) - for C++ integration
- GTK+/Cairo (visualization) - for lens design viewer

### Build System

```cmake
# CMakeLists.txt structure
project(POTK)

# Find Houdini
find_package(Houdini REQUIRED)

# Add polynomial-optics as subdirectory
add_subdirectory(ext/polynomial-optics)

# Build Python bindings
pybind11_add_module(polynomial_optics_binding
    src/python_bindings.cpp
)

# Link against Eigen and polynomial-optics
target_link_libraries(polynomial_optics_binding
    PRIVATE polynomial_optics Eigen3::Eigen
)
```

### VEX Code Generation

**Template approach:**

```vex
// Template: vex/templates/lens_shader_template.vfl
cvex karma_lentil_lens_{LENS_NAME}(
    export vector P = 0;
    export vector I = {0, 0, -1};
    // ... standard camera shader interface
)
{
    // Embedded polynomial coefficients
    float coeffs_x[] = {COEFFS_X};
    float coeffs_y[] = {COEFFS_Y};

    // Optimized polynomial evaluation
    // (specific to lens degree and structure)

    // Generated code for this specific lens...
}
```

**Benefits:**
- Per-lens optimization
- No runtime coefficient lookup
- Smaller, faster shaders
- Better shader compilation

### Python Integration

```python
# Example usage
from polynomial_optics import LensDatabase, PolyFitter

# Import lens design from patent
lens = LensDatabase.import_patent('1927-zeiss-biotar')

# Fit polynomials
fitter = PolyFitter(degree=7)
coefficients = fitter.fit(lens, validation_samples=10000)

# Validate accuracy
error = fitter.validate(lens, coefficients)
print(f"RMS error: {error}mm")

# Generate VEX shader
from potk import VEXGenerator
gen = VEXGenerator()
shader_code = gen.generate(lens, coefficients)

# Save to disk
with open('vex/generated/zeiss_biotar_1927.vfl', 'w') as f:
    f.write(shader_code)
```

## Comparison: Current vs Proper POTK

| Feature | Current System | Proper POTK |
|---------|---------------|-------------|
| **Lens Creation** | Manual JSON editing | Import from patents/designs |
| **Polynomial Fitting** | Pre-calculated | Runtime fitting with validation |
| **Accuracy** | Unknown (no validation) | RMS error measured |
| **VEX Generation** | Generic shader | Per-lens optimized |
| **Anamorphic** | Not supported | Full cylindrical projection |
| **Aspherical** | Not supported | Full support |
| **Vignetting** | Not simulated | Proper lens housing |
| **New Lenses** | Manual work | Automated workflow |
| **Validation** | None | Raytracing comparison |

## File Structure

```
karmalentil/
├── ext/
│   └── polynomial-optics/        # Submodule
│       ├── src/
│       ├── include/
│       ├── ext/Eigen/
│       └── CMakeLists.txt
├── src/
│   ├── python_bindings.cpp       # pybind11 bindings
│   └── vex_generator.cpp         # VEX code generator
├── python/
│   ├── polynomial_optics.py      # Python wrapper
│   ├── lens_importer.py          # Lens import tools
│   └── lens_fitter.py            # Fitting interface
├── tools/
│   ├── import_patent.py          # Import lens designs
│   ├── fit_polynomials.py        # Fit and validate
│   └── generate_vex.py           # Generate VEX code
├── vex/
│   ├── templates/                # VEX templates
│   │   └── lens_shader.template.vfl
│   └── generated/                # Generated shaders
│       ├── zeiss_biotar_1927.vfl
│       └── cooke_speed_panchro_1920.vfl
├── database/
│   ├── optical_designs/          # Lens design files
│   ├── fitted/                   # Fitted polynomial data
│   └── validation/               # Validation reports
├── hda/
│   ├── LensImporter.hda          # Import tool
│   ├── LensFitter.hda            # Fitting tool
│   └── LensViewer.hda            # Visualization
├── build/                        # Build directory
│   ├── lib/
│   └── bin/
└── CMakeLists.txt               # Main build file
```

## Timeline Estimate

- **Phase 1:** 2-3 days (library integration, build system)
- **Phase 2:** 3-4 days (import tools, fitting)
- **Phase 3:** 2-3 days (VEX generation)
- **Phase 4:** 2-3 days (Houdini integration)
- **Phase 5:** 3-5 days (advanced features)

**Total:** 2-3 weeks for complete implementation

## Benefits of Proper POTK

1. **Professional Quality**
   - Validated optical accuracy
   - Industry-standard workflow
   - Production-ready

2. **Extensibility**
   - Easy to add new lenses
   - Custom lens designs
   - Research/experimentation

3. **Performance**
   - Optimized VEX per lens
   - Compile-time coefficient embedding
   - Minimal runtime overhead

4. **Maintenance**
   - Based on maintained research library
   - Bug fixes upstream
   - Community contributions

5. **Feature Complete**
   - Anamorphic support
   - Aspherical elements
   - Vignetting simulation
   - Full chromatic aberration

## Next Steps

1. **Immediate:** Clone polynomial-optics repository
2. **Setup:** Build system and dependencies
3. **Test:** Basic functionality
4. **Integrate:** Python bindings
5. **Build:** Lens import tools
6. **Generate:** VEX code from existing lenses
7. **Deploy:** Replace current simplified system

## Questions to Address

- Do we need HDK plugin or is Python sufficient?
- Should we cache compiled VEX or generate on-demand?
- How to handle lens database versioning?
- Integration with existing shelf tools?
- Migration path for users of current system?
