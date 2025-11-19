#!/usr/bin/env python3
"""
Test the Fixed NumPy Raytracer

This tests if the rewritten NumPy raytracer can successfully trace rays
through a simple lens system.
"""

import numpy as np
import sys
sys.path.insert(0, 'python')

from potk.simple_raytracer import SimpleRaytracer, SimpleLensElement

print("=" * 60)
print("Testing Fixed NumPy Raytracer")
print("=" * 60)

# Create a simple single-element lens (biconvex)
print("\n1. Creating simple biconvex lens...")
print("   Front surface: R = +50mm (convex)")
print("   Thickness: 10mm")
print("   Back surface: R = -50mm (convex)")
print("   Material: N-BK7 (n=1.5168)")

elements = [
    SimpleLensElement(radius=50.0, thickness=10.0, material='N-BK7', diameter=40.0),
    SimpleLensElement(radius=-50.0, thickness=100.0, material='air', diameter=40.0),
]

raytracer = SimpleRaytracer(elements)

# Test 1: Single ray on axis
print("\n2. Testing single on-axis ray...")
ray_origin = np.array([0.0, 0.0, -10.0])
ray_direction = np.array([0.0, 0.0, 1.0])

exit_pos, exit_dir = raytracer.trace_ray(ray_origin, ray_direction)

if exit_pos is not None:
    print(f"   ✅ SUCCESS!")
    print(f"   Entry: [{ray_origin[0]:.2f}, {ray_origin[1]:.2f}, {ray_origin[2]:.2f}]")
    print(f"   Exit:  [{exit_pos[0]:.2f}, {exit_pos[1]:.2f}, {exit_pos[2]:.2f}]")
    print(f"   Direction: [{exit_dir[0]:.3f}, {exit_dir[1]:.3f}, {exit_dir[2]:.3f}]")
else:
    print(f"   ❌ FAILED - Ray did not make it through")

# Test 2: Multiple rays
print("\n3. Testing batch of rays...")
num_rays = 100
ray_origins = np.zeros((num_rays, 3))
ray_origins[:, 0] = np.linspace(-10, 10, num_rays)  # Spread across 20mm
ray_origins[:, 2] = -10.0

ray_directions = np.tile([0, 0, 1], (num_rays, 1))

exit_positions, exit_directions = raytracer.trace_rays_batch(ray_origins, ray_directions)

valid = ~np.isnan(exit_positions[:, 0])
num_valid = np.sum(valid)
success_rate = 100 * num_valid / num_rays

print(f"   Valid rays: {num_valid}/{num_rays} ({success_rate:.1f}%)")

if success_rate > 50:
    print(f"   ✅ SUCCESS - Raytracer is working!")
else:
    print(f"   ❌ FAILED - Too few rays making it through")

# Test 3: Focal length estimation
print("\n4. Estimating focal length...")
focal_length = raytracer.compute_focal_length(samples=50)
print(f"   Computed focal length: {focal_length:.2f} mm")

# For a thin lens approximation: 1/f = (n-1) * (1/R1 - 1/R2)
# R1 = +50, R2 = -50, n = 1.5168
expected_f = 1.0 / ((1.5168 - 1.0) * (1/50.0 - 1/(-50.0)))
print(f"   Expected (thin lens): {expected_f:.2f} mm")
error_pct = abs(focal_length - expected_f) / expected_f * 100
print(f"   Error: {error_pct:.1f}%")

if error_pct < 20:
    print(f"   ✅ Focal length within 20% - reasonable!")
else:
    print(f"   ⚠️  Focal length error high")

# Test 4: Off-axis rays
print("\n5. Testing off-axis rays...")
test_cases = [
    ([5.0, 0.0, -10.0], [0.0, 0.0, 1.0], "5mm off-axis"),
    ([0.0, 5.0, -10.0], [0.0, 0.0, 1.0], "5mm off-axis (Y)"),
    ([0.0, 0.0, -10.0], [0.1, 0.0, 1.0], "10° angle"),
]

all_passed = True
for origin, direction, description in test_cases:
    origin = np.array(origin)
    direction = np.array(direction)
    exit_pos, exit_dir = raytracer.trace_ray(origin, direction)

    if exit_pos is not None:
        print(f"   ✅ {description}: passed")
    else:
        print(f"   ❌ {description}: failed")
        all_passed = False

print("\n" + "=" * 60)
if success_rate > 80 and error_pct < 20 and all_passed:
    print("🎉 NumPy Raytracer FIXED and WORKING!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Test with real lens from database")
    print("  2. Run polynomial fitting")
    print("  3. Generate VEX shader with real coefficients")
    print("  4. Test in Houdini Karma")
else:
    print("⚠️  NumPy Raytracer still has issues")
    print("=" * 60)
    print(f"\n  Success rate: {success_rate:.1f}% (need >80%)")
    print(f"  Focal error: {error_pct:.1f}% (need <20%)")
    print(f"  All tests passed: {all_passed}")
