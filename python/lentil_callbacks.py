"""
lentil_callbacks.py - Parameter callbacks for lentil camera controls

This module handles parameter changes for lentil cameras.
When parameters change, we update the camera's USD properties to apply the effects.
"""

import hou


def assign_lens_material(camera_node, focal_length, fstop, focus_distance, sensor_width):
    """
    Assign Karma lens material to camera

    Karma uses "lens materials" (USD materials) instead of direct shader paths.
    This creates/assigns a Karma Lens Material LOP node.
    """
    try:
        # Get the LOP network containing the camera
        lop_network = camera_node.parent()

        # Look for lens material parameter on camera
        # Common parameter names: lensmaterial, karmamaterial, lensshader:surface
        lens_material_parm = None
        for parm_name in ['lensmaterial', 'karmamaterial', 'lensshader:surface', 'lens:shader']:
            if camera_node.parm(parm_name):
                lens_material_parm = camera_node.parm(parm_name)
                break

        if not lens_material_parm:
            print("  NOTE: Camera doesn't have lens material parameter")
            print("  Lens shader assignment not supported on this camera type")
            print("  Using Karma's built-in DOF only")
            return

        # Check if lens material node already exists
        lens_mat_node = lop_network.node('lentil_lens_material')

        if not lens_mat_node:
            # Create Karma Lens Material LOP node
            lens_mat_node = lop_network.createNode('karmalensmaterial', 'lentil_lens_material')
            lens_mat_node.moveToGoodPosition()
            print(f"  Created Karma Lens Material node: {lens_mat_node.path()}")

        # Set lens material path on camera
        material_path = '/LensMaterials/lentil_lens_material'
        lens_material_parm.set(material_path)

        print(f"  Assigned lens material: {material_path}")
        print(f"  NOTE: Lens materials only work with Karma CPU, not Karma XPU!")

    except Exception as e:
        print(f"  WARNING: Failed to assign lens material: {e}")
        import traceback
        traceback.print_exc()


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

    # Assign Karma lens shader via lens material
    # Modern Karma uses "lens materials" instead of direct shader assignment
    assign_lens_material(node, focal_length, fstop, focus_distance, sensor_width)


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

    # Clear lens material assignment (try multiple parameter names)
    for parm_name in ['lensmaterial', 'karmamaterial', 'lensshader:surface', 'lens:shader', 'lensshader']:
        if node.parm(parm_name):
            node.parm(parm_name).set('')

    print(f"  Disabled DOF and cleared lens material")


def update_lens_parameters(kwargs):
    """
    Called when lens-related parameters change
    Re-applies the lentil settings if enabled
    """
    node = kwargs['node']

    # Only re-apply if lentil is currently enabled
    if node.evalParm('enable_lentil'):
        apply_lentil_to_camera(node)
