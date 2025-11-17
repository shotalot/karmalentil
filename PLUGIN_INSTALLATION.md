# KarmaLentil Plugin Installation

Easy installation guide for the KarmaLentil Houdini plugin.

## Quick Install (3 Steps)

### Linux/macOS

```bash
cd /path/to/karmalentil
./install_karmalentil.sh
```

### Windows

```cmd
cd C:\path\to\karmalentil
install_karmalentil.bat
```

The installer will:
1. Detect your Houdini version automatically
2. Ask for installation method (package or env file)
3. Configure KarmaLentil paths
4. Ready to use!

## Manual Installation

If you prefer manual installation or the script doesn't work:

### Method 1: Package File (Recommended)

**Why**: Automatic loading, no restart needed, clean organization

1. Create `~/houdini20.5/packages/karmalentil.json`:

```json
{
    "env": [
        {
            "KARMALENTIL_PATH": "/path/to/karmalentil"
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

2. Launch Houdini - KarmaLentil loads automatically!

### Method 2: houdini.env

**Why**: Simple, traditional method

Add to `~/houdini20.5/houdini.env`:

```bash
# KarmaLentil Plugin
KARMALENTIL_PATH = "/path/to/karmalentil"
KARMALENTIL = "$KARMALENTIL_PATH"
HOUDINI_PATH = "$KARMALENTIL_PATH:&"
PYTHONPATH = "$KARMALENTIL_PATH/python:&"
```

Restart Houdini.

### Method 3: Environment Variables

Set system environment variables before launching Houdini:

**Linux/macOS**:
```bash
export KARMALENTIL="/path/to/karmalentil"
export HOUDINI_PATH="$KARMALENTIL:&"
export PYTHONPATH="$KARMALENTIL/python:&"
houdini
```

**Windows** (PowerShell):
```powershell
$env:KARMALENTIL="C:\path\to\karmalentil"
$env:HOUDINI_PATH="$env:KARMALENTIL;&"
$env:PYTHONPATH="$env:KARMALENTIL\python;&"
houdini
```

## Verify Installation

After installation:

1. **Launch Houdini 20.5+**

2. **Check console output**:
   ```
   ==========================================
   KarmaLentil - Polynomial Optics for Houdini Karma
   ==========================================
   Shelf: karmalentil
   ...
   ```

3. **Look for the karmalentil shelf** at the top of the UI

4. **Test**: Click "Lentil Camera" shelf tool
   - Should create a complete setup
   - Viewport switches to Karma
   - Ready to render!

## Using the Plugin

### Shelf Tools

The **karmalentil** shelf provides:

| Tool | Icon | Description |
|------|------|-------------|
| **Lentil Camera** | 📷 | Create complete lentil camera setup |
| **Apply Bidirectional Filter** | 🎨 | Post-process EXR with bidirectional filtering |
| **Import Lens** | 📦 | Import lens from original lentil repository |
| **Help** | ❓ | Show help and documentation |

### Quick Workflow

1. **Click "Lentil Camera"** → Creates complete setup with example scene

2. **Adjust parameters** in camera's Lentil tabs:
   - **Lentil Lens**: Focal length, f-stop, focus distance
   - **Aberrations**: Chromatic aberration strength
   - **Bokeh**: Blade count, custom textures
   - **Bidirectional**: Quality, intensity

3. **Viewport shows real-time** lens effects

4. **Render** with Karma ROP (automatically created)

5. **(Optional)** Click "Apply Bidirectional Filter" for ultimate quality

### No Python Required!

Everything works through shelf tools - no need to run Python scripts manually.

## Troubleshooting

### "No shelf visible"

**Solution**: Right-click shelf area → Shelves → Check "karmalentil"

### "Tool errors / module not found"

**Solutions**:
1. Verify `KARMALENTIL` environment variable is set:
   ```python
   # In Houdini Python shell
   import hou
   print(hou.getenv("KARMALENTIL"))
   ```

2. Check paths in package file or houdini.env

3. Restart Houdini after changing configuration

### "Camera created but no lens effects"

**Solutions**:
- Ensure viewport is in Karma mode (not GL)
- Check "Enable Lentil" parameter is ON
- Increase pixel samples (Scene View → Display Options → Sampling)
- Try lowering f-stop to 2.8 or less

### "Shelf tool doesn't work"

**Solutions**:
- Check Python console (Windows → Python Shell) for errors
- Verify all files are present in karmalentil directory
- Try manual setup via Python:
  ```python
  import setup_complete_lentil
  setup_complete_lentil.main()
  ```

## Uninstalling

### Package Method
Delete: `~/houdini20.5/packages/karmalentil.json`

### houdini.env Method
Remove KarmaLentil lines from `~/houdini20.5/houdini.env`

### Complete Removal
1. Remove package/env configuration
2. Delete karmalentil directory
3. Restart Houdini

## Updating

To update KarmaLentil:

1. Download new version
2. Replace old karmalentil directory
3. **No reinstallation needed** - paths remain the same!
4. Restart Houdini to load new version

## Distribution

To share KarmaLentil with others:

1. **Zip the entire karmalentil directory**
2. Send to colleague
3. They run `install_karmalentil.sh` (or .bat)
4. Ready to use!

**No compilation needed** - pure Python and VEX.

## Advanced: Network Installation

For studios with shared network drives:

1. **Install to shared location**:
   ```
   /mnt/pipeline/houdini/plugins/karmalentil/
   ```

2. **Each user adds to their houdini.env**:
   ```bash
   KARMALENTIL_PATH = "/mnt/pipeline/houdini/plugins/karmalentil"
   HOUDINI_PATH = "$KARMALENTIL_PATH:&"
   PYTHONPATH = "$KARMALENTIL_PATH/python:&"
   ```

3. **Or use central package**:
   Create `/mnt/pipeline/houdini/packages/karmalentil.json`

   Then each user adds to their houdini.env:
   ```bash
   HOUDINI_PACKAGE_DIR = "/mnt/pipeline/houdini/packages:&"
   ```

## Platform Compatibility

| Platform | Status | Notes |
|----------|--------|-------|
| Linux | ✅ Tested | Primary development platform |
| Windows | ✅ Supported | Use .bat installer |
| macOS | ✅ Supported | Use .sh installer |

**Houdini Versions**:
- ✅ 20.5 (recommended)
- ✅ 20.0
- ⚠️ 19.5 (should work, not tested)
- ❌ <19.5 (not supported - VEX features required)

## Next Steps

After successful installation:

1. **Read QUICKSTART.md** for 5-minute tutorial
2. **Check USAGE.md** for parameter reference
3. **Explore examples** in example scenes
4. **Import real lenses** from original lentil repository

## Support

- **Documentation**: See all .md files in karmalentil directory
- **Original lentil**: https://github.com/zpelgrims/lentil
- **Issues**: Report installation problems on GitHub

---

**Enjoy realistic lens effects in Houdini!** 🎬✨
