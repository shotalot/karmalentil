"""
VEX Code Generator

Generates optimized VEX shaders from polynomial coefficients.

Each lens gets a custom-generated shader with:
- Embedded polynomial coefficients
- Optimized evaluation order
- Lens-specific parameters
- Chromatic aberration support
"""

from pathlib import Path
from typing import Dict, List, Optional
import json


class VEXGenerator:
    """
    VEX shader code generator for polynomial lens models

    Generates per-lens optimized VEX shaders from polynomial coefficients.
    """

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize VEX generator

        Args:
            template_dir: Path to VEX template directory
        """
        if template_dir is None:
            template_dir = Path(__file__).parent.parent.parent / 'vex' / 'templates'

        self.template_dir = template_dir
        self._template = None

    def load_template(self, template_name: str = 'lens_shader_template.vfl'):
        """
        Load VEX shader template

        Args:
            template_name: Template filename
        """
        template_path = self.template_dir / template_name

        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")

        with open(template_path, 'r') as f:
            self._template = f.read()

        print(f"Loaded VEX template: {template_name}")

    @classmethod
    def generate(cls, lens_data: Dict, coefficients: Dict[str, List[float]],
                 output_path: Optional[Path] = None) -> str:
        """
        Generate optimized VEX shader for a specific lens

        Args:
            lens_data: Lens metadata (name, focal length, etc.)
            coefficients: Polynomial coefficients
            output_path: Optional path to save generated shader

        Returns:
            Generated VEX shader code
        """
        generator = cls()

        # Generate shader code
        shader_code = generator._generate_shader(lens_data, coefficients)

        # Save if output path provided
        if output_path:
            generator.save_shader(shader_code, output_path)

        return shader_code

    def _generate_shader(self, lens_data: Dict, coefficients: Dict[str, List[float]]) -> str:
        """
        Internal shader generation logic

        Args:
            lens_data: Lens metadata
            coefficients: Polynomial coefficients

        Returns:
            VEX shader code
        """
        lens_name = lens_data.get('name', 'unknown_lens').replace(' ', '_').lower()
        focal_length = lens_data.get('focal_length', 50.0)
        max_fstop = lens_data.get('max_fstop', 2.8)
        degree = lens_data.get('polynomial_degree', 7)

        # Load template if not already loaded
        if self._template is None:
            self.load_template()

        # Generate coefficient arrays
        coeffs_x = coefficients.get('exit_pupil_x', [])
        coeffs_y = coefficients.get('exit_pupil_y', [])

        # Format coefficient arrays for VEX
        coeffs_x_str = self._format_coefficient_array(coeffs_x)
        coeffs_y_str = self._format_coefficient_array(coeffs_y)

        # Generate polynomial evaluation code
        poly_eval_code = self._generate_polynomial_evaluation(degree)

        # Template substitution
        shader_code = self._template
        shader_code = shader_code.replace('{LENS_NAME}', lens_name)
        shader_code = shader_code.replace('{FOCAL_LENGTH}', str(focal_length))
        shader_code = shader_code.replace('{MAX_FSTOP}', str(max_fstop))
        shader_code = shader_code.replace('{POLYNOMIAL_DEGREE}', str(degree))
        shader_code = shader_code.replace('{COEFFS_X}', coeffs_x_str)
        shader_code = shader_code.replace('{COEFFS_Y}', coeffs_y_str)
        shader_code = shader_code.replace('{POLY_EVAL_CODE}', poly_eval_code)

        print(f"\nGenerated VEX shader for: {lens_data.get('name', 'unknown')}")
        print(f"  Polynomial degree: {degree}")
        print(f"  Coefficients: {len(coeffs_x)} per direction")
        print(f"  Lines of code: {len(shader_code.splitlines())}")

        return shader_code

    def _format_coefficient_array(self, coefficients: List[float]) -> str:
        """
        Format coefficient list as VEX array literal

        Args:
            coefficients: List of float coefficients

        Returns:
            VEX array string
        """
        # Format with 4 coefficients per line for readability
        lines = []
        for i in range(0, len(coefficients), 4):
            chunk = coefficients[i:i+4]
            line = ', '.join(f'{c:.10e}' for c in chunk)
            lines.append(f'        {line}')

        return ',\n'.join(lines)

    def _generate_polynomial_evaluation(self, degree: int) -> str:
        """
        Generate optimized polynomial evaluation code

        Args:
            degree: Polynomial degree

        Returns:
            VEX code for evaluating polynomial
        """
        # TODO: Generate Horner's method or optimized evaluation
        # This could be degree-specific for maximum performance

        code = f"""
    // Evaluate degree-{degree} polynomial using Horner's method
    // This is a placeholder - will be optimized per lens
    float eval_poly(float coeffs[]; float x; float y)
    {{
        // TODO: Implement optimized evaluation
        return 0.0;
    }}
"""
        return code

    def save_shader(self, shader_code: str, output_path: Path):
        """
        Save generated shader to file

        Args:
            shader_code: VEX shader code
            output_path: Output file path
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(shader_code)

        print(f"  Saved shader to: {output_path}")

    def generate_batch(self, lens_database: Dict[str, Dict],
                      output_dir: Path,
                      overwrite: bool = False):
        """
        Generate VEX shaders for multiple lenses

        Args:
            lens_database: Dictionary of lens_id -> lens_data
            output_dir: Output directory for generated shaders
            overwrite: Whether to overwrite existing shaders
        """
        print(f"\nGenerating VEX shaders for {len(lens_database)} lenses...")

        output_dir.mkdir(parents=True, exist_ok=True)

        generated = 0
        skipped = 0

        for lens_id, lens_data in lens_database.items():
            lens_name = lens_data.get('name', lens_id).replace(' ', '_').lower()
            output_path = output_dir / f"{lens_name}.vfl"

            if output_path.exists() and not overwrite:
                print(f"  Skipping {lens_name} (already exists)")
                skipped += 1
                continue

            coefficients = lens_data.get('coefficients', {})
            shader_code = self._generate_shader(lens_data, coefficients)
            self.save_shader(shader_code, output_path)
            generated += 1

        print(f"\n✓ Generated {generated} shaders, skipped {skipped}")
