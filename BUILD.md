# POTK Build Instructions

## Overview

POTK (Polynomial Optics to Karma) requires building C++ components and Python bindings to integrate the polynomial-optics library with Houdini.

## Prerequisites

### Required Software

1. **C++ Compiler**
   - GCC 5+ or Clang 3.8+ (Linux/macOS)
   - MSVC 2017+ (Windows)
   - Must support C++11

2. **CMake**
   - Version 3.12 or higher
   - Install: `sudo apt install cmake` (Ubuntu/Debian)

3. **Python 3.7+**
   - Houdini 19.0+ includes Python 3.9 or 3.10
   - Use Houdini's bundled Python for best compatibility

4. **Git**
   - For cloning polynomial-optics repository

### Required Libraries

1. **Eigen3** (Linear Algebra)
   - Version 3.3+
   - Header-only library (included with polynomial-optics)
   - OR install system-wide: `sudo apt install libeigen3-dev`

2. **pybind11** (Python Bindings)
   - Version 2.6+
   - Automatically downloaded by CMake if not found
   - OR install: `pip install pybind11`

### Optional

- **Houdini HDK** (for HDK plugins, Phase 4)
  - Required if building native Houdini operators
  - Included with Houdini installation

## Build Steps

### Step 1: Clone polynomial-optics Library

Run the setup script to clone the required polynomial-optics library:

```bash
cd /path/to/karmalentil
./setup_potk.sh
```

This will:
- Clone lentil repository (contains polynomial-optics)
- Initialize submodules (Eigen, etc.)
- Place library at `ext/lentil/polynomial-optics/`

**Expected output:**
```
==========================================
POTK Setup - Cloning polynomial-optics
==========================================
Cloning lentil repository (this may take a while)...
Initializing submodules...

✓ Setup complete!

polynomial-optics library is now available at:
  ext/lentil/polynomial-optics/
```

### Step 2: Configure Build with CMake

Create a build directory and configure:

```bash
mkdir build
cd build

# Using Houdini's Python (recommended)
cmake .. -DCMAKE_BUILD_TYPE=Release \
         -DPython3_ROOT_DIR=$HFS/python

# OR using system Python
cmake .. -DCMAKE_BUILD_TYPE=Release
```

