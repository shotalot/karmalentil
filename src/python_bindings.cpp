/**
 * POTK - Polynomial Optics to Karma
 * Python bindings for polynomial-optics library
 *
 * This file uses pybind11 to expose C++ polynomial-optics functionality
 * to Python for use in Houdini.
 */

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include <pybind11/eigen.h>

// Include polynomial-optics headers
#include "../ext/lentil/polynomial-optics/src/lenssystem.h"
#include "../ext/lentil/polynomial-optics/src/raytrace.h"
#include "../ext/lentil/polynomial-optics/src/spectrum.h"
#include "../ext/lentil/polynomial-optics/src/poly.h"

#include <vector>
#include <string>
#include <cmath>

namespace py = pybind11;

/**
 * Lens System Wrapper
 *
 * Wraps polynomial-optics lens system for Python access
 */
class LensSystemWrapper {
public:
    std::vector<lens_element_t> elements;
    int num_elements;
    std::string lens_id;

    LensSystemWrapper() : num_elements(0) {}

    /**
     * Load lens from polynomial-optics database
     */
    bool load_from_database(const std::string& id, int focal_length = 50) {
        lens_id = id;
        num_elements = lens_configuration(elements, id.c_str(), focal_length);

        if (num_elements <= 0) {
            return false;
        }

        return true;
    }

    /**
     * Get lens metadata
     */
    py::dict get_lens_info() const {
        py::dict info;
        info["lens_id"] = lens_id;
        info["num_elements"] = num_elements;

        if (num_elements > 0) {
            // Calculate approximate focal length
            double focal_length = 50.0;  // Default
            info["focal_length"] = focal_length;

            // Get aperture information
            double aperture_radius = lens_get_aperture_radius(elements, num_elements);
            info["aperture_radius"] = aperture_radius;

            double aperture_pos = lens_get_aperture_pos(elements, num_elements, 0.5);
            info["aperture_position"] = aperture_pos;
        }

        return info;
    }

    /**
     * Get element information for inspection
     */
    py::list get_elements() const {
        py::list result;

        for (int i = 0; i < num_elements; i++) {
            py::dict elem;
            elem["radius"] = elements[i].lens_radius;
            elem["thickness"] = elements[i].thickness_mid;
            elem["ior"] = elements[i].ior;
            elem["housing_radius"] = elements[i].housing_radius;
            elem["material"] = elements[i].material;
            result.append(elem);
        }

        return result;
    }
};

/**
 * C++ Raytracer Wrapper
 *
 * High-performance raytracing using polynomial-optics
 */
class CppRaytracer {
public:
    LensSystemWrapper* lens_system;

    CppRaytracer(LensSystemWrapper* ls) : lens_system(ls) {}

    /**
     * Trace a single ray through the lens system
     *
     * Returns: (success, exit_pos, exit_dir)
     */
    std::tuple<bool, Eigen::Vector3d, Eigen::Vector3d> trace_ray(
        const Eigen::Vector3d& origin,
        const Eigen::Vector3d& direction,
        double wavelength = 550.0) {

        Eigen::Vector3d pos = origin;
        Eigen::Vector3d dir = direction;
        dir.normalize();

        double lambda = wavelength / 1000.0;  // Convert nm to micrometers
        double zoom = 0.5;  // Mid zoom position

        // Trace through each lens element
        for (int i = 0; i < lens_system->num_elements; i++) {
            const lens_element_t& elem = lens_system->elements[i];

            // Skip aperture (iris)
            if (stringcmp(elem.material, "iris")) {
                // Just propagate through aperture
                double thickness = lens_get_thickness(elem, zoom);
                for (int k = 0; k < 3; k++) {
                    pos(k) += dir(k) * thickness;
                }

                // Check if vignetted
                double r2 = pos(0)*pos(0) + pos(1)*pos(1);
                if (r2 > elem.housing_radius * elem.housing_radius) {
                    return std::make_tuple(false, Eigen::Vector3d(0,0,0), Eigen::Vector3d(0,0,0));
                }
                continue;
            }

            // Intersect with lens surface
            Eigen::Vector3d normal;
            double dist = 0;
            double thickness = lens_get_thickness(elem, zoom);
            double center = 0;  // Surface center position

            int error = 0;
            if (elem.aspheric) {
                error = aspherical(pos, dir, dist, elem.lens_radius, center,
                                 0, elem.aspheric_correction_coefficients,
                                 elem.housing_radius, normal);
            } else {
                error = spherical(pos, dir, dist, elem.lens_radius, center,
                                elem.housing_radius, normal);
            }

            if (error != 0) {
                // Ray missed surface or was vignetted
                return std::make_tuple(false, Eigen::Vector3d(0,0,0), Eigen::Vector3d(0,0,0));
            }

            // Refract at surface (Snell's law)
            double n1 = 1.0;  // Previous IOR (air or previous element)
            double n2 = elem.ior;

            // Get IOR for wavelength (simplified - would need proper dispersion)
            // For now use fixed IOR

            double cos_i = -raytrace_dot(dir, normal);
            if (cos_i < 0) {
                cos_i = -cos_i;
                normal = -normal;
                std::swap(n1, n2);
            }

            double eta = n1 / n2;
            double k = 1.0 - eta * eta * (1.0 - cos_i * cos_i);

            if (k < 0) {
                // Total internal reflection
                return std::make_tuple(false, Eigen::Vector3d(0,0,0), Eigen::Vector3d(0,0,0));
            }

            // Refracted direction
            dir = eta * dir + (eta * cos_i - std::sqrt(k)) * normal;
            raytrace_normalise(dir);

            // Propagate to next surface
            for (int k = 0; k < 3; k++) {
                pos(k) += dir(k) * thickness;
            }
        }

        return std::make_tuple(true, pos, dir);
    }

