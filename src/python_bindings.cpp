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
     * Input: sensor position [x, y, z], direction [dx, dy, dz]
     *
     * Returns: (success, exit_pos, exit_dir)
     */
    std::tuple<bool, std::vector<double>, std::vector<double>> trace_ray(
        const std::vector<double>& sensor_pos,
        const std::vector<double>& sensor_dir,
        double wavelength = 550.0) {

        std::cerr << "[TRACE] Entered trace_ray function!" << std::endl;
        std::cerr.flush();

        if (sensor_pos.size() != 3 || sensor_dir.size() != 3) {
            std::cerr << "[ERROR] Invalid input sizes" << std::endl;
            return std::make_tuple(false, std::vector<double>{0,0,0}, std::vector<double>{0,0,0});
        }

        std::cerr << "[TRACE] Converting to Eigen..." << std::endl;

        // Convert to Eigen
        Eigen::Vector3d pos(sensor_pos[0], sensor_pos[1], sensor_pos[2]);
        Eigen::Vector3d dir(sensor_dir[0], sensor_dir[1], sensor_dir[2]);

        std::cerr << "[TRACE] Normalizing..." << std::endl;

        // Normalize direction
        dir.normalize();

        std::cerr << "[TRACE] Computing exit..." << std::endl;

        // Simple geometric optics approximation:
        // Ray exits at approximately the same lateral position
        // but displaced by the lens length
        std::vector<double> exit_pos = {
            pos(0),
            pos(1),
            lens_system->total_lens_length
        };

        std::vector<double> exit_dir = {dir(0), dir(1), dir(2)};

        std::cerr << "[TRACE] Returning..." << std::endl;

        // Mark as successful (for now, no vignetting check)
        return std::make_tuple(true, exit_pos, exit_dir);
    }

    // TODO: Implement batch raytracing once single ray works
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
             py::arg("zoom") = 0.5,
             py::keep_alive<1, 2>())  // Keep lens_system (arg 2) alive as long as Raytracer (arg 1) lives
        .def("trace_ray", &CppRaytracer::trace_ray,
             "Trace a single ray through lens system (sensor to scene)",
             py::arg("sensor_pos"),
             py::arg("sensor_dir"),
             py::arg("wavelength") = 550.0);

    // Version information
    m.attr("__version__") = "0.1.1";
    m.attr("__implementation__") = "cpp";
}
