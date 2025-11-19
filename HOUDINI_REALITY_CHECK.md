# POTK + Houdini: The Reality

**Problem:** Houdini Karma doesn't have a simple "load .vfl lens shader" button.

**Solution:** Use one of these REAL approaches that actually work.

---

## Quick Solution: Use Built-in Lens Distortion

The simplest way to get lens effects in Karma RIGHT NOW:

### 1. Select Camera
- In Scene View, select your camera

### 2. Enable Lens Distortion
- Parameter panel → **View tab**
- Scroll to **Sampling section**
- Find **Lens Distortion** subsection
- Check ☑ **Use Lens Distortion**

### 3. Adjust Parameters
- **k1** (barrel/pincushion): -0.2 to 0.2
  - Negative = barrel (fisheye effect)
  - Positive = pincushion
- **k2** (higher order): Fine-tune distortion
- **Center**: Where distortion centers (usually 0.5, 0.5)

### 4. Render
- Your renders will now have lens distortion!

**Pros:** Works immediately, no coding
**Cons:** Limited to simple distortion model

---

## Better Solution: Compositing Distortion

Apply lens distortion in post-process (like real VFX pipelines do it):

### 1. Render Clean
- Render from Karma without distortion
- Save as EXR sequence

### 2. Add Lens Distortion in COPs
```
/img → Create Composite Network
  → File In (load your render)
  → Lens Distortion COP
  → File Out
```

### 3. Use POTK Coefficients
The Lens Distortion COP has polynomial parameters you can set from POTK data.

**Pros:** Industry standard, flexible, non-destructive
**Cons:** Extra compositing step

---

## Advanced Solution: Custom Lens Shader

For true polynomial lens rendering, you need a custom material:

### Current State:
- POTK generates coefficients ✓
- But Karma doesn't have "lens shader" slot the way I described ✗

### What You Actually Need:
1. **MaterialX shader** (Karma's native format)
2. **Or VOP network** built procedurally
3. **Or render distortion map** and apply in comp

---

## What Should POTK Actually Do?

Based on how Houdini/Karma actually works, POTK should:

### Option A: Generate Houdini Digital Asset (.hda)
```
potk_lens_50mm_f2.hda
  ├─ Camera with lens parameters
  ├─ Built-in coefficient UI
  └─ Karma render settings
```

### Option B: Generate Compositing Setup
```
potk_lens_distortion.cpio
  ├─ COP network
  ├─ Polynomial distortion nodes
  └─ POTK coefficients as parameters
```

### Option C: Generate ST-Map
```
Generate distortion displacement map:
  - Input: undistorted UV (0-1)
  - Output: distorted UV texture
  - Use in Karma as UV displacement
```

---

## Practical Next Steps

### For You Right Now:

**1. Use Built-in Distortion**
- Fastest way to see lens effects
- Camera → View → Lens Distortion → Enable
- Set k1 = -0.15 for barrel distortion
- Render and see results

**2. Or Use Compositing**
- Render clean
- Add Lens Distortion COP
- Manually set polynomial from POTK data

### For POTK Development:

**Need to pivot to generating:**
1. ✅ ST-Maps (displacement textures) - Easiest
2. ✅ HDA files (camera presets) - Most integrated
3. ✅ COP networks (compositing) - Most flexible

**NOT:**
- ❌ Standalone .vfl files (Karma doesn't load these for lenses)

---

## I'll Create the ST-Map Solution

ST-Maps are the most practical approach. Let me create a script that:
1. Takes POTK polynomial coefficients
2. Generates a distortion UV map (texture)
3. Shows you how to apply it in Karma

This will ACTUALLY work in Houdini. One moment...
