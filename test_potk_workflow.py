#!/usr/bin/env python3
"""
POTK Workflow Test

Demonstrates the complete POTK workflow using the NumPy implementation:
1. Import lens design
2. Fit polynomials
3. Validate accuracy
4. Generate VEX shader

This test uses the example double-gauss lens design.
"""

import sys
from pathlib import Path

# Add python directory to path
sys.path.insert(0, str(Path(__file__).parent / 'python'))

from potk import LensImporter, PolyFitter, VEXGenerator, LensDatabaseManager


def main():
    print("="*60)
    print("POTK Workflow Demonstration")
    print("="*60)

    # Step 1: Import lens design
    print("\n1. Importing lens design from patent database...")
    print("-" * 60)

    try:
        lens_importer = LensImporter.from_patent(
            'example_lens',
            database_path=Path('database/optical_designs')
        )

        optical_system = lens_importer.get_optical_system()
        print(f"✓ Lens imported: {optical_system['name']}")
        print(f"  Focal length: {optical_system['focal_length']}mm")
        print(f"  Max f-stop: f/{optical_system['max_fstop']}")
        print(f"  Elements: {len(optical_system['elements'])}")

    except Exception as e:
        print(f"✗ Error importing lens: {e}")
        return 1

    # Step 2: Fit polynomials
    print("\n2. Fitting polynomials to lens system...")
    print("-" * 60)

    try:
        fitter = PolyFitter(degree=5, samples=500)  # Small for quick demo
        coefficients = fitter.fit(optical_system)

        print(f"✓ Polynomial fitting complete!")
        print(f"  Degree: {fitter.degree}")
        print(f"  Coefficients per direction: {len(coefficients['exit_pupil_x'])}")

    except Exception as e:
        print(f"✗ Error fitting polynomials: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Step 3: Validate accuracy
    print("\n3. Validating polynomial fit...")
    print("-" * 60)

    try:
        rms_error = fitter.validate(optical_system, coefficients, test_samples=100)

        print(f"\n✓ Validation complete!")
        print(f"  RMS error: {rms_error:.6f}mm")

    except Exception as e:
        print(f"✗ Error validating fit: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Step 4: Generate VEX shader
    print("\n4. Generating VEX shader...")
    print("-" * 60)

    try:
        lens_data = {
            **optical_system,
            'polynomial_degree': fitter.degree
        }

        output_path = Path('vex/generated/example_lens.vfl')
        shader_code = VEXGenerator.generate(
            lens_data=lens_data,
            coefficients=coefficients,
            output_path=output_path
        )

        print(f"✓ VEX shader generated!")
        print(f"  Output: {output_path}")
        print(f"  Size: {len(shader_code)} characters")

    except Exception as e:
        print(f"✗ Error generating VEX: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Step 5: Save to database
    print("\n5. Saving to lens database...")
    print("-" * 60)

    try:
        db_manager = LensDatabaseManager()

        validation_report = {
            'rms_error': rms_error,
            'test_samples': 100,
            'degree': fitter.degree,
            'fit_samples': fitter.samples,
            'implementation': 'numpy'
        }

        db_manager.save_lens(
            lens_id='example_double_gauss_50mm',
            lens_data=optical_system,
            coefficients=coefficients,
            validation_report=validation_report
        )

        print(f"✓ Lens saved to database!")

    except Exception as e:
        print(f"✗ Error saving to database: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Summary
    print("\n" + "="*60)
    print("POTK Workflow Complete!")
    print("="*60)
    print(f"""
Complete POTK workflow demonstrated:
  ✓ Lens import from patent database
  ✓ Polynomial fitting (NumPy implementation)
  ✓ Accuracy validation (RMS error: {rms_error:.6f}mm)
  ✓ VEX shader generation
  ✓ Database storage

Next steps:
  - Use tools/fit_lens.py for batch processing
  - Use tools/generate_vex.py for VEX generation
  - Integrate generated shaders with Karma
  - When network available, integrate C++ polynomial-optics

Note: This demo uses NumPy implementation.
      Full C++ polynomial-optics integration will provide:
      - 10-100x faster fitting
      - Higher accuracy
      - Research-grade validation
""")

    return 0


if __name__ == '__main__':
    sys.exit(main())
