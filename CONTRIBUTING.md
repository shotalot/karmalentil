# Contributing to KarmaLentil

Thank you for your interest in contributing to KarmaLentil!

## How to Contribute

### Reporting Issues

If you encounter bugs or have feature requests:

1. Check if the issue already exists
2. Provide detailed information:
   - Houdini version
   - Karma renderer (CPU/XPU)
   - Lens model used
   - VEX compilation errors (if applicable)
   - Steps to reproduce

### Adding New Lenses

To contribute new lens models:

1. **Obtain lens data** from the original lentil repository:
   - Clone https://github.com/zpelgrims/lentil
   - Find the lens in `polynomial-optics/database/lenses/`
   - Use a lens with pre-generated `code/` files

2. **Convert to VEX**:
   ```bash
   python python/import_lens.py \
       /path/to/lentil/polynomial-optics/database/lenses/[LENS_PATH] \
       [NEW_LENS_NAME]
   ```

3. **Test the lens**:
   - Verify VEX compilation
   - Test with Karma renders
   - Check for artifacts

4. **Submit a pull request**:
   - Include lens data in `lenses/[NEW_LENS_NAME]/`
   - Update README.md with lens name
   - Add example renders (optional)

### Improving VEX Code

If you improve the VEX implementation:

1. **Test thoroughly**:
   - Test with multiple lenses
   - Verify performance impact
   - Check for VEX compilation issues

2. **Document changes**:
   - Update code comments
   - Update USAGE.md if parameters change
   - Note any breaking changes

3. **Submit pull request**:
   - Clear description of changes
   - Before/after comparisons (if applicable)

### Creating HDAs

We welcome contributions for:

- Camera HDA with integrated lentil shader
- Lens selector HDA
- Parameter presets

Requirements:
- Must work with Houdini 20.5+
- Should be platform-independent
- Include documentation

### Documentation

Improvements to documentation are always welcome:

- Fixing typos or unclear explanations
- Adding examples
- Translating to other languages
- Creating video tutorials

## Development Setup

### Testing Changes

1. Install development version:
   ```bash
   export HOUDINI_PATH="/path/to/your/fork/karmalentil:&"
   ```

2. Test in Houdini:
   - Create test scenes
   - Try different lens configurations
   - Verify Karma rendering

3. Validate VEX syntax:
   - Check for compilation errors
   - Test include paths
   - Verify all lens files compile

### Code Style

**VEX Code**:
- Use 4-space indentation
- Comment complex polynomial terms
- Use descriptive variable names
- Include function documentation

**Python Code**:
- Follow PEP 8 style guide
- Use docstrings for functions
- Include type hints where appropriate

**Documentation**:
- Use markdown format
- Include code examples
- Provide clear, concise explanations

## Areas for Improvement

Current priorities for contribution:

1. **HDA Creation**: Package VEX shader into easy-to-use HDA
2. **Additional Lenses**: Port more lenses from lentil database
3. **Performance**: Optimize polynomial evaluation
4. **Features**:
   - Bidirectional filtering implementation
   - Aperture texture support
   - Anamorphic lens support
5. **Documentation**: Video tutorials, more examples
6. **Testing**: Automated VEX compilation tests

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to open an issue for questions about contributing.

## Credits

Contributors will be acknowledged in README.md.

Thank you for helping make KarmaLentil better!
