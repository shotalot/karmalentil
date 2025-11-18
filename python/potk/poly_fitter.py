"""
Polynomial Fitting System

Fits high-degree polynomials to optical lens systems.

This module interfaces with the polynomial-optics C++ library to:
- Sample ray paths through lens system
- Fit polynomials to ray behavior
- Validate polynomial accuracy
- Measure RMS error

If C++ library is not available, falls back to NumPy implementation.
"""

from typing import Dict, List, Optional, Tuple

# Try to import C++ bindings, fall back to NumPy implementation
try:
    from .polynomial_optics_binding import PolyFitter as CppPolyFitter
    HAS_CPP_BINDING = True
except ImportError:
    HAS_CPP_BINDING = False
    from .polynomial_fitter_numpy import NumpyPolyFitter


class PolyFitter:
    """
    Polynomial fitter for optical lens systems

    Automatically uses C++ polynomial-optics library if available,
    otherwise falls back to NumPy implementation.
    """

    def __init__(self, degree: int = 7, samples: int = 10000):
        """
        Initialize polynomial fitter

        Args:
            degree: Polynomial degree (typically 5-9)
            samples: Number of ray samples for fitting
        """
        self.degree = degree
        self.samples = samples

        # Initialize appropriate implementation
        if HAS_CPP_BINDING:
            self._fitter = CppPolyFitter(degree, samples)
            self._implementation = 'cpp'
        else:
            self._fitter = NumpyPolyFitter(degree, samples)
            self._implementation = 'numpy'

    def fit(self, optical_system, validation_samples: int = 5000) -> Dict[str, List[float]]:
        """
        Fit polynomials to optical system

        Args:
            optical_system: Optical system from LensImporter
            validation_samples: Additional samples for validation

        Returns:
            Dictionary of polynomial coefficients:
                - 'exit_pupil_x': X coefficients
                - 'exit_pupil_y': Y coefficients
                - 'entrance_pupil_x': X coefficients (reverse)
                - 'entrance_pupil_y': Y coefficients (reverse)
        """
        if self._implementation == 'numpy':
            print(f"  Using NumPy implementation (C++ polynomial-optics not available)")

        return self._fitter.fit(optical_system)

    def validate(self, optical_system, coefficients: Dict[str, List[float]],
                 test_samples: int = 1000) -> float:
        """
        Validate polynomial fit accuracy

        Args:
            optical_system: Original optical system
            coefficients: Fitted polynomial coefficients
            test_samples: Number of test rays

        Returns:
            RMS error in millimeters
        """
        return self._fitter.validate(optical_system, coefficients, test_samples)

    def optimize_degree(self, optical_system,
                       min_degree: int = 5,
                       max_degree: int = 9,
                       target_error: float = 0.01) -> Tuple[int, float]:
        """
        Find optimal polynomial degree for target accuracy

        Args:
            optical_system: Optical system to fit
            min_degree: Minimum degree to try
            max_degree: Maximum degree to try
            target_error: Target RMS error in mm

        Returns:
            Tuple of (optimal_degree, achieved_error)
        """
        print(f"\nOptimizing polynomial degree (target error: {target_error}mm)...")

        best_degree = min_degree
        best_error = float('inf')

        for degree in range(min_degree, max_degree + 1):
            self.degree = degree
            self._fitter.degree = degree  # Update underlying implementation
            coeffs = self.fit(optical_system)
            error = self.validate(optical_system, coeffs)

            print(f"  Degree {degree}: RMS = {error:.6f}mm")

            if error < best_error:
                best_degree = degree
                best_error = error

            if error <= target_error:
                print(f"  ✓ Target error achieved at degree {degree}")
                break

        return best_degree, best_error

    def compute_vignetting(self, optical_system, coefficients: Dict[str, List[float]]) -> Dict:
        """
        Compute vignetting map for lens housing

        Args:
            optical_system: Optical system
            coefficients: Fitted coefficients

        Returns:
            Vignetting data structure
        """
        # TODO: Compute vignetting from lens housing geometry
        # This requires raytracing through physical lens barrel

        return {
            'has_vignetting': False,
            'vignetting_map': None
        }
