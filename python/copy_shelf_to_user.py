"""
Alternative shelf loader using shelf sets
Creates a shelf set definition that includes the karmalentil shelf
"""

import hou
import os

def create_shelf_set():
    """
    Create a shelf set file that includes karmalentil
    """
    print("=" * 70)
    print("CREATING KARMALENTIL SHELF SET")
    print("=" * 70)
    print()

    # Get Houdini user directory
    houdini_version = hou.applicationVersionString().split('.')[0] + '.' + hou.applicationVersionString().split('.')[1]
    home = os.path.expanduser("~")

    # Try different locations for Windows
    shelf_dir = None
    possible_dirs = [
        os.path.join(home, f"houdini{houdini_version}", "toolbar"),
        os.path.join(home, "Documents", f"houdini{houdini_version}", "toolbar"),
    ]

    for dir_path in possible_dirs:
        if os.path.exists(os.path.dirname(dir_path)) or True:  # Create if needed
            shelf_dir = dir_path
            break

    if not shelf_dir:
        print("ERROR: Could not find Houdini user directory")
        return False

    # Create toolbar directory if it doesn't exist
    os.makedirs(shelf_dir, exist_ok=True)

    # Get karmalentil path
    karmalentil_path = hou.getenv("KARMALENTIL") or hou.getenv("KARMALENTIL_PATH")
    if not karmalentil_path:
        print("ERROR: KARMALENTIL path not set")
        return False

    # Create shelf set file that references our shelf
    shelf_set_file = os.path.join(shelf_dir, "karmalentil.shelf")

    print(f"Creating shelf at: {shelf_set_file}")

    # Copy shelf file to user directory
    import shutil
    source_shelf = os.path.join(karmalentil_path, "toolbar", "karmalentil.shelf")

    if not os.path.exists(source_shelf):
        print(f"ERROR: Source shelf not found: {source_shelf}")
        return False

    try:
        shutil.copy2(source_shelf, shelf_set_file)
        print(f"✓ Copied shelf file to user directory")
        print()
        print("SUCCESS!")
        print()
        print("Now restart Houdini and the shelf should appear.")
        print("You may need to enable it in:")
        print("  Right-click shelf area → Shelves → Shelf Sets → karmalentil")
        print()
        return True

    except Exception as e:
        print(f"ERROR copying shelf: {e}")
        return False

if __name__ == '__main__':
    create_shelf_set()
