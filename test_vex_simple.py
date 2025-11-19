#!/usr/bin/env python3
"""Simple VEX Generation Test - Just verify it works"""

import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).parent / 'python'))
from potk import VEXGenerator

# Create mock lens and coefficients
lens_data = {
    'name': 'Test Double-Gauss 50mm f/2.0',
    'focal_length': 50.0,
    'max_fstop': 2.0,
    'elements': [{'surface': i+1, 'radius': 45.5, 'thickness': 6.0,
                  'material': 'N-SK16', 'diameter': 40.0} for i in range(10)],
    'polynomial_degree': 5
}

num_coeffs = 21  # (5+1)*(5+2)/2
coefficients = {
    'exit_pupil_x': np.random.randn(num_coeffs) * 0.1,
    'exit_pupil_y': np.random.randn(num_coeffs) * 0.1,
    'entrance_pupil_x': np.random.randn(num_coeffs) * 0.1,
    'entrance_pupil_y': np.random.randn(num_coeffs) * 0.1,
}
coefficients['exit_pupil_x'][1] = 1.0
coefficients['exit_pupil_y'][2] = 1.0

# Generate VEX
print("Generating VEX shader...")
output_path = Path('vex/generated/test_simple.vfl')
shader_code = VEXGenerator.generate(lens_data, coefficients, output_path)

print(f"✓ VEX shader generated: {output_path}")
print(f"  Size: {len(shader_code)} bytes")
print(f"  Lines: {len(shader_code.splitlines())}")
print(f"\nFirst 30 lines:")
print("-" * 60)
for i, line in enumerate(shader_code.splitlines()[:30], 1):
    print(f"{i:3d} | {line}")
print("...")
print("\n✅ VEX generation pipeline working!")
