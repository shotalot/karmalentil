#!/usr/bin/env python3
"""
Fit Lens Tool

Command-line tool for fitting polynomials to optical lens systems.

Usage:
    python tools/fit_lens.py <lens_design> [options]

Example:
    python tools/fit_lens.py database/optical_designs/zeiss_biotar_1927.json \
        --degree 7 --samples 10000 --validate --output database/fitted/
"""

import argparse
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from potk import LensImporter, PolyFitter, LensDatabaseManager


def main():
    parser = argparse.ArgumentParser(
        description='Fit polynomials to optical lens system'
    )

    parser.add_argument(
        'lens_design',
        type=Path,
        help='Path to lens design file (JSON)'
    )

    parser.add_argument(
        '--degree',
        type=int,
        default=7,
        help='Polynomial degree (default: 7, range: 5-9)'
    )

    parser.add_argument(
        '--samples',
        type=int,
        default=10000,
        help='Number of ray samples for fitting (default: 10000)'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate fit accuracy'
    )

    parser.add_argument(
        '--validation-samples',
        type=int,
        default=5000,
        help='Number of samples for validation (default: 5000)'
    )

    parser.add_argument(
        '--optimize-degree',
        action='store_true',
        help='Automatically find optimal polynomial degree'
    )

    parser.add_argument(
        '--target-error',
        type=float,
        default=0.01,
        help='Target RMS error in mm (default: 0.01)'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help='Output path for fitted data (JSON)'
    )

    parser.add_argument(
        '--save-to-database',
        action='store_true',
        help='Save fitted lens to database'
    )

    parser.add_argument(
        '--lens-id',
        type=str,
        default=None,
        help='Lens ID for database (defaults to filename)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Load lens design
    print(f"Loading lens design: {args.lens_design}")
    print(f"{'='*60}")

    try:
        if not args.lens_design.exists():
            raise FileNotFoundError(f"Lens design file not found: {args.lens_design}")

        with open(args.lens_design, 'r') as f:
            lens_data = json.load(f)

        print(f"\n✓ Lens design loaded")
        print(f"  Name: {lens_data.get('name', 'Unknown')}")
        print(f"  Focal length: {lens_data.get('focal_length', 0)}mm")

        # Create lens importer (will load into polynomial-optics system)
        importer = LensImporter()
        importer._load_optical_design(lens_data)
        optical_system = importer.get_optical_system()

        # Optimize degree if requested
        if args.optimize_degree:
            fitter = PolyFitter(samples=args.samples)
            optimal_degree, achieved_error = fitter.optimize_degree(
                optical_system,
                min_degree=5,
                max_degree=9,
                target_error=args.target_error
            )
            degree = optimal_degree
            print(f"\n✓ Optimal degree found: {degree} (RMS: {achieved_error:.6f}mm)")
        else:
            degree = args.degree

        # Fit polynomials
        print(f"\nFitting polynomials...")
        print(f"  Degree: {degree}")
        print(f"  Samples: {args.samples}")

        fitter = PolyFitter(degree=degree, samples=args.samples)
        coefficients = fitter.fit(optical_system, validation_samples=args.validation_samples)

        print(f"\n✓ Polynomial fitting complete")
        num_coeffs = len(coefficients['exit_pupil_x'])
        print(f"  Coefficients per direction: {num_coeffs}")

        # Validate if requested
        rms_error = None
        if args.validate:
            rms_error = fitter.validate(
                optical_system,
                coefficients,
                test_samples=args.validation_samples
            )

        # Prepare validation report
        validation_report = None
        if rms_error is not None:
            validation_report = {
                'rms_error': rms_error,
                'test_samples': args.validation_samples,
                'degree': degree,
                'fit_samples': args.samples
            }

        # Save to database if requested
        if args.save_to_database:
            lens_id = args.lens_id or args.lens_design.stem

            print(f"\nSaving to database...")
            db_manager = LensDatabaseManager()
            db_manager.save_lens(
                lens_id=lens_id,
                lens_data=lens_data,
                coefficients=coefficients,
                validation_report=validation_report
            )

        # Export to file if output path specified
        elif args.output:
            output_file = args.output
            if output_file.is_dir():
                # If directory, create filename from lens name
                filename = f"{args.lens_design.stem}_fitted.json"
                output_file = output_file / filename

            # Create complete fitted lens data
            fitted_data = {
                'metadata': lens_data,
                'coefficients': coefficients,
                'polynomial_degree': degree,
                'fit_samples': args.samples
            }

            if validation_report:
                fitted_data['validation'] = validation_report

            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(fitted_data, f, indent=2)

            print(f"\n✓ Fitted data saved to: {output_file}")

        print(f"\n✓ Lens fitting complete!")
        return 0

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\n✗ Error fitting lens: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
