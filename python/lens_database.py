#!/usr/bin/env python
"""
Lens Database System for KarmaLentil
Manages lens models, loads polynomial data, and provides lens selection interface
"""

import os
import json
import glob


class LensDatabase:
    """
    Lens database manager
    """

    def __init__(self, database_path=None):
        """
        Initialize lens database

        Args:
            database_path: Path to lens database directory (default: $KARMALENTIL/lenses)
        """
        if database_path is None:
            # Use environment variable or default
            karmalentil_root = os.environ.get('KARMALENTIL', os.path.dirname(os.path.dirname(__file__)))
            database_path = os.path.join(karmalentil_root, 'lenses')

        self.database_path = database_path
        self.lenses = {}
        self.load_database()

    def load_database(self):
        """
        Load all available lenses from database
        """
        if not os.path.exists(self.database_path):
            print(f"Warning: Lens database not found at {self.database_path}")
            return

        # Scan for lens directories
        lens_dirs = glob.glob(os.path.join(self.database_path, '*'))

        for lens_dir in lens_dirs:
            if not os.path.isdir(lens_dir):
                continue

            lens_name = os.path.basename(lens_dir)

            # Check for required files
            required_files = [
                'lens_constants.h',
                'pt_evaluate.h'
            ]

            has_all = all(os.path.exists(os.path.join(lens_dir, f)) for f in required_files)

            if has_all:
                # Parse lens constants
                constants = self.parse_lens_constants(lens_dir)

                self.lenses[lens_name] = {
                    'name': lens_name,
                    'path': lens_dir,
                    'constants': constants,
                    'display_name': self.format_lens_name(lens_name)
                }

                print(f"Loaded lens: {lens_name}")

    def parse_lens_constants(self, lens_dir):
        """
        Parse lens constants from lens_constants.h

        Args:
            lens_dir: Path to lens directory

        Returns:
            Dictionary of lens constants
        """
        constants_file = os.path.join(lens_dir, 'lens_constants.h')
        constants = {}

        if not os.path.exists(constants_file):
            return constants

        with open(constants_file, 'r') as f:
            for line in f:
                line = line.strip()

                # Parse #define statements
                if line.startswith('#define'):
                    parts = line.split()
                    if len(parts) >= 3:
                        key = parts[1]
                        value = parts[2]

                        # Try to convert to number
                        try:
                            if '.' in value:
                                value = float(value)
                            else:
                                value = int(value)
                        except ValueError:
                            pass  # Keep as string

                        constants[key] = value

                # Parse const statements
                elif line.startswith('const float') or line.startswith('const int'):
                    # Extract variable name and value
                    if '=' in line:
                        parts = line.split('=')
                        name_part = parts[0].strip().split()[-1]
                        value_part = parts[1].strip().rstrip(';')

                        try:
                            if '.' in value_part:
                                value = float(value_part)
                            else:
                                value = int(value_part)
                            constants[name_part] = value
                        except ValueError:
                            pass

        return constants

    def format_lens_name(self, lens_name):
        """
        Format lens name for display

        Args:
            lens_name: Internal lens name (e.g., 'double_gauss_50mm')

        Returns:
            Display name (e.g., 'Double Gauss 50mm')
        """
        # Replace underscores with spaces and capitalize
        display_name = lens_name.replace('_', ' ').title()

        # Add f-stop if available
        # (Could parse from constants here)

        return display_name

    def get_lens_list(self):
        """
        Get list of available lenses

        Returns:
            List of (lens_name, display_name) tuples
        """
        return [(name, info['display_name']) for name, info in self.lenses.items()]

    def get_lens_info(self, lens_name):
        """
        Get information about a specific lens

        Args:
            lens_name: Internal lens name

        Returns:
            Dictionary with lens information or None if not found
        """
        return self.lenses.get(lens_name)

    def get_lens_path(self, lens_name):
        """
        Get path to lens directory

        Args:
            lens_name: Internal lens name

        Returns:
            Path to lens directory or None if not found
        """
        info = self.get_lens_info(lens_name)
        return info['path'] if info else None

    def get_lens_constants(self, lens_name):
        """
        Get lens constants

        Args:
            lens_name: Internal lens name

        Returns:
            Dictionary of lens constants or None if not found
        """
        info = self.get_lens_info(lens_name)
        return info['constants'] if info else None

    def export_to_json(self, output_path):
        """
        Export lens database to JSON

        Args:
            output_path: Path to output JSON file
        """
        export_data = {}

        for lens_name, info in self.lenses.items():
            export_data[lens_name] = {
                'display_name': info['display_name'],
                'constants': info['constants']
            }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"Exported lens database to: {output_path}")

    def generate_menu_items(self):
        """
        Generate menu items for Houdini parameter

        Returns:
            Tuple of (menu_items, menu_labels)
        """
        lenses = sorted(self.lenses.items(), key=lambda x: x[1]['display_name'])

        menu_items = [name for name, info in lenses]
        menu_labels = [info['display_name'] for name, info in lenses]

        return menu_items, menu_labels

    def search_lenses(self, query):
        """
        Search lenses by name or characteristics

        Args:
            query: Search query string

        Returns:
            List of matching lens names
        """
        query_lower = query.lower()
        matches = []

        for lens_name, info in self.lenses.items():
            # Search in name and display name
            if (query_lower in lens_name.lower() or
                query_lower in info['display_name'].lower()):
                matches.append(lens_name)
                continue

            # Search in constants (e.g., focal length)
            constants = info['constants']
            if 'LENS_FOCAL_LENGTH' in constants:
                focal = str(constants['LENS_FOCAL_LENGTH'])
                if query_lower in focal.lower():
                    matches.append(lens_name)

        return matches


def create_lens_database_json():
    """
    Create lens database JSON file
    """
    db = LensDatabase()

    # Get output path
    karmalentil_root = os.environ.get('KARMALENTIL', os.path.dirname(os.path.dirname(__file__)))
    output_path = os.path.join(karmalentil_root, 'lenses', 'lens_database.json')

    # Export
    db.export_to_json(output_path)

    return output_path


def main():
    """
    Test lens database
    """
    print("=" * 70)
    print("Lens Database")
    print("=" * 70)

    db = LensDatabase()

    print(f"\nFound {len(db.lenses)} lenses:")
    for lens_name, info in db.lenses.items():
        print(f"\n  {info['display_name']}")
        print(f"    Internal name: {lens_name}")
        print(f"    Path: {info['path']}")

        constants = info['constants']
        if 'LENS_FOCAL_LENGTH' in constants:
            print(f"    Focal length: {constants['LENS_FOCAL_LENGTH']}mm")
        if 'LENS_FSTOP_MIN' in constants:
            print(f"    Min f-stop: f/{constants['LENS_FSTOP_MIN']}")

    # Generate menu items
    menu_items, menu_labels = db.generate_menu_items()
    print("\nMenu items for Houdini:")
    for item, label in zip(menu_items, menu_labels):
        print(f"  {item}: {label}")

    # Create JSON export
    output_path = create_lens_database_json()
    print(f"\nExported database to: {output_path}")

    return db


if __name__ == '__main__':
    main()
