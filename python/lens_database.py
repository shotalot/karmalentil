#!/usr/bin/env python
"""
Lens Database System for KarmaLentil
Manages lens models, loads polynomial data from JSON files
"""

import os
import json
import glob

try:
    import hou
    HOU_AVAILABLE = True
except ImportError:
    HOU_AVAILABLE = False


class LensDatabase:
    """
    Lens database manager - loads lens data from JSON files
    """

    def __init__(self, database_path=None):
        """
        Initialize lens database

        Args:
            database_path: Path to lens database directory (default: $KARMALENTIL/lenses)
        """
        if database_path is None:
            # Use environment variable or default
            if HOU_AVAILABLE:
                karmalentil_root = hou.getenv('KARMALENTIL')
                if not karmalentil_root:
                    karmalentil_root = os.environ.get('KARMALENTIL', os.path.dirname(os.path.dirname(__file__)))
            else:
                karmalentil_root = os.environ.get('KARMALENTIL', os.path.dirname(os.path.dirname(__file__)))

            database_path = os.path.join(karmalentil_root, 'lenses')

        self.database_path = database_path
        self.lenses = {}
        self._validated_lenses = {}  # Cache for validated lens data
        self._menu_cache = None      # Cache for menu items
        self.load_database()

    def load_database(self):
        """
        Load all available lenses from JSON files in database directory
        """
        if not os.path.exists(self.database_path):
            print(f"KarmaLentil: Warning - Lens database not found at {self.database_path}")
            return

        # Scan for JSON lens files
        json_files = glob.glob(os.path.join(self.database_path, '*.json'))

        if not json_files:
            print(f"KarmaLentil: Warning - No lens JSON files found in {self.database_path}")
            return

        for json_file in json_files:
            lens_id = os.path.splitext(os.path.basename(json_file))[0]

            try:
                with open(json_file, 'r') as f:
                    lens_data = json.load(f)

                    # Store lens data
                    self.lenses[lens_id] = lens_data

                    lens_name = lens_data.get('name', lens_id)
                    print(f"KarmaLentil: Loaded lens '{lens_name}' ({lens_id})")

            except Exception as e:
                print(f"KarmaLentil: ERROR loading {json_file}: {e}")

    def validate_lens(self, lens_id, lens_data):
        """
        Validate lens data structure and values

        Args:
            lens_id: Lens identifier
            lens_data: Dictionary containing lens parameters

        Returns:
            tuple: (is_valid, error_message)
        """
        required_fields = ['name', 'focal_length', 'max_fstop', 'polynomial_degree', 'coefficients']

        # Check required fields
        for field in required_fields:
            if field not in lens_data:
                return False, f"Missing required field: {field}"

        # Validate focal length
        focal_length = lens_data.get('focal_length', 0)
        if not isinstance(focal_length, (int, float)) or focal_length <= 0:
            return False, f"Invalid focal_length: {focal_length} (must be > 0)"

        # Validate f-stop
        max_fstop = lens_data.get('max_fstop', 0)
        if not isinstance(max_fstop, (int, float)) or max_fstop <= 0:
            return False, f"Invalid max_fstop: {max_fstop} (must be > 0)"

        # Validate polynomial degree
        poly_degree = lens_data.get('polynomial_degree', 0)
        if not isinstance(poly_degree, int) or poly_degree < 1:
            return False, f"Invalid polynomial_degree: {poly_degree} (must be >= 1)"

        # Validate coefficients
        coeffs = lens_data.get('coefficients', {})
        if 'exit_pupil_x' not in coeffs or 'exit_pupil_y' not in coeffs:
            return False, "Missing exit_pupil_x or exit_pupil_y coefficients"

        if not isinstance(coeffs['exit_pupil_x'], list) or not isinstance(coeffs['exit_pupil_y'], list):
            return False, "Coefficients must be lists"

        if len(coeffs['exit_pupil_x']) == 0 or len(coeffs['exit_pupil_y']) == 0:
            return False, "Coefficient arrays cannot be empty"

        return True, ""

    def get_lens(self, lens_id):
        """
        Get lens data by ID (with validation and caching)

        Args:
            lens_id: Lens identifier (e.g., 'double_gauss_50mm')

        Returns:
            Dictionary with complete lens data, or None if not found
        """
        # Check cache first
        if lens_id in self._validated_lenses:
            return self._validated_lenses[lens_id]

        # Get lens data
        lens_data = self.lenses.get(lens_id)
        if lens_data is None:
            print(f"KarmaLentil: ERROR - Lens '{lens_id}' not found")
            return None

        # Validate lens data
        is_valid, error_msg = self.validate_lens(lens_id, lens_data)
        if not is_valid:
            print(f"KarmaLentil: ERROR - Lens '{lens_id}' validation failed: {error_msg}")
            return None

        # Cache validated lens data
        self._validated_lenses[lens_id] = lens_data
        return lens_data

    def get_lens_list(self):
        """
        Get list of available lenses

        Returns:
            List of (lens_id, display_name) tuples sorted alphabetically
        """
        lens_list = []
        for lens_id, lens_data in self.lenses.items():
            lens_name = lens_data.get('name', lens_id)
            lens_list.append((lens_id, lens_name))

        return sorted(lens_list, key=lambda x: x[1])

    def get_lens_info(self, lens_id):
        """
        Get information about a specific lens (alias for get_lens)

        Args:
            lens_id: Lens identifier

        Returns:
            Dictionary with lens information or None if not found
        """
        return self.get_lens(lens_id)

    def get_polynomial_coefficients(self, lens_id):
        """
        Get polynomial coefficients for a lens

        Args:
            lens_id: Lens identifier

        Returns:
            Dictionary with 'exit_pupil_x' and 'exit_pupil_y' coefficient arrays,
            or None if lens not found
        """
        lens = self.get_lens(lens_id)
        if not lens:
            return None

        return lens.get('coefficients')

    def get_polynomial_degree(self, lens_id):
        """
        Get polynomial degree for a lens

        Args:
            lens_id: Lens identifier

        Returns:
            Integer polynomial degree, or None if lens not found
        """
        lens = self.get_lens(lens_id)
        if not lens:
            return None

        return lens.get('polynomial_degree', 5)

    def apply_lens_to_camera(self, camera_node, lens_id):
        """
        Apply lens parameters to a camera node

        Args:
            camera_node: Camera LOP node
            lens_id: Lens identifier to apply

        Returns:
            True if successful, False otherwise
        """
        if not HOU_AVAILABLE:
            print("KarmaLentil: ERROR - Houdini module not available")
            return False

        lens = self.get_lens(lens_id)
        if not lens:
            print(f"KarmaLentil: ERROR - Lens '{lens_id}' not found")
            return False

        try:
            # Update focal length
            if camera_node.parm('lentil_focal_length'):
                focal_length = lens.get('focal_length', 50.0)
                camera_node.parm('lentil_focal_length').set(focal_length)

            # Update f-stop
            if camera_node.parm('lentil_fstop'):
                max_fstop = lens.get('max_fstop', 2.8)
                camera_node.parm('lentil_fstop').set(max_fstop)

            # Update sensor width
            if camera_node.parm('lentil_sensor_width'):
                sensor_width = lens.get('sensor_width', 36.0)
                camera_node.parm('lentil_sensor_width').set(sensor_width)

            print(f"KarmaLentil: Applied lens '{lens.get('name', lens_id)}' to {camera_node.path()}")
            return True

        except Exception as e:
            print(f"KarmaLentil: ERROR applying lens: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_menu_items(self):
        """
        Generate menu items for Houdini parameter (cached)

        Returns:
            Tuple of (menu_items, menu_labels)
        """
        # Return cached menu if available
        if self._menu_cache is not None:
            return self._menu_cache

        lens_list = self.get_lens_list()

        if not lens_list:
            result = (['none'], ['No Lenses Available'])
            self._menu_cache = result
            return result

        menu_items = [lens_id for lens_id, _ in lens_list]
        menu_labels = [lens_name for _, lens_name in lens_list]

        result = (menu_items, menu_labels)
        self._menu_cache = result
        return result

    def export_lens_for_vex(self, lens_id, output_path):
        """
        Export lens data in a format VEX can read efficiently

        VEX can't easily read JSON, so we export in a simple text format:
        Line 1: polynomial_degree
        Line 2: focal_length
        Line 3: max_fstop
        Line 4: sensor_width
        Line 5+: exit_pupil_x coefficients (space-separated)
        Line N+: exit_pupil_y coefficients (space-separated)

        Args:
            lens_id: Lens identifier
            output_path: Path to write VEX-readable file

        Returns:
            True if successful, False otherwise
        """
        lens = self.get_lens(lens_id)
        if not lens:
            print(f"KarmaLentil: ERROR - Lens '{lens_id}' not found")
            return False

        try:
            with open(output_path, 'w') as f:
                # Write metadata
                f.write(f"{lens.get('polynomial_degree', 5)}\n")
                f.write(f"{lens.get('focal_length', 50.0)}\n")
                f.write(f"{lens.get('max_fstop', 2.8)}\n")
                f.write(f"{lens.get('sensor_width', 36.0)}\n")

                # Write polynomial coefficients
                coeffs = lens.get('coefficients', {})
                exit_pupil_x = coeffs.get('exit_pupil_x', [])
                exit_pupil_y = coeffs.get('exit_pupil_y', [])

                # Write x coefficients (space-separated)
                f.write(' '.join(str(c) for c in exit_pupil_x) + '\n')

                # Write y coefficients (space-separated)
                f.write(' '.join(str(c) for c in exit_pupil_y) + '\n')

            print(f"KarmaLentil: Exported lens '{lens.get('name', lens_id)}' for VEX to {output_path}")
            return True

        except Exception as e:
            print(f"KarmaLentil: ERROR exporting lens for VEX: {e}")
            import traceback
            traceback.print_exc()
            return False


# Global singleton instance
_lens_database_instance = None


def get_lens_database():
    """
    Get global lens database instance (singleton pattern)

    Returns:
        LensDatabase instance
    """
    global _lens_database_instance

    if _lens_database_instance is None:
        _lens_database_instance = LensDatabase()

    return _lens_database_instance


def main():
    """
    Test lens database
    """
    print("=" * 70)
    print("KarmaLentil Lens Database")
    print("=" * 70)

    db = LensDatabase()

    print(f"\nFound {len(db.lenses)} lens(es):")
    for lens_id, lens_data in db.lenses.items():
        print(f"\n  {lens_data.get('name', lens_id)}")
        print(f"    ID: {lens_id}")
        print(f"    Focal length: {lens_data.get('focal_length')}mm")
        print(f"    Max f-stop: f/{lens_data.get('max_fstop')}")
        print(f"    Sensor width: {lens_data.get('sensor_width')}mm")
        print(f"    Polynomial degree: {lens_data.get('polynomial_degree')}")

        # Count coefficients
        coeffs = lens_data.get('coefficients', {})
        if coeffs:
            num_coeffs_x = len(coeffs.get('exit_pupil_x', []))
            num_coeffs_y = len(coeffs.get('exit_pupil_y', []))
            print(f"    Coefficients: {num_coeffs_x} (x), {num_coeffs_y} (y)")

    # Generate menu items
    menu_items, menu_labels = db.generate_menu_items()
    print("\nMenu items for Houdini parameter:")
    for item, label in zip(menu_items, menu_labels):
        print(f"  {item}: {label}")

    return db


if __name__ == '__main__':
    main()
