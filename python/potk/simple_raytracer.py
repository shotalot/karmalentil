"""
Simple Optical Raytracer

Simplified geometric optics raytracer for polynomial fitting and validation.

This is a Python-only implementation for environments where the C++ polynomial-optics
library is not available. It provides basic optical raytracing using Snell's law.

Note: This is less accurate than the full polynomial-optics C++ implementation,
      but sufficient for demonstration and workflow testing.
"""

import numpy as np
from typing import List, Tuple, Optional


class SimpleLensElement:
    """
    Represents a single lens element (surface)
    """

    def __init__(self, radius: float, thickness: float,
                 material: str = 'air', diameter: float = 50.0):
        """
        Args:
            radius: Radius of curvature (mm) - positive = convex towards object
            thickness: Distance to next surface (mm)
            material: Optical material (e.g., 'N-BK7', 'SF5', 'air')
            diameter: Clear aperture diameter (mm)
        """
        self.radius = radius
        self.thickness = thickness
        self.material = material
        self.diameter = diameter

        # Refractive indices (simplified - wavelength 550nm)
        self._index_map = {
            'air': 1.0,
            'N-BK7': 1.5168,
            'N-SK16': 1.6204,
            'N-LAK21': 1.6405,
            'SF5': 1.6727,
            'N-SF6': 1.8052,
            'N-LASF9': 1.8501
        }

    def get_index(self, wavelength: float = 550.0) -> float:
        """
        Get refractive index for wavelength

        Args:
            wavelength: Wavelength in nm (default: 550nm green)

        Returns:
            Refractive index
        """
        base_index = self._index_map.get(self.material, 1.0)

        # Simple dispersion model (Cauchy equation approximation)
        if base_index > 1.0 and wavelength != 550.0:
            # Adjust index based on wavelength
            wl_factor = (550.0 / wavelength) ** 2
            dispersion = (base_index - 1.0) * 0.01  # ~1% dispersion
            base_index += dispersion * (wl_factor - 1.0)

        return base_index


