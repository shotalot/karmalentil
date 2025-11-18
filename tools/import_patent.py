#!/usr/bin/env python3
"""
Import Patent Tool

Command-line tool for importing lens designs from optical patents.

Usage:
    python tools/import_patent.py <patent_id> [options]

Example:
    python tools/import_patent.py 1927-zeiss-biotar --output database/optical_designs/
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from potk import LensImporter


def main():
    parser = argparse.ArgumentParser(
        description='Import lens design from optical patent database'
    )

    parser.add_argument(
        'patent_id',
        type=str,
        help='Patent identifier (e.g., 1927-zeiss-biotar)'
    )

    parser.add_argument(
        '--database',
        type=Path,
        default=None,
        help='Path to patent database directory'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=None,
        help='Output path for imported design (JSON)'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate imported design'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Import lens design
    print(f"Importing patent: {args.patent_id}")
    print(f"{'='*60}")

    try:
        importer = LensImporter.from_patent(args.patent_id, args.database)

        # Get optical system info
        optical_system = importer.get_optical_system()
        print(f"\n✓ Lens design imported successfully!")
        print(f"  Name: {optical_system.get('name', 'Unknown')}")
        print(f"  Elements: {len(optical_system.get('elements', []))}")
        print(f"  Focal length: {optical_system.get('focal_length', 0)}mm")

        # Validate if requested
        if args.validate:
            print(f"\nValidating design...")
            is_valid, error_msg = importer.validate_design()

            if is_valid:
                print(f"  ✓ Design validation passed")
            else:
                print(f"  ✗ Design validation failed: {error_msg}")
                return 1

        # Export if output path specified
        if args.output:
            output_file = args.output
            if output_file.is_dir():
                # If directory, create filename from patent_id
                filename = f"{args.patent_id}.json"
                output_file = output_file / filename

            importer.export_to_json(output_file)

        print(f"\n✓ Import complete!")
        return 0

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        print(f"\nAvailable patents should be in:")
        print(f"  database/optical_designs/")
        return 1

    except Exception as e:
        print(f"\n✗ Error importing patent: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
