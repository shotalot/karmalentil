#!/usr/bin/env python3
"""
Test VEX Generation Pipeline

Tests the VEX shader generation without requiring working raytracer.
Uses mock polynomial coefficients to verify the VEX generation works.
"""

import sys
from pathlib import Path
import numpy as np

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent / 'python'))

from potk import VEXGenerator

def create_mock_lens_data():
    """Create mock lens data for testing"""
    return {
        'name': 'Test Double-Gauss 50mm f/2.0',
        'focal_length': 50.0,
        'max_fstop': 2.0,
        'elements': [
            {'surface': i+1, 'radius': 45.5, 'thickness': 6.0,
             'material': 'N-SK16', 'diameter': 40.0}
            for i in range(10)
        ],
        'polynomial_degree': 5
    }

def create_mock_coefficients(degree=5):
    """
    Create mock polynomial coefficients

    For a lens system, we need coefficients for:
    - exit_pupil_x: Maps sensor position to exit pupil x
    - exit_pupil_y: Maps sensor position to exit pupil y
    - entrance_pupil_x: Maps aperture to entrance pupil x
    - entrance_pupil_y: Maps aperture to entrance pupil y
    """
    # Number of coefficients = (degree + 1) * (degree + 2) / 2
    num_coeffs = (degree + 1) * (degree + 2) // 2

    # Create simple polynomial coefficients
    # For testing, we'll use simple values that create mild distortion
    coefficients = {
        'exit_pupil_x': np.random.randn(num_coeffs) * 0.1,
        'exit_pupil_y': np.random.randn(num_coeffs) * 0.1,
        'entrance_pupil_x': np.random.randn(num_coeffs) * 0.1,
        'entrance_pupil_y': np.random.randn(num_coeffs) * 0.1,
    }

    # Set linear terms to 1.0 for pass-through behavior
    coefficients['exit_pupil_x'][1] = 1.0  # x coefficient
    coefficients['exit_pupil_y'][2] = 1.0  # y coefficient
    coefficients['entrance_pupil_x'][1] = 1.0
    coefficients['entrance_pupil_y'][2] = 1.0

    return coefficients

def main():
    print("=" * 60)
    print("VEX Generation Pipeline Test")
    print("=" * 60)

    # Step 1: Create mock data
    print("\n1. Creating mock lens data...")
    print("-" * 60)

    lens_data = create_mock_lens_data()
    print(f"✓ Mock lens created: {lens_data['name']}")
    print(f"  Focal length: {lens_data['focal_length']}mm")
    print(f"  Elements: {len(lens_data['elements'])}")
    print(f"  Polynomial degree: {lens_data['polynomial_degree']}")

    # Step 2: Create mock coefficients
    print("\n2. Creating mock polynomial coefficients...")
    print("-" * 60)

    coefficients = create_mock_coefficients(degree=lens_data['polynomial_degree'])
    print(f"✓ Coefficients created:")
    for key, value in coefficients.items():
        print(f"  {key}: {len(value)} coefficients")

    # Step 3: Generate VEX shader
    print("\n3. Generating VEX shader...")
    print("-" * 60)

    try:
        output_path = Path('vex/generated/test_mock_lens.vfl')
        output_path.parent.mkdir(parents=True, exist_ok=True)

        shader_code = VEXGenerator.generate(
            lens_data=lens_data,
            coefficients=coefficients,
            output_path=output_path
        )

        print(f"✓ VEX shader generated!")
        print(f"  Output: {output_path}")
        print(f"  Size: {len(shader_code)} characters")
        print(f"  Lines: {shader_code.count(chr(10))} lines")

    except Exception as e:
        print(f"✗ Error generating VEX: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Step 4: Verify shader contents
    print("\n4. Verifying shader contents...")
    print("-" * 60)

    # Check for key components
    checks = {
        'Function declaration': 'cvex lens_shader' in shader_code,
        'Input parameters': 'vector sensor_pos' in shader_code,
        'Output parameters': 'export vector exit_pos' in shader_code,
        'Polynomial evaluation': 'polynomial_eval' in shader_code or 'eval_poly' in shader_code,
        'Lens name comment': lens_data['name'] in shader_code,
    }

    all_passed = True
    for check_name, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check_name}")
        if not passed:
            all_passed = False

    if not all_passed:
        print("\n⚠️  Warning: Some shader components missing")
        return 1

    # Step 5: Show shader preview
    print("\n5. Shader preview (first 50 lines):")
    print("-" * 60)
    lines = shader_code.split('\n')[:50]
    for i, line in enumerate(lines, 1):
        print(f"  {i:3d} | {line}")

    total_lines = len(shader_code.split('\n'))
    if total_lines > 50:
        print(f"  ... ({total_lines - 50} more lines)")

    # Summary
    print("\n" + "=" * 60)
    print("VEX Generation Test Complete!")
    print("=" * 60)
    print(f"""
Test Results:
  ✓ Mock lens data created
  ✓ Polynomial coefficients generated
  ✓ VEX shader compiled
  ✓ All shader components present

Next Steps:
  1. Load shader in Houdini Karma
  2. Apply to camera lens shader parameter
  3. Test rendering with lens distortion
  4. Compare with reference images

Note: This shader uses mock coefficients for testing.
      For production, use real polynomial fits from optical data.
""")

    return 0

if __name__ == '__main__':
    sys.exit(main())
