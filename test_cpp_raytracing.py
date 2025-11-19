#!/usr/bin/env python3
"""
Test C++ raytracing to verify segfault is fixed
"""
import sys
import numpy as np

# Set environment variable for polynomial-optics database
import os
os.environ['LENTIL_PATH'] = '/home/user/karmalentil/ext/lentil/polynomial-optics'

# Add to Python path
sys.path.insert(0, '/home/user/karmalentil/python')
sys.path.insert(0, '/home/user/karmalentil/python/potk')

print("=" * 60)
print("Testing C++ Raytracing Fix")
print("=" * 60)

try:
    import polynomial_optics_binding as cpp
    print("✓ C++ module imported successfully")
    print(f"  Version: {cpp.__version__}")
    print(f"  Implementation: {cpp.__implementation__}")
except ImportError as e:
    print(f"✗ Failed to import C++ module: {e}")
    sys.exit(1)

# Test 1: Load lens
print("\n1. Loading lens from database...")
lens = cpp.LensSystem()
success = lens.load_from_database("0001", 100)

if not success:
    print("✗ Failed to load lens")
    sys.exit(1)

print("✓ Lens loaded successfully")

# Test 2: Get lens info
print("\n2. Getting lens info...")
info = lens.get_lens_info()
print(f"✓ Lens info retrieved:")
print(f"  ID: {info['lens_id']}")
print(f"  Elements: {info['num_elements']}")
print(f"  Aperture radius: {info['aperture_radius']:.2f}mm")
print(f"  Lens length: {info['lens_length']:.2f}mm")

# Check if lens length is reasonable (not garbage)
if info['lens_length'] > 1000 or info['lens_length'] < 0:
    print(f"✗ WARNING: Lens length looks suspicious: {info['lens_length']}")
else:
    print(f"✓ Lens length looks reasonable")

# Test 3: Create raytracer
print("\n3. Creating raytracer...")
raytracer = cpp.Raytracer(lens, zoom=0.5)
print("✓ Raytracer created successfully")

# Test 4: Trace a single ray (this is where the segfault occurred before)
print("\n4. Tracing a single ray...")
print("  This is where the segfault occurred before the fix...")
try:
    sensor_pos = np.array([0.0, 0.0, 0.0])
    sensor_dir = np.array([0.0, 0.0, 1.0])
    wavelength = 550.0  # Green light

    success_flag, exit_pos, exit_dir = raytracer.trace_ray(
        sensor_pos, sensor_dir, wavelength
    )

    print("✓ Ray traced successfully! (No segfault!)")
    print(f"  Success: {success_flag}")
    if success_flag:
        print(f"  Exit position: [{exit_pos[0]:.4f}, {exit_pos[1]:.4f}, {exit_pos[2]:.4f}]")
        print(f"  Exit direction: [{exit_dir[0]:.4f}, {exit_dir[1]:.4f}, {exit_dir[2]:.4f}]")
    else:
        print("  Ray was vignetted or had TIR")

except Exception as e:
    print(f"✗ Ray tracing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Trace multiple rays
print("\n5. Tracing batch of rays...")
num_rays = 100
np.random.seed(42)
sensor_positions = np.random.randn(num_rays, 3) * 5  # Random positions within 5mm
sensor_positions[:, 2] = 0  # All on sensor plane
sensor_directions = np.tile([0, 0, 1], (num_rays, 1))  # All pointing forward

try:
    success_flags, exit_positions, exit_directions = raytracer.trace_rays_batch(
        sensor_positions, sensor_directions, wavelength=550.0
    )

    num_successful = np.sum(success_flags)
    print(f"✓ Batch raytracing successful!")
    print(f"  Traced: {num_rays} rays")
    print(f"  Successful: {num_successful} rays ({100*num_successful/num_rays:.1f}%)")

except Exception as e:
    print(f"✗ Batch raytracing failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("All tests passed! C++ raytracing is working! 🎉")
print("=" * 60)
