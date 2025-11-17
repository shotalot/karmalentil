#!/usr/bin/env python
"""
Diagnostic script to check KarmaLentil installation
Run this in Houdini's Python Shell to diagnose issues
"""

import hou
import os
import sys


def diagnose_karmalentil():
    """
    Run diagnostics on KarmaLentil installation
    """
    print("=" * 70)
    print("KARMALENTIL DIAGNOSTIC")
    print("=" * 70)
    print()

    issues = []

    # Check 1: Environment variables
    print("1. Checking environment variables...")
    karmalentil = hou.getenv("KARMALENTIL")
    karmalentil_path = hou.getenv("KARMALENTIL_PATH")
    houdini_path = hou.getenv("HOUDINI_PATH")

    print(f"   KARMALENTIL: {karmalentil}")
    print(f"   KARMALENTIL_PATH: {karmalentil_path}")
    print(f"   HOUDINI_PATH: {houdini_path}")

    if not karmalentil and not karmalentil_path:
        issues.append("KARMALENTIL environment variable not set")
        print("   ❌ KARMALENTIL not set!")
    else:
        print("   ✓ Environment variables set")

    print()

    # Check 2: Directory structure
    print("2. Checking directory structure...")
    base_path = karmalentil or karmalentil_path

    if base_path:
        required_dirs = [
            'toolbar',
            'scripts',
            'python',
            'vex',
            'lenses',
            'packages'
        ]

        for dir_name in required_dirs:
            dir_path = os.path.join(base_path, dir_name)
            exists = os.path.exists(dir_path)
            status = "✓" if exists else "❌"
            print(f"   {status} {dir_name}/")
            if not exists:
                issues.append(f"Missing directory: {dir_name}/")
    else:
        print("   ❌ Cannot check - KARMALENTIL path not set")
        issues.append("Cannot verify directory structure")

    print()

    # Check 3: Shelf file
    print("3. Checking shelf file...")
    if base_path:
        shelf_file = os.path.join(base_path, 'toolbar', 'karmalentil.shelf')
        if os.path.exists(shelf_file):
            print(f"   ✓ Shelf file exists: {shelf_file}")
            # Check file size
            size = os.path.getsize(shelf_file)
            print(f"   ✓ File size: {size} bytes")
        else:
            print(f"   ❌ Shelf file NOT found: {shelf_file}")
            issues.append("Shelf file missing")

    print()

    # Check 4: Available shelves
    print("4. Checking Houdini shelves...")
    try:
        shelves = hou.shelves.shelves()
        karmalentil_shelves = [s for s in shelves.keys() if 'karmalentil' in s.lower() or 'lentil' in s.lower()]

        if karmalentil_shelves:
            print(f"   ✓ Found KarmaLentil shelves: {karmalentil_shelves}")
        else:
            print("   ❌ No KarmaLentil shelves found")
            print(f"   Available shelves: {list(shelves.keys())[:10]}...")
            issues.append("Shelf not loaded by Houdini")
    except Exception as e:
        print(f"   ❌ Error checking shelves: {e}")
        issues.append(f"Error checking shelves: {e}")

    print()

    # Check 5: Python path
    print("5. Checking Python path...")
    if base_path:
        python_path = os.path.join(base_path, 'python')
        if python_path in sys.path:
            print(f"   ✓ Python path in sys.path")
        else:
            print(f"   ❌ Python path NOT in sys.path")
            print(f"   Expected: {python_path}")
            issues.append("Python path not in sys.path")

    print()

    # Check 6: Startup script
    print("6. Checking if startup script ran...")
    if hasattr(hou.session, 'lentil_lens_database'):
        print("   ✓ Lens database initialized (startup script ran)")
    else:
        print("   ❌ Lens database not found (startup script may not have run)")
        issues.append("Startup script (123.py) did not run or failed")

    print()

    # Check 7: Package file
    print("7. Checking package file...")
    houdini_version = hou.applicationVersionString().split('.')[0] + '.' + hou.applicationVersionString().split('.')[1]
    home = os.path.expanduser("~")

    # Try different locations
    package_locations = [
        os.path.join(home, f"houdini{houdini_version}", "packages", "karmalentil.json"),
        os.path.join(home, "Documents", f"houdini{houdini_version}", "packages", "karmalentil.json"),  # Windows
    ]

    found_package = False
    for pkg_path in package_locations:
        if os.path.exists(pkg_path):
            print(f"   ✓ Package file found: {pkg_path}")
            found_package = True
            # Try to read it
            try:
                with open(pkg_path, 'r') as f:
                    content = f.read()
                    print(f"   Content preview: {content[:200]}...")
            except Exception as e:
                print(f"   ⚠ Could not read package file: {e}")
            break

    if not found_package:
        print("   ❌ Package file not found in standard locations")
        print(f"   Checked: {package_locations}")
        issues.append("Package file not found")

    print()

    # Summary
    print("=" * 70)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 70)

    if issues:
        print(f"\n❌ Found {len(issues)} issue(s):\n")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")

        print("\n" + "=" * 70)
        print("RECOMMENDED FIXES")
        print("=" * 70)
        print()

        if "KARMALENTIL environment variable not set" in issues:
            print("FIX 1: Reinstall the plugin")
            print("   Run: ./install_karmalentil.sh (Linux/Mac)")
            print("   Or:  install_karmalentil.bat (Windows)")
            print()

        if "Shelf not loaded by Houdini" in issues:
            print("FIX 2: Manually add shelf")
            print("   1. Right-click on shelf area")
            print("   2. Choose 'Shelves' → 'Shelf Sets...'")
            print("   3. Look for 'karmalentil' in the list")
            print("   4. Check the box to enable it")
            print()

        if "Package file not found" in issues:
            print("FIX 3: Create package file manually")
            print(f"   Create: ~/houdini{houdini_version}/packages/karmalentil.json")
            print("   With content:")
            print('   {')
            print('       "env": [')
            print('           {"KARMALENTIL_PATH": "/path/to/karmalentil"},')
            print('           {"HOUDINI_PATH": "$KARMALENTIL_PATH;&"}')
            print('       ]')
            print('   }')
            print()

        print("After fixes, restart Houdini!")

    else:
        print("\n✓ All checks passed! Installation looks good.")
        print("\nIf shelf still doesn't appear:")
        print("   1. Check if shelf is hidden: Right-click shelf area → 'Shelves'")
        print("   2. Restart Houdini")
        print("   3. Check for errors in console on startup")

    print()
    print("=" * 70)

    return issues


if __name__ == '__main__':
    diagnose_karmalentil()
