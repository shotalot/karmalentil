# How to Actually Use POTK Lens Shaders in Houdini

**TL;DR:** Karma doesn't directly load custom lens shaders the way described. Here are the REAL options that work:

---

## Option 1: Use Built-in Lens Distortion (Easiest)

Houdini Karma has built-in lens distortion parameters on the camera.

### Step-by-Step:

1. **Select your camera** in Houdini
2. **Go to View tab** → Sampling section
3. **Find "Lens Distortion" parameters:**
   - Enable "Use Lens Distortion"
   - Set "Distortion" value (-1 to 1)
     - Negative = barrel distortion
     - Positive = pincushion distortion
   - Adjust "Distortion Center"

This gives you basic lens distortion without needing custom shaders.

---

## Option 2: Use Lens Shader VOP (Recommended for POTK)

This is the proper way to use custom lens effects in Karma.

### Step-by-Step:

1. **Create a Lens Shader:**
   ```
   /mat context → Create → Karma Lens Shader
   ```

2. **Inside the shader:**
   - Add VOP nodes to implement polynomial distortion
   - Connect to output parameters
   - Or import compiled VEX code

3. **Apply to camera:**
   ```
   Camera → Rendering → Lens Shader → Select your lens shader material
   ```

### Creating the Lens Shader Material:

I'll create a proper Material Builder setup for this...

---

## Option 3: Composite Lens Distortion (Post-Process)

Use lens distortion as a post-process effect in compositing.

### In Houdini COPs:

1. Render clean image from Karma
2. Add Lens Distortion COP
3. Use polynomial parameters from POTK data
4. Composite final result

---

## What POTK Actually Needs to Generate

Instead of `.vfl` files, POTK should generate:

### A. Material Builder Preset (`.hdanc` or `.hda`)
- Pre-configured Karma Lens Shader
- With polynomial VOP network
- Ready to apply to camera

### B. Python Script to Build Lens Shader
- Creates material network procedurally
- Sets polynomial coefficients as parameters
- Applies to camera automatically

### C. Compositing Nodes (`.cpio` file)
- COP network for post-process distortion
- Configured with POTK polynomial coefficients

---

## Let me create the RIGHT solution...

I'll create a Python script that:
1. Creates a Karma lens shader material in Houdini
2. Builds the polynomial VOP network
3. Sets your POTK coefficients as parameters
4. Applies it to a camera automatically

This will actually work in Houdini. Give me a moment...