**CMake Options:**
- `CMAKE_BUILD_TYPE`: `Release` (optimized) or `Debug` (debugging symbols)
- `BUILD_PYTHON_BINDINGS`: `ON` (default) or `OFF`
- `Python3_ROOT_DIR`: Path to Python installation (defaults to Houdini's Python)

**Expected output:**
```
-- Found Python: 3.10.10 at /opt/hfs20.5/python/bin/python3
-- Found pybind11: v2.11.1
-- Found Eigen3: 3.4.0

========================================
POTK Build Configuration
========================================
Version:                0.1.0
Build type:             Release
C++ standard:           11
Python bindings:        ON
  Python version:       3.10.10
  Python executable:    /opt/hfs20.5/python/bin/python3
polynomial-optics:      /home/user/karmalentil/ext/lentil/polynomial-optics
Eigen3:                 /usr/include/eigen3
========================================
```

### Step 3: Build

Compile the project:

```bash
# From build/ directory
make -j$(nproc)

# OR on Windows
cmake --build . --config Release --parallel
```

**Expected output:**
```
[ 25%] Building CXX object CMakeFiles/polynomial_optics_binding.dir/src/python_bindings.cpp.o
[ 50%] Linking CXX shared module python/potk/polynomial_optics_binding.so
[100%] Built target polynomial_optics_binding
```

### Step 4: Install (Optional)

Install Python modules and tools:

```bash
# From build/ directory
make install

# OR on Windows
cmake --install .
```

This copies:
- Python modules to `python/potk/`
- VEX templates to `vex/templates/`
- CLI tools to `tools/`

### Step 5: Test

Test the Python bindings:

```bash
# Set Houdini environment
cd /opt/hfs20.5
source houdini_setup

# Test import
cd /path/to/karmalentil
python3 -c "from potk import LensImporter, PolyFitter, VEXGenerator; print('POTK imported successfully!')"
```

**Expected output:**
```
POTK imported successfully!
```

## Houdini Integration

### Add POTK to Houdini Python Path

Add to your Houdini environment file (`~/houdini20.5/houdini.env`):

```bash
PYTHONPATH = "/path/to/karmalentil/python:$PYTHONPATH"
```

### Verify in Houdini Python Shell

Open Houdini, then in Python Shell:

```python
import potk
print(potk.__version__)  # Should print: 0.1.0

from potk import LensImporter
```

## Troubleshooting

### Error: "polynomial-optics library not found"

**Solution:** Run the setup script:
```bash
./setup_potk.sh
```

### Error: "Could not find Python"

**Solution:** Specify Houdini's Python explicitly:
```bash
cmake .. -DPython3_ROOT_DIR=$HFS/python
```

### Error: "pybind11 not found"

**Solution:** Let CMake download it automatically (default), or install manually:
```bash
pip install pybind11
```

### Error: "Eigen3 not found"

**Solution:** Eigen is included with polynomial-optics. If CMake still can't find it:
```bash
# Ubuntu/Debian
sudo apt install libeigen3-dev

# macOS
brew install eigen

# OR specify path manually
cmake .. -DEIGEN3_INCLUDE_DIR=/path/to/eigen
```

### Python Import Error: "No module named 'potk'"

**Solutions:**
1. Add to PYTHONPATH:
   ```bash
   export PYTHONPATH="/path/to/karmalentil/python:$PYTHONPATH"
   ```

2. Or add to Houdini environment file (`~/houdini20.5/houdini.env`):
   ```bash
   PYTHONPATH = "/path/to/karmalentil/python:$PYTHONPATH"
   ```

3. Or run from karmalentil directory:
   ```bash
   cd /path/to/karmalentil
   python3
   >>> import sys
   >>> sys.path.insert(0, 'python')
   >>> import potk
   ```

### Build Errors with polynomial-optics

**Solution:** Ensure submodules are initialized:
```bash
cd ext/lentil
git submodule update --init --recursive
```

## Platform-Specific Notes

### Linux (Ubuntu/Debian)

Install dependencies:
```bash
sudo apt update
sudo apt install build-essential cmake libeigen3-dev git python3-dev
```

### macOS

Install dependencies:
```bash
brew install cmake eigen git
```

Ensure Xcode Command Line Tools are installed:
```bash
xcode-select --install
```

### Windows

1. Install Visual Studio 2017+ with C++ support
2. Install CMake from https://cmake.org/download/
3. Use CMake GUI for configuration
4. Build from Visual Studio or command line:
   ```cmd
   cmake --build . --config Release
   ```

## Next Steps

After successful build:

1. **Test Python bindings** (see Step 5 above)
2. **Import a lens design** (see POTK_README.md for workflow)
3. **Generate VEX shaders** (Phase 3 of implementation plan)
4. **Integrate with Houdini** (Phase 4 of implementation plan)

## Build Targets Summary

| Target | Description |
|--------|-------------|
| `polynomial_optics_binding` | Python bindings (.so file) |
| `install` | Install Python modules and tools |
| `clean` | Remove build artifacts |

## Directory Structure After Build

```
karmalentil/
├── build/
│   ├── lib/
│   │   └── polynomial_optics_binding.so
│   └── CMakeFiles/
├── python/
│   └── potk/
│       ├── __init__.py
│       ├── lens_importer.py
│       ├── poly_fitter.py
│       ├── vex_generator.py
│       └── polynomial_optics_binding.so  (copied here)
└── ext/
    └── lentil/
        └── polynomial-optics/
```

## Development Build

For active development with debugging:

```bash
mkdir build-debug
cd build-debug
cmake .. -DCMAKE_BUILD_TYPE=Debug
make -j$(nproc)
```

Debug builds include:
- Debug symbols for GDB/LLDB
- Assertions enabled
- No optimization (easier to debug)

## References

- **CMake Documentation:** https://cmake.org/documentation/
- **pybind11 Documentation:** https://pybind11.readthedocs.io/
- **polynomial-optics:** https://github.com/zpelgrims/lentil/tree/dev/polynomial-optics
- **Houdini HDK:** https://www.sidefx.com/docs/hdk/
