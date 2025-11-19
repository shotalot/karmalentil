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


def fit_polynomial_from_data(sensor_positions, sensor_directions,
                              exit_positions, exit_directions, degree=5):
    """
    Fit polynomial coefficients from raw ray data

    Args:
        sensor_positions: Array of sensor positions [N, 3] or [N, 2]
        sensor_directions: Array of sensor directions [N, 3] or [N, 2]
        exit_positions: Array of exit pupil positions [N, 3] or [N, 2]
        exit_directions: Array of exit pupil directions [N, 3] or [N, 2]
        degree: Polynomial degree

    Returns:
        Dictionary of polynomial coefficients
    """
    import numpy as np
    from numpy.polynomial import polynomial as P

    # Convert to 2D if needed (take x,y components)
    if sensor_positions.shape[1] == 3:
        sensor_pos_2d = sensor_positions[:, :2]
        exit_pos_2d = exit_positions[:, :2]
    else:
        sensor_pos_2d = sensor_positions
        exit_pos_2d = exit_positions

    # Build polynomial basis matrix
    # For 2D polynomial: sum over i,j of c_ij * x^i * y^j
    num_samples = len(sensor_pos_2d)
    num_coeffs = (degree + 1) * (degree + 2) // 2

    # Create design matrix
    A = np.zeros((num_samples, num_coeffs))

    idx = 0
    for total_deg in range(degree + 1):
        for i in range(total_deg + 1):
            j = total_deg - i

            # Evaluate x^i * y^j for all samples
            A[:, idx] = (sensor_pos_2d[:, 0] ** i) * (sensor_pos_2d[:, 1] ** j)
            idx += 1

    # Solve least squares for X and Y separately
    coeffs_x, residuals_x, rank_x, s_x = np.linalg.lstsq(A, exit_pos_2d[:, 0], rcond=None)
    coeffs_y, residuals_y, rank_y, s_y = np.linalg.lstsq(A, exit_pos_2d[:, 1], rcond=None)

    # Return in polynomial-optics format
    return {
        'exit_pupil_x': coeffs_x,
        'exit_pupil_y': coeffs_y,
        'degree': degree,
        'num_samples': num_samples,
        'residuals_x': residuals_x[0] if len(residuals_x) > 0 else 0.0,
        'residuals_y': residuals_y[0] if len(residuals_y) > 0 else 0.0
    }
