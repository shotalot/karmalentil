// Lentil VEX Utility Functions
// Common utilities for polynomial optics in Karma

#ifndef LENTIL_UTILS_H
#define LENTIL_UTILS_H

// Convert wavelength (in micrometers) to approximate RGB value
// Uses a simplified spectral to RGB conversion
function vector wavelength_to_rgb(float lambda)
{
    // lambda is in micrometers (0.38 - 0.78)
    // Convert to nanometers for easier reading
    float nm = lambda * 1000.0;

    float r, g, b;

    if (nm >= 380.0 && nm < 440.0) {
        r = -(nm - 440.0) / (440.0 - 380.0);
        g = 0.0;
        b = 1.0;
    }
    else if (nm >= 440.0 && nm < 490.0) {
        r = 0.0;
        g = (nm - 440.0) / (490.0 - 440.0);
        b = 1.0;
    }
    else if (nm >= 490.0 && nm < 510.0) {
        r = 0.0;
        g = 1.0;
        b = -(nm - 510.0) / (510.0 - 490.0);
    }
    else if (nm >= 510.0 && nm < 580.0) {
        r = (nm - 510.0) / (580.0 - 510.0);
        g = 1.0;
        b = 0.0;
    }
    else if (nm >= 580.0 && nm < 645.0) {
        r = 1.0;
        g = -(nm - 645.0) / (645.0 - 580.0);
        b = 0.0;
    }
    else if (nm >= 645.0 && nm <= 780.0) {
        r = 1.0;
        g = 0.0;
        b = 0.0;
    }
    else {
        r = 0.0;
        g = 0.0;
        b = 0.0;
    }

    // Intensity falloff at extremes
    float factor = 1.0;
    if (nm >= 380.0 && nm < 420.0) {
        factor = 0.3 + 0.7 * (nm - 380.0) / (420.0 - 380.0);
    }
    else if (nm >= 700.0 && nm <= 780.0) {
        factor = 0.3 + 0.7 * (780.0 - nm) / (780.0 - 700.0);
    }

    return set(r * factor, g * factor, b * factor);
}

// Sample wavelength for chromatic aberration
// Returns wavelength in micrometers based on RGB channel
// channel: 0=red, 1=green, 2=blue
function float sample_wavelength_rgb(int channel)
{
    if (channel == 0) {
        return 0.65;  // Red ~650nm
    }
    else if (channel == 1) {
        return 0.55;  // Green ~550nm
    }
    else {
        return 0.45;  // Blue ~450nm
    }
}

// Concentric disk sampling
// Maps uniform square samples [0,1]^2 to uniform disk samples
function void concentric_disk_sample(
    float u1, u2;
    export float dx, dy)
{
    // Map [0,1]^2 to [-1,1]^2
    float sx = 2.0 * u1 - 1.0;
    float sy = 2.0 * u2 - 1.0;

    // Handle degeneracy at origin
    if (sx == 0.0 && sy == 0.0) {
        dx = 0.0;
        dy = 0.0;
        return;
    }

    // Apply concentric mapping
    float r, theta;
    if (abs(sx) > abs(sy)) {
        r = sx;
        theta = (M_PI / 4.0) * (sy / sx);
    }
    else {
        r = sy;
        theta = (M_PI / 2.0) - (M_PI / 4.0) * (sx / sy);
    }

    dx = r * cos(theta);
    dy = r * sin(theta);
}

// Apply aperture blade shape (polygonal bokeh)
// blade_count: 0-3 = circular, 4+ = polygonal aperture
function void apply_aperture_blades(
    float dx, dy;
    int blade_count;
    float rotation;
    export float out_dx, out_dy)
{
    if (blade_count < 4) {
        // Circular aperture
        out_dx = dx;
        out_dy = dy;
        return;
    }

    // Convert to polar
    float r = sqrt(dx*dx + dy*dy);
    float theta = atan2(dy, dx) + rotation;

    // Polygonal aperture shape
    float angle_per_blade = 2.0 * M_PI / blade_count;
    float blade_angle = theta - floor(theta / angle_per_blade) * angle_per_blade;

    // Distance to blade edge (simplified)
    float blade_radius = cos(M_PI / blade_count);
    float actual_radius = blade_radius / cos(blade_angle - angle_per_blade * 0.5);

    // Scale radius to fit polygon
    r *= actual_radius;

    // Convert back to Cartesian
    out_dx = r * cos(theta);
    out_dy = r * sin(theta);
}

// Scale aperture by f-stop
// fstop: f-stop number (0 = wide open, use lens minimum)
// fstop_min: minimum f-stop of the lens
function float get_aperture_scale(float fstop; float fstop_min)
{
    if (fstop < 0.01) {
        // Wide open
        return 1.0;
    }

    // Aperture diameter is inversely proportional to f-stop
    // radius scales with diameter
    return fstop_min / fstop;
}

#endif // LENTIL_UTILS_H
