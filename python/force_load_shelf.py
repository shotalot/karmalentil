"""
Force Load KarmaLentil Shelf
Run this in Houdini Python Shell to manually load the shelf
"""

import hou
import os

def force_load_shelf():
    """
    Force load the karmalentil shelf into Houdini
    """
    print("=" * 70)
    print("FORCE LOADING KARMALENTIL SHELF")
    print("=" * 70)
    print()

    # Get shelf path
    karmalentil_path = hou.getenv("KARMALENTIL") or hou.getenv("KARMALENTIL_PATH")

    if not karmalentil_path:
        print("ERROR: KARMALENTIL path not set!")
        print("Please run the installer first.")
        return False

    shelf_file = os.path.join(karmalentil_path, "toolbar", "karmalentil.shelf")

    print(f"Shelf file: {shelf_file}")

    # Check if file exists
    if not os.path.exists(shelf_file):
        print(f"ERROR: Shelf file not found at: {shelf_file}")
        return False

    print(f"✓ Shelf file exists ({os.path.getsize(shelf_file)} bytes)")
    print()

    # Try to load the shelf
    print("Loading shelf file...")
    try:
        # Method 1: Direct load
        hou.shelves.loadFile(shelf_file)
        print("✓ Shelf loaded successfully!")
        print()

        # Verify it loaded
        shelves = hou.shelves.shelves()
        karmalentil_shelves = [s for s in shelves.keys() if 'karmalentil' in s.lower() or 'lentil' in s.lower()]

        if karmalentil_shelves:
            print(f"✓ Found loaded shelves: {karmalentil_shelves}")
            print()
            print("SUCCESS! The shelf should now appear in Houdini.")
            print()
            print("If you still don't see it:")
            print("  1. Right-click shelf area → Shelves → Shelf Sets")
            print("  2. Look for 'karmalentil' and check the box")
            print()
            return True
        else:
            print("⚠ Shelf loaded but not appearing in shelf list")
            print("This might be a Houdini UI issue.")
            print()
            return False

    except Exception as e:
        print(f"❌ Error loading shelf: {e}")
        print()
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    force_load_shelf()
