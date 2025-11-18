"""
POTK - Polynomial Optics to Karma

Python package for integrating polynomial-optics library with Houdini Karma.

This package provides:
- Lens database management
- Polynomial fitting interface
- VEX code generation
- Patent import tools

Usage:
    from potk import LensImporter, PolyFitter, VEXGenerator

    # Import lens design
    lens = LensImporter.from_patent('1927-zeiss-biotar')

    # Fit polynomials
    fitter = PolyFitter(degree=7)
    coeffs = fitter.fit(lens, samples=10000)

    # Validate
    error = fitter.validate(lens, coeffs)

    # Generate VEX shader
    shader = VEXGenerator.generate(lens, coeffs)
"""

__version__ = "0.1.0"
__author__ = "KarmaLentil Project"

# Core components (to be implemented)
from .lens_importer import LensImporter
from .poly_fitter import PolyFitter
from .vex_generator import VEXGenerator
from .lens_database_manager import LensDatabaseManager

__all__ = [
    'LensImporter',
    'PolyFitter',
    'VEXGenerator',
    'LensDatabaseManager'
]