class SimpleRaytracer:
    """
    Simplified optical raytracer for lens systems

    Implements basic geometric optics using Snell's law for refraction.
    """

    def __init__(self, lens_elements: List[SimpleLensElement]):
        """
        Args:
            lens_elements: List of lens elements (surfaces)
        """
        self.elements = lens_elements

    @classmethod
    def from_lens_data(cls, lens_data: dict) -> 'SimpleRaytracer':
        """
        Create raytracer from lens design data

        Args:
            lens_data: Lens design dictionary

        Returns:
            SimpleRaytracer instance
        """
        elements = []

        for elem in lens_data.get('elements', []):
            element = SimpleLensElement(
                radius=elem.get('radius', 0.0),
                thickness=elem.get('thickness', 0.0),
                material=elem.get('material', 'air'),
                diameter=elem.get('diameter', 50.0)
            )
            elements.append(element)

        return cls(elements)

    def trace_ray(self, ray_origin: np.ndarray, ray_direction: np.ndarray,
                  wavelength: float = 550.0) -> Tuple[Optional[np.ndarray],
                                                       Optional[np.ndarray]]:
        """
        Trace a single ray through the lens system

        Args:
            ray_origin: Ray origin position [x, y, z] in mm
            ray_direction: Ray direction [dx, dy, dz] (normalized)
            wavelength: Wavelength in nm

        Returns:
            Tuple of (exit_position, exit_direction) or (None, None) if ray fails
        """
        pos = ray_origin.copy()
        direction = ray_direction / np.linalg.norm(ray_direction)
        current_index = 1.0  # Air

        for i, element in enumerate(self.elements):
            # Propagate to surface
            if abs(element.radius) < 1e-6:
                # Flat surface
                t = element.thickness / direction[2]
            else:
                # Curved surface - intersect with sphere
                t = self._intersect_sphere(pos, direction, element.radius)
                if t is None:
                    return None, None  # Ray missed surface

            pos = pos + t * direction

            # Check if ray is vignetted by aperture
            r = np.sqrt(pos[0]**2 + pos[1]**2)
            if r > element.diameter / 2:
                return None, None  # Vignetted

            # Refract at surface (Snell's law)
            next_index = element.get_index(wavelength)

            if abs(element.radius) > 1e-6:
                # Compute surface normal
                if element.radius > 0:
                    normal = pos / element.radius
                else:
                    normal = -pos / abs(element.radius)
                normal = normal / np.linalg.norm(normal)

                # Snell's law
                direction = self._refract(direction, normal, current_index, next_index)
                if direction is None:
                    return None, None  # Total internal reflection

            current_index = next_index

        return pos, direction

    def trace_rays_batch(self, ray_origins: np.ndarray, ray_directions: np.ndarray,
                        wavelength: float = 550.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Trace multiple rays through lens system

        Args:
            ray_origins: Array of ray origins [N, 3]
            ray_directions: Array of ray directions [N, 3]
            wavelength: Wavelength in nm

        Returns:
            Tuple of (exit_positions, exit_directions) [N, 3]
        """
        num_rays = ray_origins.shape[0]
        exit_pos = np.zeros((num_rays, 3))
        exit_dir = np.zeros((num_rays, 3))

        for i in range(num_rays):
            pos, direction = self.trace_ray(ray_origins[i], ray_directions[i], wavelength)

            if pos is not None:
                exit_pos[i] = pos
                exit_dir[i] = direction
            else:
                # Mark failed ray
                exit_pos[i] = np.array([np.nan, np.nan, np.nan])
                exit_dir[i] = np.array([np.nan, np.nan, np.nan])

        return exit_pos, exit_dir

    def _intersect_sphere(self, ray_origin: np.ndarray, ray_dir: np.ndarray,
                         radius: float) -> Optional[float]:
        """
        Intersect ray with sphere of given radius

        Args:
            ray_origin: Ray origin [x, y, z]
            ray_dir: Ray direction [dx, dy, dz] (normalized)
            radius: Sphere radius

        Returns:
            Distance t to intersection, or None if no intersection
        """
        # Sphere is centered on z-axis at current position
        # Simplified: assume sphere center at origin of local coordinate system

        a = np.dot(ray_dir, ray_dir)
        b = 2.0 * np.dot(ray_origin, ray_dir)
        c = np.dot(ray_origin, ray_origin) - radius ** 2

        discriminant = b ** 2 - 4 * a * c

        if discriminant < 0:
            return None  # No intersection

        # Take closest positive intersection
        sqrt_d = np.sqrt(discriminant)
        t1 = (-b + sqrt_d) / (2 * a)
        t2 = (-b - sqrt_d) / (2 * a)

        if t1 > 1e-6:
            return t1
        elif t2 > 1e-6:
            return t2

        return None

    def _refract(self, incident: np.ndarray, normal: np.ndarray,
                 n1: float, n2: float) -> Optional[np.ndarray]:
        """
        Compute refracted ray direction using Snell's law

        Args:
            incident: Incident ray direction (normalized)
            normal: Surface normal (normalized)
            n1: Refractive index of incident medium
            n2: Refractive index of refracted medium

        Returns:
            Refracted direction, or None if total internal reflection
        """
        cos_i = -np.dot(incident, normal)

        # Handle ray coming from either side of surface
        if cos_i < 0:
            cos_i = -cos_i
            normal = -normal

        eta = n1 / n2
        k = 1.0 - eta ** 2 * (1.0 - cos_i ** 2)

        if k < 0:
            return None  # Total internal reflection

        refracted = eta * incident + (eta * cos_i - np.sqrt(k)) * normal
        return refracted / np.linalg.norm(refracted)

    def compute_focal_length(self, samples: int = 100) -> float:
        """
        Estimate focal length by tracing parallel rays

        Args:
            samples: Number of ray samples

        Returns:
            Estimated focal length in mm
        """
        # Trace collimated rays parallel to axis
        ray_origins = np.zeros((samples, 3))
        ray_origins[:, 0] = np.linspace(-5, 5, samples)  # Spread across 10mm diameter

        ray_directions = np.tile([0, 0, 1], (samples, 1))

        exit_pos, exit_dir = self.trace_rays_batch(ray_origins, ray_directions)

        # Find where rays cross optical axis (z-axis)
        # Focal point: where x=0, y=0

        valid = ~np.isnan(exit_pos[:, 0])
        if not np.any(valid):
            return 0.0

        # Compute focal point as average crossing point
        focal_distances = []
        for i in np.where(valid)[0]:
            # How far along ray until x=0?
            if abs(exit_dir[i, 0]) > 1e-6:
                t = -exit_pos[i, 0] / exit_dir[i, 0]
                focal_z = exit_pos[i, 2] + t * exit_dir[i, 2]
                focal_distances.append(focal_z)

        if focal_distances:
            return np.mean(focal_distances)

        return 0.0