    /**
     * Trace multiple rays (batch operation)
     *
     * Input: origins [N, 3], directions [N, 3], wavelength
     * Output: (success [N], exit_positions [N, 3], exit_directions [N, 3])
     */
    std::tuple<py::array_t<bool>, py::array_t<double>, py::array_t<double>> trace_rays_batch(
        py::array_t<double> origins,
        py::array_t<double> directions,
        double wavelength = 550.0) {

        auto origins_buf = origins.request();
        auto directions_buf = directions.request();

        if (origins_buf.ndim != 2 || directions_buf.ndim != 2) {
            throw std::runtime_error("Input arrays must be 2D");
        }

        size_t num_rays = origins_buf.shape[0];

        // Allocate output arrays
        auto success = py::array_t<bool>(num_rays);
        auto exit_pos = py::array_t<double>({num_rays, (size_t)3});
        auto exit_dir = py::array_t<double>({num_rays, (size_t)3});

        auto success_ptr = success.mutable_unchecked<1>();
        auto exit_pos_ptr = exit_pos.mutable_unchecked<2>();
        auto exit_dir_ptr = exit_dir.mutable_unchecked<2>();

        auto origins_ptr = origins.unchecked<2>();
        auto directions_ptr = directions.unchecked<2>();

        // Trace each ray
        for (size_t i = 0; i < num_rays; i++) {
            Eigen::Vector3d origin(origins_ptr(i, 0), origins_ptr(i, 1), origins_ptr(i, 2));
            Eigen::Vector3d direction(directions_ptr(i, 0), directions_ptr(i, 1), directions_ptr(i, 2));

            auto [success_flag, pos, dir] = trace_ray(origin, direction, wavelength);

            success_ptr(i) = success_flag;

            if (success_flag) {
                for (int k = 0; k < 3; k++) {
                    exit_pos_ptr(i, k) = pos(k);
                    exit_dir_ptr(i, k) = dir(k);
                }
            } else {
                for (int k = 0; k < 3; k++) {
                    exit_pos_ptr(i, k) = std::numeric_limits<double>::quiet_NaN();
                    exit_dir_ptr(i, k) = std::numeric_limits<double>::quiet_NaN();
                }
            }
        }

        return std::make_tuple(success, exit_pos, exit_dir);
    }
};

/**
 * pybind11 Module Definition
 *
 * Exposes C++ classes and functions to Python
 */
PYBIND11_MODULE(polynomial_optics_binding, m) {
    m.doc() = "Python bindings for polynomial-optics library (POTK) - C++ implementation";

    // LensSystem class
    py::class_<LensSystemWrapper>(m, "LensSystem")
        .def(py::init<>())
        .def("load_from_database", &LensSystemWrapper::load_from_database,
             "Load lens design from polynomial-optics database",
             py::arg("lens_id"),
             py::arg("focal_length") = 50)
        .def("get_lens_info", &LensSystemWrapper::get_lens_info,
             "Get lens metadata")
        .def("get_elements", &LensSystemWrapper::get_elements,
             "Get list of lens elements");

    // Raytracer class
    py::class_<CppRaytracer>(m, "Raytracer")
        .def(py::init<LensSystemWrapper*>(),
             py::arg("lens_system"))
        .def("trace_ray", &CppRaytracer::trace_ray,
             "Trace a single ray through lens system",
             py::arg("origin"),
             py::arg("direction"),
             py::arg("wavelength") = 550.0)
        .def("trace_rays_batch", &CppRaytracer::trace_rays_batch,
             "Trace multiple rays through lens system (batch operation)",
             py::arg("origins"),
             py::arg("directions"),
             py::arg("wavelength") = 550.0);

    // Version information
    m.attr("__version__") = "0.1.0";
    m.attr("__implementation__") = "cpp";
}
