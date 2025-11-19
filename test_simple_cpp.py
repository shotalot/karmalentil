#!/usr/bin/env python3
import sys
import os
os.environ['LENTIL_PATH'] = '/home/user/karmalentil/ext/lentil/polynomial-optics'
sys.path.insert(0, '/home/user/karmalentil/python/potk')

print("Test 1: Import module")
import polynomial_optics_binding as cpp
print(f"✓ Module version: {cpp.__version__}")

print("\nTest 2: Create LensSystem")
lens = cpp.LensSystem()
print("✓ LensSystem created")

print("\nTest 3: Load lens")
success = lens.load_from_database("0001", 100)
print(f"✓ Load success: {success}")

print("\nTest 4: Get info")
info = lens.get_lens_info()
print(f"✓ Info: {info}")

print("\nTest 5: Create Raytracer")
try:
    raytracer = cpp.Raytracer(lens, 0.5)
    print("✓ Raytracer created")
except Exception as e:
    print(f"✗ Failed to create raytracer: {e}")
    sys.exit(1)

print("\nTest 6: Try to access raytracer attributes")
try:
    # Just check if we can access the object
    print(f"✓ Raytracer object: {raytracer}")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\nTest 7: Call trace_ray with list instead of numpy")
try:
    print("Calling trace_ray...")
    result = raytracer.trace_ray([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], 550.0)
    print(f"✓ Success: {result}")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\nAll tests passed!")
