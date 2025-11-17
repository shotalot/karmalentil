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

    # Convert focus distance from mm to Houdini units (cm to meters)
    # Houdini typically uses meters, lens database uses mm
    focus_distance_m = focus_distance / 1000.0  # mm to meters

    # Set the camera's native DOF parameters
    # These control Karma's depth of field rendering

    # Focal length (convert mm to cm for Houdini)
    if node.parm('focal'):
        node.parm('focal').set(focal_length / 10.0)  # mm to cm

    # F-stop
    if node.parm('fstop'):
        node.parm('fstop').set(fstop)

    # Focus distance
    if node.parm('focus'):
        node.parm('focus').set(focus_distance_m)

    # Enable depth of field
    if node.parm('depthoffield'):
        node.parm('depthoffield').set(1)

    # Set aperture (sensor width)
    if node.parm('aperture'):
        node.parm('aperture').set(sensor_width / 10.0)  # mm to cm

    print(f"  Applied DOF: focal={focal_length}mm, f/{fstop}, focus={focus_distance}mm")
    print(f"  TIP: Render or use Karma viewport to see depth of field effect")

    # TODO: Apply polynomial optics shader when implemented
    # For now, we're using Karma's built-in DOF which will show a visible effect


def disable_lentil_on_camera(node):
    """
    Disable lentil on the camera - restore default DOF off
    """
    # Disable depth of field
    if node.parm('depthoffield'):
        node.parm('depthoffield').set(0)

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
