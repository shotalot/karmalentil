#!/usr/bin/env python3
"""
Test Full POTK Pipeline Using C++ Bindings

This tests the complete workflow using the working C++ bindings:
1. Load real lens from polynomial-optics database
2. Generate sample rays from lens
3. Fit polynomial coefficients
4. Generate VEX shader
5. Ready for Houdini!
"""

import numpy as np
import sys
import json
from pathlib import Path

sys.path.insert(0, 'python')

try:
    import polynomial_optics_binding as cpp
    print("✅ C++ bindings imported successfully")
except ImportError as e:
    print(f"❌ Cannot import C++ bindings: {e}")
    print("   Make sure the module is built and in Python path")
    sys.exit(1)

from potk.poly_fitter import fit_polynomial_from_data
from potk.vex_generator import VEXGenerator

print("=" * 70)
print("POTK Full Pipeline Test - C++ Bindings")
print("=" * 70)

# Step 1: Load real lens from C++ database
print("\n1. Loading lens from polynomial-optics database...")
print("   Lens ID: 0001")
print("   Focal length: 100mm")

try:
    lens = cpp.LensSystem()
    success = lens.load_from_database("0001", 100.0)

    if not success:
        print("   ❌ Failed to load lens from database")
        sys.exit(1)

    print(f"   ✅ Lens loaded successfully")
    print(f"   Lens length: {lens.lens_length:.2f}mm")
    print(f"   Num elements: {lens.num_lenses}")

