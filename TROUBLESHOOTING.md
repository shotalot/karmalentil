# Troubleshooting KarmaLentil Installation

If the karmalentil shelf doesn't appear in Houdini, follow these steps:

## Quick Fix (Try These First)

### 1. Check if Shelf is Hidden

The shelf might be loaded but hidden:

1. **Right-click** on the shelf area (top of Houdini)
2. Choose **"Shelves"** → **"Shelf Sets..."**
3. Look for **"karmalentil"** in the list
4. **Check the box** to enable it
5. Click **"Accept"**

### 2. Restart Houdini

Sometimes a simple restart is all that's needed:

1. Close Houdini completely
2. Launch Houdini again
3. Check for the shelf

### 3. Run Diagnostic Script

In Houdini's **Python Shell** (Windows → Python Shell):

```python
import sys
sys.path.append('/home/user/karmalentil/python')
import diagnose_installation
diagnose_installation.diagnose_karmalentil()
```

This will tell you exactly what's wrong.

## Common Issues and Solutions

### Issue: "KARMALENTIL not set"

**Cause**: Installation didn't complete or environment not configured

**Solution**:
```bash
# Re-run installer
cd /home/user/karmalentil
./install_karmalentil.sh
```

Then restart Houdini.

### Issue: "Shelf file not found"

**Cause**: Missing files or wrong installation location

**Solution**:
```bash
# Verify files exist
ls -la /home/user/karmalentil/toolbar/karmalentil.shelf

# If missing, re-download/clone the repository
```

### Issue: "Package file not found"

**Cause**: Package wasn't created during installation

**Solution - Manual Package Creation**:

1. Find your Houdini user directory:
   ```bash
   # Linux/macOS
   ~/houdini20.5/

   # Windows
   %USERPROFILE%\Documents\houdini20.5\
   ```

2. Create `packages` directory if it doesn't exist:
   ```bash
   mkdir -p ~/houdini20.5/packages
   ```

3. Create `~/houdini20.5/packages/karmalentil.json`:
   ```json
   {
       "env": [
           {
               "KARMALENTIL_PATH": "/home/user/karmalentil"
           },
           {
               "KARMALENTIL": "$KARMALENTIL_PATH"
           },
           {
               "HOUDINI_PATH": "$KARMALENTIL_PATH;&"
           },
           {
               "PYTHONPATH": "$KARMALENTIL_PATH/python;&"
           }
       ]
   }
   ```

4. **Important**: Replace `/home/user/karmalentil` with your actual path!

5. Restart Houdini

## Verify Installation

### Method 1: Check Environment in Houdini

In Python Shell:
```python
import hou
print("KARMALENTIL:", hou.getenv("KARMALENTIL"))
print("HOUDINI_PATH:", hou.getenv("HOUDINI_PATH"))
```

Should show:
```
KARMALENTIL: /home/user/karmalentil
HOUDINI_PATH: /home/user/karmalentil;...
```

### Method 2: Check Available Shelves

In Python Shell:
```python
import hou
shelves = hou.shelves.shelves()
print([s for s in shelves.keys() if 'lentil' in s.lower()])
```

Should show: `['karmalentil']` or similar

### Method 3: Manually Load Shelf

If shelf exists but won't load:

In Python Shell:
```python
import hou
shelf_path = "/home/user/karmalentil/toolbar/karmalentil.shelf"
hou.shelves.loadFile(shelf_path)
```

## Alternative: Manual Setup (No Shelf)

If you can't get the shelf to work, you can still use KarmaLentil:

```python
# In Houdini Python Shell
import sys
sys.path.append('/home/user/karmalentil/python')

# Create lentil camera
import setup_complete_lentil
cam, rop = setup_complete_lentil.main()
```

This gives you the same result as the shelf tool.

## Platform-Specific Issues

### Linux

**Issue**: Permission denied on install script
```bash
chmod +x install_karmalentil.sh
./install_karmalentil.sh
```

**Issue**: SELinux blocking files
```bash
# Check SELinux status
getenforce

# If enforcing, may need to adjust contexts
```

### Windows

**Issue**: Script doesn't run
- Right-click `install_karmalentil.bat`
- Choose "Run as Administrator"

**Issue**: Path with spaces
- Move karmalentil to path without spaces
- Or use quotes in package JSON

### macOS

**Issue**: Gatekeeper blocking script
```bash
chmod +x install_karmalentil.sh
xattr -d com.apple.quarantine install_karmalentil.sh
./install_karmalentil.sh
```

## Still Not Working?

### Check Houdini Console on Startup

Look for error messages when Houdini starts:

```
KarmaLentil: Error during initialization: ...
```

Common errors:
- **Import errors**: Python path not set correctly
- **File not found**: Wrong KARMALENTIL_PATH
- **Syntax errors**: Shelf file corrupted

### Verify File Integrity

```bash
cd /home/user/karmalentil

# Check all required files exist
ls toolbar/karmalentil.shelf
ls scripts/123.py
ls packages/karmalentil.json
ls python/setup_complete_lentil.py
```

All should exist. If any are missing, re-clone/download the repository.

### Check Houdini Version

KarmaLentil requires **Houdini 20.5+**

```python
# In Houdini Python Shell
import hou
print(hou.applicationVersionString())
```

Should show `20.5.xxx` or higher.

### Nuclear Option: Clean Reinstall

1. **Remove old installation**:
   ```bash
   rm ~/houdini20.5/packages/karmalentil.json
   # Or remove KarmaLentil lines from houdini.env
   ```

2. **Close Houdini completely**

3. **Verify karmalentil directory is complete**:
   ```bash
   cd /home/user/karmalentil
   git status  # Should be clean
   ```

4. **Run installer again**:
   ```bash
   ./install_karmalentil.sh
   ```

5. **Choose option 1** (package file)

6. **Launch Houdini**

7. **Check console output** for "KarmaLentil" messages

## Getting Help

If still having issues, collect this information:

1. **Houdini version**: `hou.applicationVersionString()`
2. **Operating system**: Linux/Windows/macOS
3. **Installation method used**: Package/houdini.env/manual
4. **Environment variables**: `hou.getenv("KARMALENTIL")`
5. **Console errors**: Any errors shown on Houdini startup
6. **Diagnostic output**: Run `diagnose_installation.py` and share output

## Success Checklist

✅ Installer ran without errors
✅ Package file created or houdini.env updated
✅ Houdini restarted after installation
✅ Environment variables show correct path
✅ Console shows "KarmaLentil initialized" on startup
✅ Shelf "karmalentil" appears in shelf list
✅ Clicking "Lentil Camera" creates camera

If all checkboxes are checked, you're good to go! 🎉
