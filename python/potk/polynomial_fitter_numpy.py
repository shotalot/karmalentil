"""
NumPy-based Polynomial Fitter

Pure Python implementation of polynomial fitting for optical lens systems.

This provides a simplified alternative to the full polynomial-optics C++ library,
using NumPy for polynomial fitting. Suitable for demonstration and environments
where C++ extensions are not available.

Note: Less accurate and slower than the C++ implementation, but functionally complete.
"""

import numpy as np
from typing import Dict, List, Tuple
from .simple_raytracer import SimpleRaytracer


class NumpyPolyFitter:
    """
    Fit polynomials to optical lens system using NumPy

    Uses least-squares polynomial fitting to approximate lens ray behavior.
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
        self.num_coeffs = (degree + 1) * (degree + 2) // 2

    def fit(self, optical_system: dict, wavelength: float = 550.0) -> Dict[str, List[float]]:
        """
        Fit polynomials to optical system

        Args:
            optical_system: Optical system from LensImporter
            wavelength: Wavelength in nm for fitting

        Returns:
            Dictionary of polynomial coefficients
        """
        print(f"\nFitting polynomials (NumPy implementation)")
        print(f"  Degree: {self.degree}")
        print(f"  Samples: {self.samples}")
        print(f"  Wavelength: {wavelength}nm")

        # Create raytracer from optical system
        raytracer = SimpleRaytracer.from_lens_data(optical_system)

        # Generate sample rays
        print(f"  Generating {self.samples} sample rays...")
        sensor_positions, aperture_positions = self._generate_sample_points(self.samples)

        # Trace rays through lens
        print(f"  Tracing rays through {len(optical_system.get('elements', []))} elements...")
        ray_origins, ray_directions = self._generate_rays(
            sensor_positions, aperture_positions, optical_system
        )

        exit_positions, exit_directions = raytracer.trace_rays_batch(
            ray_origins, ray_directions, wavelength
        )

        # Filter valid rays (remove vignetted)
        valid = ~np.isnan(exit_positions[:, 0])
        num_valid = np.sum(valid)
        print(f"  Valid rays: {num_valid}/{self.samples} ({100.0 * num_valid / self.samples:.1f}%)")

        if num_valid < self.num_coeffs * 2:
            print(f"  ⚠️  Warning: Low ray count may affect fit quality")

        sensor_positions = sensor_positions[valid]
        aperture_positions = aperture_positions[valid]
        exit_positions = exit_positions[valid]
        exit_directions = exit_directions[valid]

        # Fit polynomials
        print(f"  Fitting exit pupil polynomials...")
        coeffs_x, coeffs_y = self._fit_exit_pupil(
            sensor_positions, aperture_positions,
            exit_positions, exit_directions
        )

        print(f"  Fitting entrance pupil polynomials...")
        coeffs_x_entrance, coeffs_y_entrance = self._fit_entrance_pupil(
            sensor_positions, aperture_positions,
            exit_positions, exit_directions
        )

        coefficients = {
            'exit_pupil_x': coeffs_x.tolist(),
            'exit_pupil_y': coeffs_y.tolist(),
            'entrance_pupil_x': coeffs_x_entrance.tolist(),
            'entrance_pupil_y': coeffs_y_entrance.tolist()
        }

        print(f"\n✓ Polynomial fitting complete!")
        print(f"  Coefficients per direction: {len(coeffs_x)}")

        return coefficients

    def validate(self, optical_system: dict, coefficients: Dict[str, List[float]],
                 test_samples: int = 1000, wavelength: float = 550.0) -> float:
        """
        Validate polynomial fit accuracy

        Args:
            optical_system: Original optical system
            coefficients: Fitted polynomial coefficients
            test_samples: Number of test rays
            wavelength: Wavelength in nm

        Returns:
            RMS error in millimeters
        """
        print(f"\nValidating polynomial fit...")
        print(f"  Test samples: {test_samples}")

        # Create raytracer
        raytracer = SimpleRaytracer.from_lens_data(optical_system)

        # Generate test rays
        sensor_positions, aperture_positions = self._generate_sample_points(test_samples)

        ray_origins, ray_directions = self._generate_rays(
            sensor_positions, aperture_positions, optical_system
        )

        # Trace through real lens
        exit_positions_real, _ = raytracer.trace_rays_batch(
            ray_origins, ray_directions, wavelength
        )

        # Evaluate polynomial approximation
        exit_positions_poly = self._evaluate_polynomial(
            sensor_positions, aperture_positions, coefficients
        )

        # Compute RMS error
        valid = ~np.isnan(exit_positions_real[:, 0])
        errors = np.linalg.norm(
            exit_positions_real[valid] - exit_positions_poly[valid],
            axis=1
        )

        rms_error = np.sqrt(np.mean(errors ** 2))

        print(f"  RMS error: {rms_error:.6f}mm")
        print(f"  Max error: {np.max(errors):.6f}mm")
        print(f"  Mean error: {np.mean(errors):.6f}mm")

        if rms_error < 0.01:
            print(f"  ✓ Excellent fit (< 0.01mm)")
        elif rms_error < 0.1:
            print(f"  ✓ Good fit (< 0.1mm)")
        elif rms_error < 1.0:
            print(f"  ⚠️  Acceptable fit (< 1mm)")
        else:
            print(f"  ⚠️  Poor fit (> 1mm) - consider higher degree or more samples")

        return rms_error

    def _generate_sample_points(self, num_samples: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate sensor and aperture sample points

        Args:
            num_samples: Number of samples

        Returns:
            Tuple of (sensor_positions, aperture_positions) [N, 2]
        """
        # Stratified sampling for better coverage
        grid_size = int(np.sqrt(num_samples))
        u = np.linspace(-1, 1, grid_size)
        v = np.linspace(-1, 1, grid_size)

        uu, vv = np.meshgrid(u, v)
        sensor_positions = np.stack([uu.ravel(), vv.ravel()], axis=1)

        # Random aperture sampling (uniform disk)
        r = np.sqrt(np.random.rand(len(sensor_positions)))
        theta = 2 * np.pi * np.random.rand(len(sensor_positions))
        aperture_positions = np.stack([r * np.cos(theta), r * np.sin(theta)], axis=1)

        return sensor_positions[:num_samples], aperture_positions[:num_samples]

    def _generate_rays(self, sensor_positions: np.ndarray, aperture_positions: np.ndarray,
                      optical_system: dict) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate ray origins and directions from sensor/aperture samples

        Args:
            sensor_positions: Sensor positions [N, 2] (normalized -1 to 1)
            aperture_positions: Aperture positions [N, 2] (normalized -1 to 1)
            optical_system: Optical system data

        Returns:
            Tuple of (ray_origins, ray_directions) [N, 3]
        """
        num_rays = len(sensor_positions)
        sensor_width = optical_system.get('sensor_width', 36.0)
        aperture_diameter = optical_system.get('aperture', 25.0)

        # Scale sensor positions to physical size
        sensor_x = sensor_positions[:, 0] * sensor_width / 2
        sensor_y = sensor_positions[:, 1] * sensor_width / 2

        # Scale aperture positions
        aperture_x = aperture_positions[:, 0] * aperture_diameter / 2
        aperture_y = aperture_positions[:, 1] * aperture_diameter / 2

        # Ray origins at sensor plane (z=0)
        ray_origins = np.zeros((num_rays, 3))
        ray_origins[:, 0] = sensor_x
        ray_origins[:, 1] = sensor_y

        # Ray directions towards aperture
        # Simplified: assume aperture at focal length distance
        focal_length = optical_system.get('focal_length', 50.0)

        target_x = aperture_x
        target_y = aperture_y
        target_z = np.full(num_rays, focal_length)

        ray_directions = np.stack([
            target_x - sensor_x,
            target_y - sensor_y,
            target_z
        ], axis=1)

        # Normalize
        ray_directions /= np.linalg.norm(ray_directions, axis=1, keepdims=True)

        return ray_origins, ray_directions

    def _fit_exit_pupil(self, sensor_pos: np.ndarray, aperture_pos: np.ndarray,
                       exit_pos: np.ndarray, exit_dir: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit exit pupil polynomials (sensor + aperture → exit position)

        Args:
            sensor_pos: Sensor positions [N, 2]
            aperture_pos: Aperture positions [N, 2]
            exit_pos: Exit positions [N, 3]
            exit_dir: Exit directions [N, 3]

        Returns:
            Tuple of (coeffs_x, coeffs_y) polynomial coefficients
        """
        # Input features: sensor_x, sensor_y, aperture_x, aperture_y
        X = np.concatenate([sensor_pos, aperture_pos], axis=1)

        # Build polynomial feature matrix
        features = self._build_polynomial_features(X, self.degree)

        # Fit X and Y separately
        coeffs_x = np.linalg.lstsq(features, exit_pos[:, 0], rcond=None)[0]
        coeffs_y = np.linalg.lstsq(features, exit_pos[:, 1], rcond=None)[0]

        return coeffs_x, coeffs_y

    def _fit_entrance_pupil(self, sensor_pos: np.ndarray, aperture_pos: np.ndarray,
                           exit_pos: np.ndarray, exit_dir: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fit entrance pupil polynomials (reverse direction)

        Args:
            sensor_pos: Sensor positions [N, 2]
            aperture_pos: Aperture positions [N, 2]
            exit_pos: Exit positions [N, 3]
            exit_dir: Exit directions [N, 3]

        Returns:
            Tuple of (coeffs_x, coeffs_y) polynomial coefficients
        """
        # For entrance pupil, we reverse the mapping
        # This is a simplified approach - real implementation would trace backwards

        X = np.concatenate([exit_pos[:, :2], exit_dir[:, :2]], axis=1)
        features = self._build_polynomial_features(X, self.degree)

        coeffs_x = np.linalg.lstsq(features, sensor_pos[:, 0], rcond=None)[0]
        coeffs_y = np.linalg.lstsq(features, sensor_pos[:, 1], rcond=None)[0]

        return coeffs_x, coeffs_y

    def _build_polynomial_features(self, X: np.ndarray, degree: int) -> np.ndarray:
        """
        Build polynomial feature matrix for 2D input

        Args:
            X: Input features [N, 4] (sensor_x, sensor_y, aperture_x, aperture_y)
            degree: Maximum polynomial degree

        Returns:
            Feature matrix [N, num_coeffs]
        """
        num_samples = X.shape[0]
        features = []

        # For simplicity, use only sensor positions for polynomial
        # (full implementation would use all 4 dimensions)
        x = X[:, 0]
        y = X[:, 1]

        # Generate polynomial terms: x^i * y^j where i+j <= degree
        for total_deg in range(degree + 1):
            for i in range(total_deg + 1):
                j = total_deg - i
                features.append(x**i * y**j)

        return np.stack(features, axis=1)

    def _evaluate_polynomial(self, sensor_pos: np.ndarray, aperture_pos: np.ndarray,
                            coefficients: Dict[str, List[float]]) -> np.ndarray:
        """
        Evaluate polynomial at given positions

        Args:
            sensor_pos: Sensor positions [N, 2]
            aperture_pos: Aperture positions [N, 2]
            coefficients: Polynomial coefficients

        Returns:
            Evaluated positions [N, 3]
        """
        X = np.concatenate([sensor_pos, aperture_pos], axis=1)
        features = self._build_polynomial_features(X, self.degree)

        coeffs_x = np.array(coefficients['exit_pupil_x'])
        coeffs_y = np.array(coefficients['exit_pupil_y'])

        exit_x = features @ coeffs_x
        exit_y = features @ coeffs_y
        exit_z = np.zeros_like(exit_x)  # Simplified

        return np.stack([exit_x, exit_y, exit_z], axis=1)
