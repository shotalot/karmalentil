#!/usr/bin/env python3
"""
Generate VEX Tool

Command-line tool for generating optimized VEX shaders from fitted lens data.

Usage:
    python tools/generate_vex.py <fitted_lens> [options]

Example:
    python tools/generate_vex.py database/fitted/zeiss_biotar_1927.json \
        --output vex/generated/zeiss_biotar_1927.vfl
"""

import argparse
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from potk import VEXGenerator, LensDatabaseManager


def main():
    parser = argparse.ArgumentParser(
        description='Generate optimized VEX shader from fitted lens data'
    )

    parser.add_argument(
        'fitted_lens',
        type=str,
        help='Path to fitted lens JSON file OR lens ID from database'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help='Output path for VEX shader (.vfl)'
    )

    parser.add_argument(
        '--template',
        type=str,
        default='lens_shader_template.vfl',
        help='VEX template filename (default: lens_shader_template.vfl)'
    )

    parser.add_argument(
        '--batch',
        action='store_true',
        help='Generate shaders for all lenses in database'
    )

    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('vex/generated'),
        help='Output directory for batch generation'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing shaders in batch mode'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    print(f"VEX Shader Generator")
    print(f"{'='*60}")

    try:
        # Batch mode: generate all lenses from database
        if args.batch:
            print(f"\nBatch generation mode")
            print(f"Output directory: {args.output_dir}")

            db_manager = LensDatabaseManager()
            all_lenses = db_manager.list_lenses()

            if not all_lenses:
                print(f"\n✗ No lenses found in database", file=sys.stderr)
                return 1

            print(f"Found {len(all_lenses)} lenses in database\n")

            # Load all lens data
            lens_database = {}
            for lens_info in all_lenses:
                lens_id = lens_info['id']
                lens_record = db_manager.load_lens(lens_id)
                if lens_record:
                    # Flatten structure for VEX generator
                    lens_database[lens_id] = {
                        **lens_record['metadata'],
                        'coefficients': lens_record['coefficients']
                    }

            # Generate batch
            generator = VEXGenerator()
            generator.generate_batch(
                lens_database=lens_database,
                output_dir=args.output_dir,
                overwrite=args.overwrite
            )

            return 0

        # Single lens mode
        fitted_lens_path = Path(args.fitted_lens)

        # Try loading from database first
        if not fitted_lens_path.exists():
            print(f"Trying to load '{args.fitted_lens}' from database...")
            db_manager = LensDatabaseManager()
            lens_record = db_manager.load_lens(args.fitted_lens)

            if lens_record is None:
                raise FileNotFoundError(
                    f"Lens not found as file or in database: {args.fitted_lens}"
                )

            # Extract lens data and coefficients
            lens_data = lens_record['metadata']
            coefficients = lens_record['coefficients']

            print(f"✓ Loaded from database")

        else:
            # Load from file
            print(f"Loading fitted lens: {fitted_lens_path}")

            with open(fitted_lens_path, 'r') as f:
                fitted_data = json.load(f)

            # Extract lens data and coefficients
            lens_data = fitted_data.get('metadata', fitted_data)
            coefficients = fitted_data.get('coefficients', {})

            print(f"✓ Loaded from file")

        print(f"  Name: {lens_data.get('name', 'Unknown')}")
        print(f"  Degree: {fitted_data.get('polynomial_degree', lens_data.get('polynomial_degree', 7))}")

        # Determine output path
        if args.output:
            output_path = args.output
        else:
            # Generate default filename
            lens_name = lens_data.get('name', 'unknown_lens').replace(' ', '_').lower()
            output_path = Path(f"vex/generated/{lens_name}.vfl")

        # Generate VEX shader
        print(f"\nGenerating VEX shader...")
        shader_code = VEXGenerator.generate(
            lens_data=lens_data,
            coefficients=coefficients,
            output_path=output_path
        )

        print(f"\n✓ VEX shader generation complete!")
        return 0

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\n✗ Error generating VEX shader: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
