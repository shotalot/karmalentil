"""
lentil_callbacks.py - Parameter callbacks for lentil camera controls

This module handles parameter changes for lentil cameras.
When parameters change, we update the camera's USD properties to apply the effects.
"""

import hou


def on_enable_changed(kwargs):
    """
    Called when the enable_lentil parameter is changed

    This applies lentil settings to the camera's USD properties
    """
    node = kwargs['node']

    # Get parameter values
    enable = node.evalParm('enable_lentil')

    if enable:
        # Lentil is enabled - apply settings
        apply_lentil_to_camera(node)
        print(f"KarmaLentil: Enabled on {node.path()}")
    else:
        # Lentil is disabled - restore defaults
        disable_lentil_on_camera(node)
        print(f"KarmaLentil: Disabled on {node.path()}")


def apply_lentil_to_camera(node):
    """
    Apply lentil parameters to the camera's USD properties

    This sets depth of field and other camera properties based on
    the lentil parameters.
    """
    # Get lentil parameters
    focal_length = node.evalParm('lentil_focal_length')  # mm
    fstop = node.evalParm('lentil_fstop')
    focus_distance = node.evalParm('lentil_focus_distance')  # mm
    sensor_width = node.evalParm('lentil_sensor_width')  # mm

    # Validate parameters - don't apply if they're invalid
    if focal_length <= 0:
        print(f"  ERROR: Invalid focal length ({focal_length}), skipping application")
        return
    if fstop <= 0:
        print(f"  ERROR: Invalid f-stop ({fstop}), skipping application")
        return

    # Convert focus distance from mm to Houdini units (cm to meters)
    # Houdini typically uses meters, lens database uses mm
    focus_distance_m = focus_distance / 1000.0  # mm to meters

    # Set the camera's native DOF parameters
    # These control Karma's depth of field rendering

    # Focal length
    # LOP cameras use camelCase: 'focalLength' not 'focallength'!
    if node.parm('focalLength'):
        node.parm('focalLength').set(focal_length)  # in mm
    elif node.parm('focal'):
        focal_cm = focal_length / 10.0  # mm to cm
        node.parm('focal').set(focal_cm)

    # F-stop
    # LOP cameras use camelCase: 'fStop' not 'fstop'!
    if node.parm('fStop'):
        node.parm('fStop').set(fstop)
    elif node.parm('fstop'):
        node.parm('fstop').set(fstop)

    # Focus distance
    # LOP cameras use camelCase: 'focusDistance' not 'focusdistance'!
    if node.parm('focusDistance'):
        node.parm('focusDistance').set(focus_distance_m)
    elif node.parm('focus'):
        node.parm('focus').set(focus_distance_m)

    # Enable depth of field
    # LOP cameras may not have this toggle - DOF is always on if fstop < inf
    if node.parm('dof'):
        node.parm('dof').set(1)
    elif node.parm('depthoffield'):
        node.parm('depthoffield').set(1)

    # Set aperture (sensor width)
    # NOTE: Don't set this - it changes the field of view!
    # The sensor_width parameter is used for polynomial calculations,
    # but we shouldn't override the camera's existing sensor size
    # as it will change the framing/zoom of the image.

    # TODO: Apply polynomial optics shader when implemented
    # For now, we're using Karma's built-in DOF which will show a visible effect

    # Assign Karma lens shader (Karma CPU only - NOT XPU!)
    # Get path to compiled lens shader
    import os
    karmalentil_path = node.evalParm('KARMALENTIL') if node.parm('KARMALENTIL') else os.getenv('KARMALENTIL')

    if karmalentil_path:
        # Path to VEX lens shader
        vex_path = os.path.join(karmalentil_path, 'vex', 'karma_lentil_lens.vfl')

        # Check if lens shader parameter exists
        if node.parm('lensshader'):
            # Assign lens shader
            node.parm('lensshader').set(vex_path)
            print(f"  Assigned Karma lens shader: {vex_path}")
            print(f"  NOTE: Lens shader only works with Karma CPU, not Karma XPU!")
        else:
            print(f"  WARNING: Camera doesn't have 'lensshader' parameter")
            print(f"  Lens shader assignment not supported on this camera type")


def disable_lentil_on_camera(node):
    """
    Disable lentil on the camera - restore default DOF off
    """
    # Disable depth of field (or set fstop very high to effectively disable)
    # LOP cameras use camelCase parameter names
    if node.parm('dof'):
        node.parm('dof').set(0)
    elif node.parm('depthoffield'):
        node.parm('depthoffield').set(0)
    else:
        # If no DOF toggle exists, set fstop to very high value
        if node.parm('fStop'):
            node.parm('fStop').set(64.0)
        elif node.parm('fstop'):
            node.parm('fstop').set(64.0)

    # Clear lens shader
    if node.parm('lensshader'):
        node.parm('lensshader').set('')

    print(f"  Disabled DOF on camera")


def update_lens_parameters(kwargs):
    """
    Called when lens-related parameters change
    Re-applies the lentil settings if enabled
    """
    node = kwargs['node']

    # Only re-apply if lentil is currently enabled
    if node.evalParm('enable_lentil'):
        apply_lentil_to_camera(node)