except Exception as e:
    print(f"   ❌ Error loading lens: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Create raytracer and generate sample data
print("\n2. Generating sample ray data...")
print("   Using C++ raytracer...")

try:
    raytracer = cpp.Raytracer(lens, zoom=0.5)
    print("   ✅ Raytracer created")

    # Generate sample rays
    num_samples = 500
    print(f"   Generating {num_samples} sample rays...")

    # Generate grid of sensor positions and directions
    sensor_positions = []
    sensor_directions = []
    exit_positions = []
    exit_directions = []

    # Grid sampling
    grid_size = int(np.sqrt(num_samples))
    for i in range(grid_size):
        for j in range(grid_size):
            # Sensor position (normalized -0.5 to 0.5)
            sx = (i / (grid_size - 1)) - 0.5
            sy = (j / (grid_size - 1)) - 0.5

            # Direction (small angles)
            dx = sx * 0.2  # Small angle
            dy = sy * 0.2
            dz = 1.0

            sensor_positions.append([sx, sy, 0.0])
            sensor_directions.append([dx, dy, dz])

            # Trace ray through lens
            try:
                success, exit_pos, exit_dir = raytracer.trace_ray(
                    [sx, sy, 0.0],
                    [dx, dy, dz],
                    550.0  # wavelength
                )

                if success:
                    exit_positions.append(exit_pos)
                    exit_directions.append(exit_dir)
                else:
                    exit_positions.append([np.nan, np.nan, np.nan])
                    exit_directions.append([np.nan, np.nan, np.nan])

            except Exception as e:
                exit_positions.append([np.nan, np.nan, np.nan])
                exit_directions.append([np.nan, np.nan, np.nan])

    sensor_positions = np.array(sensor_positions)
    sensor_directions = np.array(sensor_directions)
    exit_positions = np.array(exit_positions)
    exit_directions = np.array(exit_directions)

    # Count valid rays
    valid = ~np.isnan(exit_positions[:, 0])
    num_valid = np.sum(valid)
    success_rate = 100 * num_valid / len(exit_positions)

    print(f"   Valid rays: {num_valid}/{len(exit_positions)} ({success_rate:.1f}%)")

    if num_valid < 50:
        print("   ⚠️  Too few valid rays, continuing anyway...")
    else:
        print("   ✅ Sufficient rays for polynomial fitting")

except Exception as e:
    print(f"   ❌ Error generating rays: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Fit polynomial coefficients
print("\n3. Fitting polynomial coefficients...")
print("   Degree: 5")
print("   Using valid ray pairs...")

try:
    # Filter to valid rays only
    valid_sensor_pos = sensor_positions[valid]
    valid_sensor_dir = sensor_directions[valid]
    valid_exit_pos = exit_positions[valid]
    valid_exit_dir = exit_directions[valid]

    print(f"   Fitting with {len(valid_sensor_pos)} valid samples...")

    # Fit polynomials
    coefficients = fit_polynomial_from_data(
        sensor_positions=valid_sensor_pos,
        sensor_directions=valid_sensor_dir,
        exit_positions=valid_exit_pos,
        exit_directions=valid_exit_dir,
        degree=5
    )

    total_coeffs = sum(len(v) for v in coefficients.values())
    print(f"   ✅ Polynomial fitting complete!")
    print(f"   Total coefficients: {total_coeffs}")

    # Show sample coefficients
    print("\n   Sample coefficients:")
    for key in ['exit_pupil_x', 'exit_pupil_y']:
        if key in coefficients:
            print(f"   {key}: {len(coefficients[key])} coeffs")
            print(f"     c[0] = {coefficients[key][0]:+.6f} (constant)")
            print(f"     c[1] = {coefficients[key][1]:+.6f} (linear x)")
            print(f"     c[2] = {coefficients[key][2]:+.6f} (linear y)")

except Exception as e:
    print(f"   ❌ Polynomial fitting failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Generate VEX shader
print("\n4. Generating VEX shader...")

output_dir = Path('vex/generated')
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / 'potk_cpp_lens.vfl'

try:
    # Create lens data dictionary
    lens_data = {
        'name': 'POTK Lens (from C++ database)',
        'focal_length': 100.0,
        'lens_id': '0001',
        'aperture': 2.0
    }

    shader_code = VEXGenerator.generate(
        lens_data=lens_data,
        coefficients=coefficients,
        output_path=output_path,
        shader_name='potk_cpp_lens'
    )

    file_size = output_path.stat().st_size
    num_lines = len(shader_code.split('\n'))

    print(f"   ✅ VEX shader generated!")
    print(f"   Output: {output_path}")
    print(f"   Size: {file_size:,} bytes")
    print(f"   Lines: {num_lines}")

except Exception as e:
    print(f"   ❌ VEX generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Save metadata
print("\n5. Saving lens metadata...")

metadata_path = output_dir / 'potk_cpp_lens.json'
metadata = {
    'lens_id': '0001',
    'name': lens_data['name'],
    'focal_length': lens_data['focal_length'],
    'polynomial_degree': 5,
    'num_samples': num_valid,
    'success_rate': success_rate,
    'coefficients': {k: v.tolist() if isinstance(v, np.ndarray) else v
                     for k, v in coefficients.items()}
}

with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"   ✅ Metadata saved: {metadata_path}")

# Summary
print("\n" + "=" * 70)
print("🎉 POTK PIPELINE COMPLETE!")
print("=" * 70)
print(f"""
Pipeline summary:
  ✅ Loaded real lens from C++ database
  ✅ Generated {num_valid} valid ray samples ({success_rate:.1f}% success)
  ✅ Fit polynomial coefficients ({total_coeffs} coefficients)
  ✅ Generated VEX shader ({num_lines} lines, {file_size/1024:.1f}KB)
  ✅ Saved metadata

Generated files:
  - {output_path}
  - {metadata_path}

Next step: USE IN HOUDINI!

1. Set environment variable (in houdini.env):
   HOUDINI_VEX_PATH = "{output_path.parent.absolute()};&"

2. In Houdini Python shell:
   import hou
   cam = hou.node('/obj/cam1')
   cam.parm('vm_lensshader').set('potk_cpp_lens')

3. Render with Karma and see REAL lens distortion from REAL lens data!

This is POTK working end-to-end:
Real lens database → C++ raytracing → Polynomial fitting → VEX shader → Houdini!
""")
