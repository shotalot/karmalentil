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

    # DEBUG: Print what we're reading
    print(f"  Reading lentil parameters:")
    print(f"    lentil_focal_length = {focal_length}")
    print(f"    lentil_fstop = {fstop}")
    print(f"    lentil_focus_distance = {focus_distance}")
    print(f"    lentil_sensor_width = {sensor_width}")

    # DEBUG: List all camera parameters to find the right names
    print(f"  Available camera parameters:")
    all_parms = [p.name() for p in node.parms()]
    camera_parms = [p for p in all_parms if any(keyword in p.lower() for keyword in ['focal', 'focus', 'fstop', 'aperture', 'dof'])]
    for p in camera_parms:
        print(f"    - {p}")

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
        print(f"  Setting focalLength to {focal_length}mm")
        node.parm('focalLength').set(focal_length)  # in mm
    elif node.parm('focal'):
        focal_cm = focal_length / 10.0  # mm to cm
        print(f"  Setting focal to {focal_cm}cm")
        node.parm('focal').set(focal_cm)

    # F-stop
    # LOP cameras use camelCase: 'fStop' not 'fstop'!
    if node.parm('fStop'):
        print(f"  Setting fStop to {fstop}")
        node.parm('fStop').set(fstop)
    elif node.parm('fstop'):
        print(f"  Setting fstop to {fstop}")
        node.parm('fstop').set(fstop)

    # Focus distance
    # LOP cameras use camelCase: 'focusDistance' not 'focusdistance'!
    if node.parm('focusDistance'):
        print(f"  Setting focusDistance to {focus_distance_m}m")
        node.parm('focusDistance').set(focus_distance_m)
    elif node.parm('focus'):
        print(f"  Setting focus to {focus_distance_m}m")
        node.parm('focus').set(focus_distance_m)

    # Enable depth of field
    # LOP cameras may not have this toggle - DOF is always on if fstop < inf
    if node.parm('dof'):
        node.parm('dof').set(1)
    elif node.parm('depthoffield'):
        node.parm('depthoffield').set(1)

    # Set aperture (sensor width)
    # LOP cameras use camelCase: 'horizontalAperture' not 'aperture'!
    aperture_cm = sensor_width / 10.0  # mm to cm
    if node.parm('horizontalAperture'):
        print(f"  Setting horizontalAperture to {aperture_cm}cm")
        node.parm('horizontalAperture').set(aperture_cm)
    elif node.parm('aperture'):
        print(f"  Setting aperture to {aperture_cm}cm")
        node.parm('aperture').set(aperture_cm)

    print(f"  ✓ Applied DOF: focal={focal_length}mm, f/{fstop}, focus={focus_distance}mm")
    print(f"  TIP: Render or use Karma viewport to see depth of field effect")

    # TODO: Apply polynomial optics shader when implemented
    # For now, we're using Karma's built-in DOF which will show a visible effect


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
