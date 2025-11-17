// Aperture Sampling using Newton-Raphson
// Solves the inverse problem: given sensor position (x,y), find aperture direction (dx,dy)
// Uses iterative Newton-Raphson method to converge to the solution

#ifndef PT_SAMPLE_APERTURE_H
#define PT_SAMPLE_APERTURE_H

// Sample aperture position given sensor coordinates and target outer pupil
// This is used for importance sampling from lights (reverse ray tracing)
// Returns 1 on success, 0 on failure
function int pt_sample_aperture(
    float in[5];              // Input: x, y, ?, ?, lambda
    float target_x, target_y; // Target outer pupil position
    export float out_dx, out_dy)  // Output: aperture direction
{
    // Initial guess for aperture direction
    float dx = 0.0;
    float dy = 0.0;

    // Newton-Raphson iteration parameters
    int max_iterations = 10;
    float tolerance = 1e-4;

    for (int iter = 0; iter < max_iterations; iter++) {
        // Evaluate polynomial at current guess
        float eval_in[5];
        eval_in[0] = in[0];  // x
        eval_in[1] = in[1];  // y
        eval_in[2] = dx;
        eval_in[3] = dy;
        eval_in[4] = in[4];  // lambda

        float eval_out[4];
        float transmittance;
        pt_evaluate(eval_in, eval_out, transmittance);

        // Compute error
        float err_x = eval_out[0] - target_x;
        float err_y = eval_out[1] - target_y;
        float sqr_err = err_x*err_x + err_y*err_y;

        // Check convergence
        if (sqr_err < tolerance) {
            out_dx = dx;
            out_dy = dy;
            return 1;  // Success
        }

        // Compute Jacobian (numerical differentiation)
        float h = 0.001;  // Step size

        // Partial derivatives for dx
        eval_in[2] = dx + h;
        float eval_out_dx[4];
        float trans_tmp;
        pt_evaluate(eval_in, eval_out_dx, trans_tmp);

        float J00 = (eval_out_dx[0] - eval_out[0]) / h;  // d(out_x)/d(dx)
        float J10 = (eval_out_dx[1] - eval_out[1]) / h;  // d(out_y)/d(dx)

        // Partial derivatives for dy
        eval_in[2] = dx;
        eval_in[3] = dy + h;
        float eval_out_dy[4];
        pt_evaluate(eval_in, eval_out_dy, trans_tmp);

        float J01 = (eval_out_dy[0] - eval_out[0]) / h;  // d(out_x)/d(dy)
        float J11 = (eval_out_dy[1] - eval_out[1]) / h;  // d(out_y)/d(dy)

        // Invert 2x2 Jacobian
        float det = J00*J11 - J01*J10;

        if (abs(det) < 1e-10) {
            // Jacobian is singular, cannot continue
            return 0;  // Failure
        }

        float invJ00 =  J11 / det;
        float invJ01 = -J01 / det;
        float invJ10 = -J10 / det;
        float invJ11 =  J00 / det;

        // Newton-Raphson update: [dx, dy] -= invJ * [err_x, err_y]
        dx -= (invJ00 * err_x + invJ01 * err_y);
        dy -= (invJ10 * err_x + invJ11 * err_y);

        // Reset eval_in for next iteration
        eval_in[3] = dy;
    }

    // Failed to converge
    return 0;
}

#endif // PT_SAMPLE_APERTURE_H
