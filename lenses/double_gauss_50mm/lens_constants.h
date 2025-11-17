// Lens Constants for Double Gauss 50mm f/2.8
// These values would typically come from fitted polynomial data

#ifndef LENS_CONSTANTS_H
#define LENS_CONSTANTS_H

// Physical lens parameters
#define LENS_NAME "Double Gauss 50mm f/2.8"
#define LENS_FOCAL_LENGTH 50.0              // Effective focal length in mm
#define LENS_FSTOP_MIN 2.8                   // Maximum aperture (wide open)
#define LENS_OUTER_PUPIL_RADIUS 25.0         // Outer pupil radius in mm
#define LENS_OUTER_PUPIL_CURVATURE_RADIUS 50.0  // Radius of curvature
#define LENS_OUTER_PUPIL_CURVATURE_HEIGHT 0.0   // Height offset
#define LENS_FIELD_OF_VIEW 27.0              // Half field of view in degrees
#define LENS_APERTURE_RADIUS_AT_FSTOP_MIN 8.93  // Aperture radius at min f-stop
#define LENS_INNER_PUPIL_RADIUS 10.0         // Inner pupil radius
#define LENS_INNER_PUPIL_CURVATURE_RADIUS -30.0

// Sensor parameters
#define LENS_SENSOR_DIAGONAL 43.27           // Full frame sensor diagonal in mm
#define LENS_MAXIMUM_SENSOR_RADIUS 21.635    // Half diagonal

// Geometry types
#define LENS_GEOMETRY_PLANAR 0
#define LENS_GEOMETRY_SPHERICAL 1
#define LENS_GEOMETRY_CYLINDRICAL 2

#define LENS_OUTER_PUPIL_GEOMETRY LENS_GEOMETRY_SPHERICAL
#define LENS_INNER_PUPIL_GEOMETRY LENS_GEOMETRY_SPHERICAL

#endif // LENS_CONSTANTS_H
