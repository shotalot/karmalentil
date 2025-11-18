#!/usr/bin/env python3
"""
Validate Database Tool

Command-line tool for validating the lens database.

Usage:
    python tools/validate_database.py [options]

Example:
    python tools/validate_database.py --verbose
    python tools/validate_database.py --export validation_report.json
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'python'))

from potk import LensDatabaseManager


def main():
    parser = argparse.ArgumentParser(
        description='Validate polynomial lens database'
    )

    parser.add_argument(
        '--database',
        type=Path,
        default=None,
        help='Path to database root directory'
    )

    parser.add_argument(
        '--export',
        type=Path,
        default=None,
        help='Export validation report to JSON file'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List all lenses in database'
    )

    parser.add_argument(
        '--search',
        type=str,
        default=None,
        help='Search for lenses by name or metadata'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    print(f"Lens Database Validation")
    print(f"{'='*60}")

    try:
        # Initialize database manager
        db_manager = LensDatabaseManager(args.database)

        # List mode
        if args.list:
            lenses = db_manager.list_lenses()

            if not lenses:
                print(f"\n✗ No lenses found in database", file=sys.stderr)
                return 1

            print(f"\nFound {len(lenses)} lenses:\n")

            for lens in lenses:
                print(f"  • {lens['id']}")
                print(f"    Name: {lens['name']}")
                print(f"    Created: {lens['created']}")

                if args.verbose:
                    metadata = lens.get('metadata', {})
                    if 'focal_length' in metadata:
                        print(f"    Focal length: {metadata['focal_length']}mm")
                    if 'max_fstop' in metadata:
                        print(f"    Max f-stop: f/{metadata['max_fstop']}")
                    if 'polynomial_degree' in metadata:
                        print(f"    Polynomial degree: {metadata['polynomial_degree']}")

                print()

            return 0

        # Search mode
        if args.search:
            print(f"\nSearching for: '{args.search}'")

            matches = db_manager.search_lenses(args.search)

            if not matches:
                print(f"\n✗ No matching lenses found", file=sys.stderr)
                return 1

            print(f"\nFound {len(matches)} matching lenses:\n")

            for lens in matches:
                print(f"  • {lens['id']}")
                print(f"    Name: {lens['name']}")
                print()

            return 0

        # Validation mode (default)
        print(f"\nValidating database...")
        print(f"Database root: {db_manager.database_root}\n")

        valid_count, invalid_count, errors = db_manager.validate_database()

        # Create validation report
        validation_report = {
            'timestamp': datetime.now().isoformat(),
            'database_root': str(db_manager.database_root),
            'total_lenses': valid_count + invalid_count,
            'valid_lenses': valid_count,
            'invalid_lenses': invalid_count,
            'errors': errors
        }

        # Export report if requested
        if args.export:
            with open(args.export, 'w') as f:
                json.dump(validation_report, f, indent=2)
            print(f"\n✓ Validation report exported to: {args.export}")

        # Return error code if any validation failures
        if invalid_count > 0:
            print(f"\n⚠ Validation completed with {invalid_count} errors", file=sys.stderr)
            return 1

        print(f"\n✓ All lenses validated successfully!")
        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
