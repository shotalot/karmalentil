# POTK Network Limitation - Alternative Implementation Path

## Current Situation

External network access is restricted in this environment, preventing the cloning of the polynomial-optics library from GitHub:

```bash
git clone https://github.com/zpelgrims/lentil.git
# Fails with exit code 1 (no network access)
```

The polynomial-optics C++ library is a key dependency for POTK's full implementation.

## Verification

The polynomial-optics library exists and is accessible:
- **Repository:** https://github.com/zpelgrims/lentil (branch: dev)
- **Subdirectory:** `polynomial-optics/` (confirmed present)
- **Purpose:** Sparse high-degree polynomials for wide-angle lenses
- **Includes:** Eigen submodule for linear algebra

## Implementation Options

### Option 1: External Setup (Recommended for Production)

**For users with network access**, follow the original plan:

```bash
# Clone polynomial-optics
./setup_potk.sh

# Build with CMake
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc)

# Test
python3 -c "from potk import LensImporter; print('Success!')"
```

This provides the full research-grade implementation with:
- ✅ Real polynomial fitting algorithms
- ✅ Raytracing validation
- ✅ RMS error measurement
- ✅ Optimal accuracy

### Option 2: Pure Python Implementation (Current Environment)

**For environments without network access**, create a simplified Python-only implementation that:

1. **Demonstrates the POTK architecture**
2. **Provides working lens import/export**
3. **Implements simplified polynomial fitting** (NumPy-based)
4. **Generates functional VEX shaders**
5. **Works with current lens database**

**Limitations:**
- ⚠️ No C++ polynomial-optics integration
- ⚠️ Simplified fitting algorithms (less accurate)
- ⚠️ No raytracing validation
- ⚠️ Approximate RMS errors

**Advantages:**
- ✅ No external dependencies
- ✅ Works in restricted environments
- ✅ Demonstrates full workflow
- ✅ Easy to swap for real implementation later

### Option 3: Hybrid Approach (Staged Implementation)

1. **Phase 1 (Current):** Python-only implementation for workflow demonstration
2. **Phase 2 (When network available):** Integrate real polynomial-optics
3. **Phase 3:** Performance optimization with C++ extensions

## Recommended Path Forward

Given the network limitation, I recommend **Option 2: Pure Python Implementation** with these components:

### 1. Python Polynomial Fitting (NumPy-based)

```python
# python/potk/polynomial_fitter_numpy.py
import numpy as np
from scipy.optimize import least_squares

class NumpyPolyFitter:
    """
    Pure Python polynomial fitter using NumPy/SciPy

    Simplified fitting algorithm for demonstration.
    Can be replaced with polynomial-optics C++ library.
    """

    def fit(self, lens_system, samples=10000):
        # Generate sample rays through lens system
        # Fit polynomials using least-squares
        # Return coefficients
        pass
```

### 2. Simplified Ray Tracer

```python
# python/potk/simple_raytracer.py
import numpy as np

class SimpleRaytracer:
    """
    Simplified optical raytracer for validation

    Basic geometric optics implementation.
    Less accurate than polynomial-optics C++ raytracer.
    """

    def trace_through_lens(self, lens_system, ray_origins, ray_dirs):
        # Trace rays through lens elements
        # Apply Snell's law at each surface
        # Return exit positions and directions
        pass
```

### 3. Current Lens Database Integration

```python
# Leverage existing lens database (40 lenses, JSON format)
# Convert to POTK format with metadata
# Generate VEX shaders from existing coefficients
```

## File Structure for Option 2

```
python/potk/
├── __init__.py
├── lens_importer.py          (✅ ready)
├── vex_generator.py           (✅ ready)
├── lens_database_manager.py   (✅ ready)
├── poly_fitter.py             (stub - needs implementation)
│
# New files for Python-only implementation:
├── polynomial_fitter_numpy.py  (NumPy-based fitting)
├── simple_raytracer.py        (Basic raytracer)
├── lens_converter.py          (Convert existing lens database)
└── validation.py              (Simplified validation)
```

## Timeline Adjustment

### Original Timeline (with polynomial-optics)
- Phase 1: 2-3 days (library integration)
- **Blocked:** No network access

### Adjusted Timeline (Python-only)
- Phase 1a: 1-2 days (Python polynomial fitting)
- Phase 1b: 1 day (Simple raytracer)
- Phase 1c: 1 day (Lens database conversion)
- Phase 2-5: Continue as planned

**Total:** Same 2-3 weeks, different implementation path

## Migration Path

When polynomial-optics becomes available:

1. **Drop-in replacement** for Python implementations:
   ```python
   # Before (Python-only)
   from potk.polynomial_fitter_numpy import NumpyPolyFitter

   # After (C++ integration)
   from potk.poly_fitter import PolyFitter  # Uses C++ bindings
   ```

2. **Improved accuracy** with no workflow changes
3. **Performance boost** (10-100x faster fitting)
4. **Research-grade validation**

## Current Status

- ✅ Infrastructure complete (Python package, CMake, bindings stub)
- ✅ CLI tools ready
- ✅ VEX template ready
- ✅ Documentation complete
- ⏳ **Network access blocked** - cannot clone polynomial-optics
- 📋 **Next:** Implement Python-only version (Option 2)

## Decision Point

**Which path should we take?**

1. **Wait for network access** → Option 1 (full C++ integration)
2. **Proceed with Python-only** → Option 2 (demonstration + workflow)
3. **Document and defer** → Focus on other project aspects

**Recommendation:** Proceed with **Option 2** to maintain momentum and demonstrate the complete POTK architecture, with clear migration path to C++ implementation when network access is available.
