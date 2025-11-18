# POTK Quick Start Guide

## What You Just Built

You've set up the infrastructure for **POTK (Polynomial Optics to Karma)** - a proper integration of the polynomial-optics library with Houdini Karma renderer.

## Current Status: Phase 1 Foundation ✅

The following infrastructure is now in place:

### ✅ Completed Components

1. **Python Package Structure** (`python/potk/`)
   - `LensImporter` - Import lens designs from patents
   - `PolyFitter` - Fit polynomials to optical systems
   - `VEXGenerator` - Generate optimized VEX shaders
   - `LensDatabaseManager` - Manage lens database

2. **Build System** (`CMakeLists.txt`)
   - CMake configuration for C++ compilation
   - Python bindings setup with pybind11
   - Dependency management (Eigen, polynomial-optics)

3. **C++ Python Bindings** (`src/python_bindings.cpp`)
   - Wrapper classes for polynomial-optics library
   - pybind11 integration for Python access

4. **CLI Tools** (`tools/`)
   - `import_patent.py` - Import lens designs
   - `fit_lens.py` - Fit polynomials
   - `generate_vex.py` - Generate VEX shaders
   - `validate_database.py` - Validate lens database

5. **VEX Template** (`vex/templates/lens_shader_template.vfl`)
   - Template for generated lens shaders
   - Polynomial evaluation code
   - Chromatic aberration support
   - Bokeh/DOF implementation

6. **Documentation**
   - `BUILD.md` - Complete build instructions
   - `POTK_README.md` - System overview
   - `POTK_IMPLEMENTATION_PLAN.md` - Full roadmap
   - `FEATURE_COMPARISON.md` - Feature analysis

7. **Example Data**
   - `database/optical_designs/example_lens.json` - Sample lens design

## Next Steps: Building POTK

### Phase 1: Library Integration (Current - 2-3 days)

**Status:** Infrastructure ready, needs implementation

**TODO:**
1. ✅ Directory structure created
2. ✅ Python package structure created
3. ✅ CMake build system created
4. ✅ Python bindings stub created
5. ⏳ **Next:** Clone polynomial-optics library
6. ⏳ Verify polynomial-optics build
7. ⏳ Implement C++ wrapper functions
8. ⏳ Build and test Python bindings
9. ⏳ Test basic lens import

**Commands to continue:**
```bash
# 1. Clone polynomial-optics library
./setup_potk.sh

# 2. Configure build
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release

# 3. Build (once polynomial-optics integration is complete)
make -j$(nproc)

# 4. Test
python3 -c "from potk import LensImporter; print('Success!')"
```

### Phase 2: Lens Database & Import Tools (3-4 days)

**TODO:**
- Implement lens import from patents
- Build polynomial fitting workflow
- Create validation tools
- Add lens database management
- Create Houdini HDAs for workflow

### Phase 3: VEX Code Generation (2-3 days)

**TODO:**
- Implement VEX code generator
- Add per-lens optimization
- Generate shaders from fitted lenses
- Test in Karma CPU

### Phase 4: Houdini Integration (2-3 days)

**TODO:**
- Python shelf tools
- Update camera parameter UI
- Real-time parameter updates
- Optional HDK plugin

### Phase 5: Advanced Features (3-5 days)

**TODO:**
- Anamorphic lens support
- Lens housing/vignetting
- Aspherical elements
- Chromatic aberration (wavelength-dependent)
- Bokeh AOV outputs

## File Structure

```
karmalentil/
├── README_POTK_QUICKSTART.md   ← You are here
├── BUILD.md                     ← Build instructions
├── POTK_README.md              ← System overview
├── POTK_IMPLEMENTATION_PLAN.md ← Full roadmap
├── FEATURE_COMPARISON.md       ← Feature analysis
├── setup_potk.sh               ← Setup script
├── CMakeLists.txt              ← Build configuration
│
├── python/potk/                ← Python package
│   ├── __init__.py
│   ├── lens_importer.py        ← Import lens designs
│   ├── poly_fitter.py          ← Fit polynomials
│   ├── vex_generator.py        ← Generate VEX
│   └── lens_database_manager.py ← Database management
│
├── src/
│   └── python_bindings.cpp     ← C++ ↔ Python bridge
│
├── tools/                      ← CLI tools
│   ├── import_patent.py
│   ├── fit_lens.py
│   ├── generate_vex.py
│   └── validate_database.py
│
├── vex/
│   ├── templates/              ← VEX templates
│   │   └── lens_shader_template.vfl
│   └── generated/              ← Generated shaders (future)
│
├── database/
│   ├── optical_designs/        ← Raw lens designs
│   │   └── example_lens.json
│   ├── fitted/                 ← Fitted lenses (future)
│   └── validation/             ← Validation reports (future)
│
├── hda/                        ← Houdini tools (future)
├── build/                      ← Build artifacts (gitignored)
└── ext/                        ← External dependencies (gitignored)
    └── lentil/                 ← Clone with ./setup_potk.sh
        └── polynomial-optics/
```

## What Makes POTK Different?

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
- Research-grade quality

## Example Workflow (Once Complete)

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
print(f"RMS error: {error}mm")  # Should be < 0.01mm

# 4. Generate optimized VEX shader
from potk import VEXGenerator
shader = VEXGenerator.generate(lens, coeffs)

# 5. Save to database
from potk import LensDatabaseManager
db = LensDatabaseManager()
db.save_lens('zeiss_biotar_1927', lens, coeffs)

# 6. Use in Houdini
# Select lens in camera parameter
# Render with Karma CPU
```

## Timeline

- **Phase 1 (Current):** 2-3 days - Library integration
- **Phase 2:** 3-4 days - Lens import/fitting
- **Phase 3:** 2-3 days - VEX generation
- **Phase 4:** 2-3 days - Houdini integration
- **Phase 5:** 3-5 days - Advanced features

**Total:** 2-3 weeks for complete professional-grade system

## Key Advantages

✅ **Automated lens creation** - Import from patents, fit automatically
✅ **Validated accuracy** - RMS error measurement, raytracing comparison
✅ **Optimized performance** - Per-lens generated VEX shaders
✅ **Full optical features** - Anamorphic, aspherical, vignetting
✅ **Research-grade quality** - Based on published optical research
✅ **Easy extensibility** - Add new lenses in minutes, not hours

## Questions?

See the detailed documentation:
- `BUILD.md` - How to build POTK
- `POTK_README.md` - System architecture and workflow
- `POTK_IMPLEMENTATION_PLAN.md` - Complete roadmap
- `FEATURE_COMPARISON.md` - Feature parity analysis

## Current Working System

The simplified KarmaLentil system (40 lenses, JSON-based) continues to work.
POTK will eventually replace it with a proper, research-based implementation.

**To use current system:** See main `README.md`
**To build POTK:** Continue with Phase 1 above
