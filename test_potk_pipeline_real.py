#!/usr/bin/env python3
"""
Test Full POTK Pipeline with Real Lens

This tests the complete workflow:
1. Load real lens from database
2. Create NumPy raytracer
3. Fit polynomial coefficients
4. Generate VEX shader
5. Ready for Houdini!
"""

import numpy as np
import sys
import json
from pathlib import Path

sys.path.insert(0, 'python')

from potk.lens_importer import load_lens_from_database
from potk.simple_raytracer import SimpleRaytracer
from potk.poly_fitter import fit_polynomial_lens
from potk.vex_generator import VEXGenerator

print("=" * 70)
print("POTK Full Pipeline Test - Real Lens")
print("=" * 70)

# Step 1: Load real lens from database
print("\n1. Loading lens from database...")
print("   Lens ID: 0001 (50mm f/2)")

lens_data = load_lens_from_database("0001", focal_length=50.0)

if lens_data:
    print(f"   ✅ Loaded: {lens_data['name']}")
    print(f"   Elements: {len(lens_data['elements'])}")
    print(f"   Focal length: {lens_data['focal_length']}mm")
    print(f"   Patent: {lens_data.get('patent_number', 'Unknown')}")
else:
    print("   ❌ Failed to load lens")
    sys.exit(1)

# Step 2: Create raytracer
print("\n2. Creating NumPy raytracer...")

raytracer = SimpleRaytracer.from_lens_data(lens_data)
print(f"   ✅ Raytracer created with {len(raytracer.elements)} surfaces")

# Quick test
print("   Testing raytracer...")
test_ray_origin = np.array([0.0, 0.0, -10.0])
test_ray_direction = np.array([0.0, 0.0, 1.0])
test_pos, test_dir = raytracer.trace_ray(test_ray_origin, test_ray_direction)

if test_pos is not None:
    print("   ✅ Raytracer working (test ray passed)")
else:
    print("   ⚠️  Test ray failed - checking batch...")

# Batch test
test_origins = np.zeros((50, 3))
test_origins[:, 0] = np.linspace(-5, 5, 50)
test_origins[:, 2] = -10.0
test_dirs = np.tile([0, 0, 1], (50, 1))
test_exit_pos, _ = raytracer.trace_rays_batch(test_origins, test_dirs)
num_valid = np.sum(~np.isnan(test_exit_pos[:, 0]))
print(f"   Batch test: {num_valid}/50 rays valid ({100*num_valid/50:.1f}%)")

if num_valid == 0:
    print("   ❌ Raytracer not working with this lens")
    print("   Lens may have complex geometry or require different approach")
    sys.exit(1)

# Step 3: Fit polynomial coefficients
print("\n3. Fitting polynomial coefficients...")
print("   Degree: 5")
print("   Samples: 500 rays")
print("   This may take a moment...")

try:
    coefficients = fit_polynomial_lens(
        lens_data=lens_data,
        raytracer=raytracer,
        degree=5,
        num_samples=500
    )

    # Count coefficients
    total_coeffs = sum(len(v) for v in coefficients.values())
    print(f"   ✅ Polynomial fitting complete!")
    print(f"   Total coefficients: {total_coeffs}")
    print(f"   Exit pupil X: {len(coefficients.get('exit_pupil_x', []))} coeffs")
    print(f"   Exit pupil Y: {len(coefficients.get('exit_pupil_y', []))} coeffs")

    # Show some example coefficients
    print("\n   Sample coefficients (exit_pupil_x):")
    for i, coeff in enumerate(coefficients.get('exit_pupil_x', [])[:6]):
        print(f"     c[{i}] = {coeff:+.6f}")

except Exception as e:
    print(f"   ❌ Polynomial fitting failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Generate VEX shader
print("\n4. Generating VEX shader...")

output_dir = Path('vex/generated')
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / 'potk_real_lens_50mm.vfl'

try:
    shader_code = VEXGenerator.generate(
        lens_data=lens_data,
        coefficients=coefficients,
        output_path=output_path,
        shader_name='potk_real_lens_50mm'
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

metadata_path = output_dir / 'potk_real_lens_50mm.json'
metadata = {
    'lens_id': '0001',
    'name': lens_data['name'],
    'focal_length': lens_data['focal_length'],
    'num_elements': len(lens_data['elements']),
    'polynomial_degree': 5,
    'num_samples': 500,
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
  ✅ Loaded real lens from database
  ✅ Created working raytracer ({num_valid}/50 test rays = {100*num_valid/50:.1f}%)
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
   cam.parm('vm_lensshader').set('potk_real_lens_50mm')

3. Render with Karma and see REAL lens distortion!

This is the FULL POTK workflow working end-to-end.
Real lens → Real raytracing → Real polynomial fit → Real Houdini shader!
""")
