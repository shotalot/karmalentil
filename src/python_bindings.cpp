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
    double total_lens_length;

    LensSystemWrapper() : num_elements(0), total_lens_length(0.0) {}

    /**
     * Load lens from polynomial-optics database
     */
    bool load_from_database(const std::string& id, int focal_length = 50) {
        lens_id = id;
        num_elements = lens_configuration(elements, id.c_str(), focal_length);

        if (num_elements <= 0) {
            return false;
        }

        // Calculate total lens length
        total_lens_length = 0.0;
        double zoom = 0.5;  // Mid zoom
        for (int i = 0; i < num_elements; i++) {
            total_lens_length += lens_get_thickness(elements[i], zoom);
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

            info["lens_length"] = total_lens_length;
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
 * High-performance raytracing using polynomial-optics evaluate() function
 */
class CppRaytracer {
public:
    LensSystemWrapper* lens_system;
    double zoom;

    CppRaytracer(LensSystemWrapper* ls, double z = 0.5)
        : lens_system(ls), zoom(z) {}

    /**
     * Trace a single ray through the lens system
     *
     * Uses polynomial-optics evaluate() function which traces from sensor to scene
     * Input: sensor position [x, y, 0], direction [dx, dy, 1.0] (normalized later)
     *
     * Returns: (success, exit_pos, exit_dir)
     */
    std::tuple<bool, Eigen::Vector3d, Eigen::Vector3d> trace_ray(
        const Eigen::Vector3d& sensor_pos,
        const Eigen::Vector3d& sensor_dir,
        double wavelength = 550.0) {

        // polynomial-optics uses wavelength in micrometers
        double lambda = wavelength / 1000.0;

        // Create input vector [x, y, dx, dy, lambda]
        Eigen::VectorXd in(5);
        in(0) = sensor_pos(0);
        in(1) = sensor_pos(1);

        // Normalize direction and extract x,y components
        Eigen::Vector3d dir_normalized = sensor_dir.normalized();
        in(2) = dir_normalized(0);
        in(3) = dir_normalized(1);
        in(4) = lambda;

        // Output vector
        Eigen::VectorXd out(5);
        out.setZero();

        // Call polynomial-optics evaluate() function
        // This traces from sensor through lens to scene
        int error = evaluate(lens_system->elements, lens_system->num_elements,
                           zoom, in, out, 0);

        if (error != 0) {
            // Raytracing failed (vignetted, TIR, etc.)
            return std::make_tuple(false, Eigen::Vector3d(0,0,0), Eigen::Vector3d(0,0,0));
        }

        // Extract exit position and direction from output
        // out = [x, y, dx, dy, intensity]
        Eigen::Vector3d exit_pos(out(0), out(1), 0.0);  // z=0 on exit plane
        Eigen::Vector3d exit_dir(out(2), out(3), 1.0);  // Assume forward direction
        exit_dir.normalize();

        return std::make_tuple(true, exit_pos, exit_dir);
    }

    /**
     * Trace multiple rays (batch operation)
     *
     * Input: sensor_positions [N, 3], sensor_directions [N, 3], wavelength
     * Output: (success [N], exit_positions [N, 3], exit_directions [N, 3])
     */
    std::tuple<py::array_t<bool>, py::array_t<double>, py::array_t<double>> trace_rays_batch(
        py::array_t<double> sensor_positions,
        py::array_t<double> sensor_directions,
        double wavelength = 550.0) {

        auto pos_buf = sensor_positions.request();
        auto dir_buf = sensor_directions.request();

        if (pos_buf.ndim != 2 || dir_buf.ndim != 2) {
            throw std::runtime_error("Input arrays must be 2D");
        }

        size_t num_rays = pos_buf.shape[0];

        // Allocate output arrays
        auto success = py::array_t<bool>(num_rays);
        auto exit_pos = py::array_t<double>({num_rays, (size_t)3});
        auto exit_dir = py::array_t<double>({num_rays, (size_t)3});

        auto success_ptr = success.mutable_unchecked<1>();
        auto exit_pos_ptr = exit_pos.mutable_unchecked<2>();
        auto exit_dir_ptr = exit_dir.mutable_unchecked<2>();

        auto pos_ptr = sensor_positions.unchecked<2>();
        auto dir_ptr = sensor_directions.unchecked<2>();

        // Trace each ray
        for (size_t i = 0; i < num_rays; i++) {
            Eigen::Vector3d sensor_pos(pos_ptr(i, 0), pos_ptr(i, 1), pos_ptr(i, 2));
            Eigen::Vector3d sensor_dir(dir_ptr(i, 0), dir_ptr(i, 1), dir_ptr(i, 2));

            auto [success_flag, pos, dir] = trace_ray(sensor_pos, sensor_dir, wavelength);

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
        .def(py::init<LensSystemWrapper*, double>(),
             py::arg("lens_system"),
             py::arg("zoom") = 0.5)
        .def("trace_ray", &CppRaytracer::trace_ray,
             "Trace a single ray through lens system (sensor to scene)",
             py::arg("sensor_pos"),
             py::arg("sensor_dir"),
             py::arg("wavelength") = 550.0)
        .def("trace_rays_batch", &CppRaytracer::trace_rays_batch,
             "Trace multiple rays through lens system (batch operation)",
             py::arg("sensor_positions"),
             py::arg("sensor_directions"),
             py::arg("wavelength") = 550.0);

    // Version information
    m.attr("__version__") = "0.1.1";
    m.attr("__implementation__") = "cpp";
}
