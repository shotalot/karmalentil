#!/usr/bin/env python
"""
Import Lens Data from Lentil Repository
Converts C/C++ polynomial code to VEX-compatible format
"""

import os
import sys
import re
import argparse


def convert_c_to_vex(c_code):
    """
    Convert C polynomial code to VEX syntax
    - Replace pow(x, n) with lens_ipow(x, n) for integer powers
    - Adjust function signatures
    """
    vex_code = c_code

    # Replace common C patterns with VEX equivalents
    # pow(base, exp) -> lens_ipow(base, exp) for small integer exponents
    def replace_pow(match):
        base = match.group(1)
        exp = match.group(2)
        try:
            exp_int = int(float(exp))
            if exp_int == int(float(exp)) and exp_int <= 10:
                return f"lens_ipow({base}, {exp_int})"
        except:
            pass
        return f"pow({base}, {exp})"

    vex_code = re.sub(r'pow\((.*?),\s*(.*?)\)', replace_pow, vex_code)

    # Replace static inline with function
    vex_code = vex_code.replace('static inline void', 'function void')
    vex_code = vex_code.replace('static void', 'function void')
    vex_code = vex_code.replace('inline void', 'function void')

    # Replace const with VEX constants (if needed)
    # VEX uses #define for constants

    return vex_code


def import_lens_constants(lens_path, output_path):
    """
    Import lens_constants.h from lentil repository
    """
    constants_file = os.path.join(lens_path, 'code', 'lens_constants.h')

    if not os.path.exists(constants_file):
        print(f"Error: {constants_file} not found")
        return False

    with open(constants_file, 'r') as f:
        content = f.read()

    # Convert to VEX format (mostly compatible already)
    vex_content = content.replace('static const', 'const')

    output_file = os.path.join(output_path, 'lens_constants.h')
    os.makedirs(output_path, exist_ok=True)

    with open(output_file, 'w') as f:
        f.write(vex_content)

    print(f"Imported lens constants to {output_file}")
    return True


def import_pt_evaluate(lens_path, output_path):
    """
    Import pt_evaluate.h and convert to VEX
    """
    pt_eval_file = os.path.join(lens_path, 'code', 'pt_evaluate.h')

    if not os.path.exists(pt_eval_file):
        print(f"Error: {pt_eval_file} not found")
        return False

    with open(pt_eval_file, 'r') as f:
        content = f.read()

    # Convert to VEX format
    vex_content = convert_c_to_vex(content)

    # Adjust function signature for VEX
    vex_content = re.sub(
        r'static inline void evaluate\(',
        'function void pt_evaluate(',
        vex_content
    )

    # Add export keyword for output parameters
    vex_content = re.sub(
        r'void pt_evaluate\((.*?)float out\[',
        r'void pt_evaluate(\1export float out[',
        vex_content
    )

    output_file = os.path.join(output_path, 'pt_evaluate.h')

    with open(output_file, 'w') as f:
        f.write(vex_content)

    print(f"Imported pt_evaluate to {output_file}")
    return True


def import_pt_sample_aperture(lens_path, output_path):
    """
    Import pt_sample_aperture.h and convert to VEX
    """
    pt_sample_file = os.path.join(lens_path, 'code', 'pt_sample_aperture.h')

    if not os.path.exists(pt_sample_file):
        print(f"Warning: {pt_sample_file} not found (optional)")
        return True  # Not critical

    with open(pt_sample_file, 'r') as f:
        content = f.read()

    # Convert to VEX format
    vex_content = convert_c_to_vex(content)

    # Adjust function signature
    vex_content = re.sub(
        r'static inline int sample_aperture\(',
        'function int pt_sample_aperture(',
        vex_content
    )

    output_file = os.path.join(output_path, 'pt_sample_aperture.h')

    with open(output_file, 'w') as f:
        f.write(vex_content)

    print(f"Imported pt_sample_aperture to {output_file}")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Import lens data from lentil repository to karmalentil'
    )
    parser.add_argument(
        'lens_path',
        help='Path to lens directory in lentil repo (e.g., polynomial-optics/database/lenses/1953-angenieux-double-gauss/49mm)'
    )
    parser.add_argument(
        'lens_name',
        help='Name for the lens in karmalentil (e.g., double_gauss_50mm)'
    )
    parser.add_argument(
        '--karmalentil-root',
        default='.',
        help='Root directory of karmalentil repository'
    )

    args = parser.parse_args()

    lens_path = args.lens_path
    lens_name = args.lens_name
    karmalentil_root = args.karmalentil_root

    # Create output directory
    output_path = os.path.join(karmalentil_root, 'lenses', lens_name)

    print(f"Importing lens from {lens_path}")
    print(f"Output to {output_path}")

    # Import each component
    success = True
    success &= import_lens_constants(lens_path, output_path)
    success &= import_pt_evaluate(lens_path, output_path)
    success &= import_pt_sample_aperture(lens_path, output_path)

    if success:
        print(f"\nSuccessfully imported lens '{lens_name}'")
        print(f"Lens data available at: {output_path}")
        print(f"\nNext steps:")
        print(f"1. Review the generated VEX code for any syntax issues")
        print(f"2. Update vex/camera/lentil_camera.vfl to include this lens")
        print(f"3. Test with Karma renderer")
    else:
        print("\nImport failed - please check errors above")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
