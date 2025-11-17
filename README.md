# KarmaLentil

Polynomial optics for Houdini Karma - realistic lens aberrations and bokeh effects.

Port of [lentil](https://github.com/zpelgrims/lentil) from Arnold to Houdini Karma.

## Features

- Physically-based lens aberration modeling using polynomial optics
- Chromatic aberration support
- Real-world lens models based on patent data
- Integration with Karma XPU and CPU renderers
- VEX-based implementation for performance

## Installation

### Quick Start

1. Set `HOUDINI_PATH` to include this repository:
   ```bash
   export HOUDINI_PATH="/path/to/karmalentil:&"
   ```

2. Launch Houdini 20.5+

3. Create a camera and add the "Karma Lentil Camera" properties

## Usage

1. Create a Karma camera in your scene
2. In the camera parameters, navigate to the "Lentil" tab
3. Select a lens model from the dropdown
4. Adjust focus distance and f-stop
5. Render with Karma

## Lens Models

Currently included sample lenses:
- Double Gauss 50mm f/2.8
- (More lenses coming soon)

## Technical Details

KarmaLentil uses sparse high-degree polynomials (degree 9-15) to model lens aberrations:
- Input: sensor position (x, y), aperture direction (dx, dy), wavelength (λ)
- Output: outer pupil position and direction with transmittance
- Evaluated in VEX for each camera ray in Karma

## Requirements

- Houdini 20.5 or later
- Karma renderer (CPU or XPU)

## Credits

Based on the original [lentil](https://github.com/zpelgrims/lentil) project by Zeno Pelgrims
- Original Arnold implementation: [www.lentil.xyz](http://www.lentil.xyz)
- Research paper: Polynomial Optics (Joo et al.)

## License

MIT License - See LICENSE file for details
