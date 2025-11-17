// Polynomial Evaluation for Double Gauss 50mm f/2.8
// Point-to-Pupil (PT) evaluation
// Maps from sensor position (x,y) and aperture direction (dx,dy) at wavelength lambda
// to outer pupil position and direction

#ifndef PT_EVALUATE_H
#define PT_EVALUATE_H

// Evaluate polynomial to get outer pupil position and direction
// Inputs:
//   in[0] = x (sensor x position in mm)
//   in[1] = y (sensor y position in mm)
//   in[2] = dx (aperture x direction)
//   in[3] = dy (aperture y direction)
//   in[4] = lambda (wavelength in micrometers, typically 0.4-0.7)
// Outputs:
//   out[0] = outer pupil x position (mm)
//   out[1] = outer pupil y position (mm)
//   out[2] = outer pupil x direction
//   out[3] = outer pupil y direction
//   out_transmittance = light transmittance (0-1)

function void pt_evaluate(
    float in[5];
    export float out[4];
    export float out_transmittance)
{
    // Extract input variables for clarity
    float x = in[0];
    float y = in[1];
    float dx = in[2];
    float dy = in[3];
    float lambda = in[4];

    // NOTE: These are PLACEHOLDER polynomials for demonstration
    // Real polynomials should be generated using the lentil fitting tools
    // from the original repository: https://github.com/zpelgrims/lentil
    //
    // To generate real polynomials:
    // 1. Use the polynomial-optics tools to fit lens data
    // 2. Run gencode to generate optimized polynomial C code
    // 3. Convert to VEX syntax (replace pow() with lens_ipow())

    // Simplified polynomial approximation for Double Gauss lens
    // This provides a basic lens model with some aberrations

    // X position at outer pupil (simplified paraxial + aberration terms)
    out[0] = 50.0 * dx  // Focal length term
           + 0.8 * x    // Position transfer
           - 0.3 * x * lambda  // Chromatic aberration
           - 15.0 * dx * (dy*dy)  // Coma-like aberration
           - 0.05 * x * (x*x + y*y);  // Spherical-like aberration

    // Y position at outer pupil
    out[1] = 50.0 * dy
           + 0.8 * y
           - 0.3 * y * lambda
           - 15.0 * dy * (dx*dx)
           - 0.05 * y * (x*x + y*y);

    // X direction at outer pupil (normalized)
    out[2] = dx
           + 0.001 * x
           - 0.002 * x * lambda
           - 0.01 * dx * (dx*dx + dy*dy);

    // Y direction at outer pupil
    out[3] = dy
           + 0.001 * y
           - 0.002 * y * lambda
           - 0.01 * dy * (dx*dx + dy*dy);

    // Transmittance (vignetting approximation)
    float r_sensor = sqrt(x*x + y*y);
    float r_aperture = sqrt(dx*dx + dy*dy);
    float max_radius = LENS_MAXIMUM_SENSOR_RADIUS;

    // Simple vignetting model
    out_transmittance = 1.0;
    if (r_sensor > max_radius * 0.7) {
        float t = (r_sensor - max_radius * 0.7) / (max_radius * 0.3);
        out_transmittance = 1.0 - t * 0.5;  // 50% vignetting at edge
    }

    // Ensure valid transmittance
    out_transmittance = clamp(out_transmittance, 0.0, 1.0);
}

// Helper function for integer powers (VEX doesn't have direct ipow)
function float lens_ipow(float base; int exp)
{
    if (exp == 0) return 1.0;
    if (exp == 1) return base;
    if (exp == 2) return base * base;
    if (exp == 3) return base * base * base;
    if (exp == 4) {
        float b2 = base * base;
        return b2 * b2;
    }
    // For higher powers, use pow()
    return pow(base, exp);
}

#endif // PT_EVALUATE_H
