"""
Lens Database Manager

Manages the database of fitted polynomial lens models.

Handles:
- Lens storage (JSON + binary formats)
- Versioning and validation
- Search and retrieval
- Metadata management
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime


class LensDatabaseManager:
    """
    Manager for polynomial lens database

    Stores fitted lens data with metadata, validation reports,
    and historical versions.
    """

    def __init__(self, database_root: Optional[Path] = None):
        """
        Initialize database manager

        Args:
            database_root: Root directory for lens database
        """
        if database_root is None:
            database_root = Path(__file__).parent.parent.parent / 'database'

        self.database_root = database_root
        self.optical_designs_dir = database_root / 'optical_designs'
        self.fitted_dir = database_root / 'fitted'
        self.validation_dir = database_root / 'validation'

        # Create directories if they don't exist
        for directory in [self.optical_designs_dir, self.fitted_dir, self.validation_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def save_lens(self, lens_id: str, lens_data: Dict,
                  coefficients: Dict[str, List[float]],
                  validation_report: Optional[Dict] = None):
        """
        Save fitted lens to database

        Args:
            lens_id: Unique lens identifier
            lens_data: Lens metadata
            coefficients: Fitted polynomial coefficients
            validation_report: Optional validation data
        """
        # Create complete lens record
        lens_record = {
            'id': lens_id,
            'name': lens_data.get('name', lens_id),
            'created': datetime.now().isoformat(),
            'metadata': lens_data,
            'coefficients': coefficients
        }

        # Save to fitted directory
        output_path = self.fitted_dir / f"{lens_id}.json"
        with open(output_path, 'w') as f:
            json.dump(lens_record, f, indent=2)

        print(f"Saved lens to database: {lens_id}")

        # Save validation report if provided
        if validation_report:
            validation_path = self.validation_dir / f"{lens_id}_validation.json"
            with open(validation_path, 'w') as f:
                json.dump(validation_report, f, indent=2)
            print(f"  Validation report: {validation_path}")

    def load_lens(self, lens_id: str) -> Optional[Dict]:
        """
        Load fitted lens from database

        Args:
            lens_id: Lens identifier

        Returns:
            Lens record or None if not found
        """
        lens_path = self.fitted_dir / f"{lens_id}.json"

        if not lens_path.exists():
            print(f"Lens not found in database: {lens_id}")
            return None

        with open(lens_path, 'r') as f:
            lens_record = json.load(f)

        return lens_record

    def list_lenses(self, filter_by: Optional[Dict] = None) -> List[Dict]:
        """
        List all lenses in database

        Args:
            filter_by: Optional filter criteria

        Returns:
            List of lens metadata dictionaries
        """
        lenses = []

        for lens_file in self.fitted_dir.glob('*.json'):
            with open(lens_file, 'r') as f:
                lens_data = json.load(f)

            # Apply filters if provided
            if filter_by:
                match = True
                for key, value in filter_by.items():
                    if lens_data.get('metadata', {}).get(key) != value:
                        match = False
                        break
                if not match:
                    continue

            lenses.append({
                'id': lens_data['id'],
                'name': lens_data.get('name', lens_data['id']),
                'created': lens_data.get('created', 'unknown'),
                'metadata': lens_data.get('metadata', {})
            })

        return sorted(lenses, key=lambda x: x['name'])

    def search_lenses(self, query: str) -> List[Dict]:
        """
        Search lenses by name or metadata

        Args:
            query: Search query string

        Returns:
            List of matching lens records
        """
        all_lenses = self.list_lenses()
        query_lower = query.lower()

        matches = []
        for lens in all_lenses:
            # Search in name
            if query_lower in lens['name'].lower():
                matches.append(lens)
                continue

            # Search in metadata
            metadata_str = json.dumps(lens['metadata']).lower()
            if query_lower in metadata_str:
                matches.append(lens)

        return matches

    def validate_database(self) -> Tuple[int, int, List[str]]:
        """
        Validate all lenses in database

        Returns:
            Tuple of (valid_count, invalid_count, error_messages)
        """
        print("\nValidating lens database...")

        valid_count = 0
        invalid_count = 0
        errors = []

        for lens_file in self.fitted_dir.glob('*.json'):
            try:
                with open(lens_file, 'r') as f:
                    lens_data = json.load(f)

                # Check required fields
                required_fields = ['id', 'name', 'coefficients']
                for field in required_fields:
                    if field not in lens_data:
                        raise ValueError(f"Missing required field: {field}")

                # Check coefficients
                coeffs = lens_data['coefficients']
                if not isinstance(coeffs, dict):
                    raise ValueError("Coefficients must be a dictionary")

                valid_count += 1
                print(f"  ✓ {lens_data['id']}")

            except Exception as e:
                invalid_count += 1
                error_msg = f"  ✗ {lens_file.name}: {str(e)}"
                errors.append(error_msg)
                print(error_msg)

        print(f"\nValidation complete: {valid_count} valid, {invalid_count} invalid")

        return valid_count, invalid_count, errors

    def export_database(self, output_path: Path):
        """
        Export entire database to single JSON file

        Args:
            output_path: Output file path
        """
        lenses = self.list_lenses()

        database_export = {
            'version': '1.0',
            'exported': datetime.now().isoformat(),
            'lens_count': len(lenses),
            'lenses': {}
        }

        for lens_info in lenses:
            lens_data = self.load_lens(lens_info['id'])
            if lens_data:
                database_export['lenses'][lens_info['id']] = lens_data

        with open(output_path, 'w') as f:
            json.dump(database_export, f, indent=2)

        print(f"Exported {len(lenses)} lenses to: {output_path}")
