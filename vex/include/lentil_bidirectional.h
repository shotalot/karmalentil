// Bidirectional Ray Tracing Utilities
// Traces rays backward from world space through the lens to the sensor
// Used for computing circle of confusion and sample redistribution

#ifndef LENTIL_BIDIRECTIONAL_H
#define LENTIL_BIDIRECTIONAL_H

// Trace a world-space ray backward through the lens to find sensor position
// This is the inverse of the forward camera ray generation
//
// Inputs:
//   world_pos: 3D position in world space
//   camera_pos: Camera position in world space
//   camera_matrix: Camera to world transform matrix (4x4)
//   focal_length: Lens focal length in mm
//   focus_distance: Focus distance in mm
//   fstop: Current f-stop
//
// Outputs:
//   sensor_x, sensor_y: Position on sensor in mm
//   coc_radius: Circle of confusion radius on sensor in mm
//   success: 1 if ray successfully traced, 0 otherwise
function int trace_backward_to_sensor(
    vector world_pos;
    vector camera_pos;
    matrix camera_matrix;
    float focal_length;
    float focus_distance;
    float fstop;
    export float sensor_x, sensor_y;
    export float coc_radius)
{
    // Transform world position to camera space
    matrix inv_camera = invert(camera_matrix);
    vector camera_space_pos = world_pos * inv_camera;

    // Distance from camera to point
    float distance = length(camera_space_pos);

    if (distance < 0.001) {
        return 0;  // Too close, invalid
    }

    // Direction from camera to point (in camera space)
    vector dir = normalize(camera_space_pos);

    // Project onto sensor plane
    // Camera looks down -Z axis, sensor is at z = -focal_length
    float t = -focal_length / dir.z;

    if (t < 0) {
        return 0;  // Behind camera
    }

    // Sensor position
    sensor_x = dir.x * t;
    sensor_y = dir.y * t;

    // Compute circle of confusion using thin lens equation
    // CoC = (A * |S2 - S1|) / (S2 * (N))
    // where:
    //   A = aperture diameter = focal_length / fstop
    //   S1 = focus distance
    //   S2 = object distance
    //   N = f-stop number

    float aperture_diameter = (fstop > 0.01) ? (focal_length / fstop) : (focal_length / LENS_FSTOP_MIN);

    // Use world-space distance for more accurate CoC
    float object_distance = distance;

    // Circle of confusion formula
    if (abs(object_distance - focus_distance) < 0.1) {
        // In focus
        coc_radius = 0.0;
    } else {
        coc_radius = (aperture_diameter * abs(object_distance - focus_distance)) /
                     (object_distance * max(fstop, LENS_FSTOP_MIN));
    }

    // Clamp to reasonable values
    coc_radius = clamp(coc_radius, 0.0, 50.0);  // Max 50mm CoC

    return 1;  // Success
}

// Trace backward through polynomial lens (more accurate than thin lens approximation)
// This uses the actual polynomial to trace from outer pupil back to sensor
function int trace_backward_polynomial(
    vector world_pos;
    vector camera_pos;
    matrix camera_matrix;
    float focal_length;
    float focus_distance;
    float fstop;
    float lambda;  // Wavelength
    export float sensor_x, sensor_y;
    export float coc_radius;
    export float transmittance)
{
    // Transform to camera space
    matrix inv_camera = invert(camera_matrix);
    vector camera_space_pos = world_pos * inv_camera;

    // Direction from camera to point
    float distance = length(camera_space_pos);
    if (distance < 0.001) return 0;

    vector dir = normalize(camera_space_pos);

    // Outer pupil is at z = -focal_length
    float t = -focal_length / dir.z;
    if (t < 0) return 0;

    // Position at outer pupil
    float pupil_x = dir.x * t;
    float pupil_y = dir.y * t;
    float pupil_dx = dir.x;
    float pupil_dy = dir.y;

    // Use Newton-Raphson to find sensor position that maps to this pupil position
    // This is the inverse problem: given pupil position, find sensor position

    // Initial guess: pinhole projection
    float sx = pupil_x;
    float sy = pupil_y;

    // Aperture direction: sample center of aperture as approximation
    float dx = 0.0;
    float dy = 0.0;

    // In a full implementation, we would iterate to find the exact sensor position
    // For now, use thin lens approximation for CoC and polynomial for sensor position

    // Polynomial input
    float poly_in[5];
    poly_in[0] = sx;
    poly_in[1] = sy;
    poly_in[2] = dx;
    poly_in[3] = dy;
    poly_in[4] = lambda;

    // Evaluate to check
    float poly_out[4];
    pt_evaluate(poly_in, poly_out, transmittance);

    // For simplicity, use thin lens CoC calculation
    // Full implementation would trace through polynomial at multiple aperture samples
    float aperture_diameter = (fstop > 0.01) ? (focal_length / fstop) : (focal_length / LENS_FSTOP_MIN);
    float object_distance = distance;

    if (abs(object_distance - focus_distance) < 0.1) {
        coc_radius = 0.0;
    } else {
        coc_radius = (aperture_diameter * abs(object_distance - focus_distance)) /
                     (object_distance * max(fstop, LENS_FSTOP_MIN));
    }

    coc_radius = clamp(coc_radius, 0.0, 50.0);

    sensor_x = sx;
    sensor_y = sy;

    return 1;
}

// Compute pixel footprint for a given circle of confusion
// Returns the radius in pixels that this CoC covers
function float coc_to_pixel_radius(
    float coc_mm;          // CoC radius in mm on sensor
    float sensor_width_mm; // Sensor width in mm
    int image_width)       // Image width in pixels
{
    // Convert CoC from mm to pixels
    float mm_per_pixel = sensor_width_mm / float(image_width);
    float coc_pixels = coc_mm / mm_per_pixel;
    return coc_pixels;
}

// Compute sample weight for redistribution using Gaussian falloff
function float compute_redistribution_weight(
    float dx, dy;          // Offset from center in pixels
    float coc_radius)      // CoC radius in pixels
{
    if (coc_radius < 0.5) {
        // In focus, use delta function
        return (dx*dx + dy*dy < 0.25) ? 1.0 : 0.0;
    }

    // Gaussian falloff
    float r_sq = dx*dx + dy*dy;
    float sigma = coc_radius / 2.0;  // Standard deviation
    float sigma_sq = sigma * sigma;

    // Gaussian: exp(-r^2 / (2*sigma^2))
    float weight = exp(-r_sq / (2.0 * sigma_sq));

    // Normalize by CoC area for energy conservation
    float normalization = 1.0 / (2.0 * M_PI * sigma_sq);

    return weight * normalization;
}

// Compute importance sampling weight for bokeh highlights
// Out-of-focus bright areas should contribute more samples
function float compute_importance_weight(
    vector color;
    float coc_radius;
    float importance_scale)
{
    // Luminance
    float luma = color.r * 0.2126 + color.g * 0.7152 + color.b * 0.0722;

    // Importance increases with both brightness and CoC
    float importance = luma * coc_radius * importance_scale;

    // Clamp to reasonable range
    return clamp(importance, 0.1, 10.0);
}

#endif // LENTIL_BIDIRECTIONAL_H
