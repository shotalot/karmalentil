"""
lentil_callbacks.py - Parameter callbacks for lentil camera controls

This module handles parameter changes for lentil cameras.
When parameters change, we update the camera's USD properties to apply the effects.
"""

import hou


def _detect_karma_renderer(camera_node):
    """
    Detect whether Karma CPU or XPU is being used

    Returns:
        str: 'cpu', 'xpu', or 'unknown'
    """
    try:
        # Try to find a Karma render settings LOP in the network
        lop_network = camera_node.parent()

        # Look for karma render settings nodes
        for node in lop_network.children():
            if node.type().name() in ['karmarenderproperties', 'usdrendersettings']:
                # Check for renderer parameter
                if node.parm('renderer'):
                    renderer = node.evalParm('renderer')
                    if 'xpu' in renderer.lower():
                        return 'xpu'
                    elif 'cpu' in renderer.lower():
                        return 'cpu'

                # Check for karma:renderMode parameter
                if node.parm('karma:renderMode'):
                    render_mode = node.evalParm('karma:renderMode')
                    if render_mode == 1:  # XPU mode
                        return 'xpu'
                    else:
                        return 'cpu'

        # Default to CPU if not specified (safer assumption)
        return 'cpu'

    except Exception as e:
        print(f"  Note: Could not detect renderer type: {e}")
        return 'unknown'


def _set_lens_material_parameters(lens_mat_node, camera_node, lens_data, focal_length, fstop, focus_distance, sensor_width):
    """
    Set lens shader parameters on the Karma Lens Material node

    This passes all lens parameters and polynomial coefficients to the VEX shader.
    If parameters don't exist on the node, they're added as spare parameters.
    """
    try:
        # Get parameter template group for adding spare parameters
        ptg = lens_mat_node.parmTemplateGroup()

        # Helper function to set or create parameter
        def set_or_create_parm(name, value, parm_type='float', label=None, size=1):
            """Set parameter value, creating it as spare if it doesn't exist"""
            if lens_mat_node.parm(name):
                if size == 1:
                    lens_mat_node.parm(name).set(value)
                else:
                    # For tuple parameters
                    for i in range(min(size, len(value) if hasattr(value, '__len__') else size)):
                        parm = lens_mat_node.parm(f"{name}{i}")
                        if parm:
                            parm.set(value[i] if hasattr(value, '__len__') else value)
            else:
                # Create spare parameter
                if parm_type == 'float':
                    if size == 1:
                        template = hou.FloatParmTemplate(name, label or name, 1, default_value=(value,))
                    else:
                        template = hou.FloatParmTemplate(name, label or name, size)
                elif parm_type == 'int':
                    template = hou.IntParmTemplate(name, label or name, 1, default_value=(value,))
                elif parm_type == 'toggle':
                    template = hou.ToggleParmTemplate(name, label or name, default_value=value)
                elif parm_type == 'string':
                    template = hou.StringParmTemplate(name, label or name, 1, default_value=(value,))

                ptg.append(template)
                lens_mat_node.setParmTemplateGroup(ptg)

                # Now set the value
                if size == 1:
                    lens_mat_node.parm(name).set(value)
                else:
                    for i in range(min(size, len(value) if hasattr(value, '__len__') else size)):
                        parm = lens_mat_node.parm(f"{name}{i}")
                        if parm:
                            parm.set(value[i] if hasattr(value, '__len__') else value)

        # Helper to set array parameter (creates multiple indexed parameters)
        # Returns list of (parm_name, value) tuples to set after PTG is applied
        def prepare_array_parm(name, values, label=None):
            """Prepare array parameter templates (to be batched with other operations)"""
            nonlocal ptg

            # Remove old array parameters if they exist
            for i in range(100):  # Reasonable max
                parm_name = f"{name}{i}"
                if lens_mat_node.parm(parm_name):
                    try:
                        pt = ptg.find(parm_name)
                        if pt:
                            ptg.remove(pt)
                    except:
                        pass

            # Create new array parameter templates
            value_list = []
            for i, value in enumerate(values):
                parm_name = f"{name}{i}"
                template = hou.FloatParmTemplate(
                    parm_name,
                    f"{label or name}[{i}]",
                    1,
                    default_value=(value,)
                )
                ptg.append(template)
                value_list.append((parm_name, value))

            return value_list

        # === Basic Camera Parameters ===
        set_or_create_parm('focal_length', focal_length, 'float', 'Focal Length (mm)')
        set_or_create_parm('fstop', fstop, 'float', 'F-Stop')
        set_or_create_parm('focus_distance', focus_distance, 'float', 'Focus Distance (mm)')
        set_or_create_parm('sensor_width', sensor_width, 'float', 'Sensor Width (mm)')

        # === Lens Effect Parameters (from camera lentil params) ===
        if camera_node.parm('lentil_chromatic_aberration'):
            chromatic = camera_node.evalParm('lentil_chromatic_aberration')
            set_or_create_parm('chromatic_aberration', chromatic, 'float', 'Chromatic Aberration')

        if camera_node.parm('lentil_bokeh_blades'):
            blades = camera_node.evalParm('lentil_bokeh_blades')
            set_or_create_parm('bokeh_blades', blades, 'int', 'Bokeh Blades')

        if camera_node.parm('lentil_bokeh_rotation'):
            rotation = camera_node.evalParm('lentil_bokeh_rotation')
            set_or_create_parm('bokeh_rotation', rotation, 'float', 'Bokeh Rotation')

        if camera_node.parm('lentil_bokeh_intensity'):
            intensity = camera_node.evalParm('lentil_bokeh_intensity')
            set_or_create_parm('bokeh_intensity', intensity, 'float', 'Bokeh Intensity')

        # === Polynomial Parameters ===
        poly_degree = lens_data.get('polynomial_degree', 5)
        set_or_create_parm('polynomial_degree', poly_degree, 'int', 'Polynomial Degree')
        set_or_create_parm('use_polynomial', 1, 'toggle', 'Use Polynomial Optics')
        set_or_create_parm('enable_lentil', 1, 'toggle', 'Enable Lentil')

        # === Polynomial Coefficients ===
        # Prepare coefficient arrays (batched - PTG applied once)
        coeffs = lens_data.get('coefficients', {})
        coefficient_values = []

        # Exit pupil X and Y coefficients
        if 'exit_pupil_x' in coeffs:
            coeffs_x = coeffs['exit_pupil_x']
            x_values = prepare_array_parm('poly_coeffs_x', coeffs_x, 'Polynomial Coefficients X')
            coefficient_values.extend(x_values)
            print(f"    Prepared {len(coeffs_x)} X coefficients")

        if 'exit_pupil_y' in coeffs:
            coeffs_y = coeffs['exit_pupil_y']
            y_values = prepare_array_parm('poly_coeffs_y', coeffs_y, 'Polynomial Coefficients Y')
            coefficient_values.extend(y_values)
            print(f"    Prepared {len(coeffs_y)} Y coefficients")

        # Apply all parameter template changes at once (optimization)
        if coefficient_values:
            lens_mat_node.setParmTemplateGroup(ptg)

            # Now set all the coefficient values
            for parm_name, value in coefficient_values:
                if lens_mat_node.parm(parm_name):
                    lens_mat_node.parm(parm_name).set(value)

        print(f"  Set all lens parameters on material node")

    except Exception as e:
        print(f"  WARNING: Failed to set lens material parameters: {e}")
        import traceback
        traceback.print_exc()


def assign_lens_material(camera_node, focal_length, fstop, focus_distance, sensor_width):
    """
    Assign Karma lens material to camera with polynomial lens data

    Karma uses "lens materials" (USD materials) instead of direct shader paths.
    This creates/assigns a Karma Lens Material LOP node and sets shader parameters.

    Note: Custom lens shaders only work with Karma CPU, not XPU (GPU).
    For XPU, this falls back to built-in DOF parameters.
    """
    try:
        # Detect renderer type (CPU vs XPU)
        renderer_type = _detect_karma_renderer(camera_node)

        if renderer_type == 'xpu':
            print("  ⚠ Karma XPU detected - custom lens shaders not supported")
            print("  → Using built-in DOF parameters instead")
            print("  → For polynomial lens effects, switch to Karma CPU renderer")
            # Skip lens material assignment for XPU, just use built-in DOF
            return

        # Get the LOP network containing the camera
        lop_network = camera_node.parent()

        # Look for lens material parameter on camera
        # Try multiple possible parameter names (USD namespace and camelCase variants)
        lens_material_parm = None
        possible_names = [
            'karma:lens:surface',      # USD namespace format (most likely)
            'karma:lens:material',     # Alternative USD format
            'ri:lens:surface',         # Renderman-style convention
            'lensMaterial',            # camelCase following other camera params
            'lensmaterial',            # lowercase variant
            'lensshader:surface',      # Legacy format
            'lens:shader'              # Simplified namespace
        ]

        for parm_name in possible_names:
            if camera_node.parm(parm_name):
                lens_material_parm = camera_node.parm(parm_name)
                print(f"  Found lens material parameter: '{parm_name}'")
                break

        if not lens_material_parm:
            # Debug: Print available parameters in Karma tab to help identify the right one
            print("  NOTE: Camera doesn't have recognized lens material parameter")
            print("  Available parameters on camera:")
            for parm in camera_node.parms():
                if 'karma' in parm.name().lower() or 'lens' in parm.name().lower():
                    print(f"    - {parm.name()} = {parm.eval()}")
            print("  Using Karma's built-in DOF only (no custom lens shader)")
            return

        # Check if lens material node already exists
        lens_mat_node = lop_network.node('lentil_lens_material')
        node_created = False

        if not lens_mat_node:
            # Create Karma Lens Material LOP node
            lens_mat_node = lop_network.createNode('karmalensmaterial', 'lentil_lens_material')
            node_created = True

            # Position it near the camera for visual organization
            camera_pos = camera_node.position()
            lens_mat_node.setPosition(camera_pos + hou.Vector2(0, -1.5))

            # Set color to distinguish it (light blue)
            lens_mat_node.setColor(hou.Color(0.4, 0.6, 1.0))

            print(f"  Created Karma Lens Material node: {lens_mat_node.path()}")
        else:
            print(f"  Using existing Karma Lens Material node: {lens_mat_node.path()}")

        # Get VEX shader path
        karmalentil_path = hou.getenv('KARMALENTIL')
        if not karmalentil_path:
            print("  ERROR: $KARMALENTIL environment variable not set")
            return

        shader_path = f"{karmalentil_path}/vex/karma_lentil_lens.vfl"

        # Set VEX shader path on the Karma Lens Material node
        # Only set if newly created or if shader path is different (optimization)
        shader_parm = None
        shader_parm_names = [
            'lenssurfaceshader',    # Most likely name
            'lensshader',           # Alternative
            'shader',               # Generic
            'surface',              # VOP-style
            'lenssurface'           # Another variant
        ]

        for parm_name in shader_parm_names:
            if lens_mat_node.parm(parm_name):
                shader_parm = lens_mat_node.parm(parm_name)
                current_path = shader_parm.eval()

                # Only update if different (avoid redundant updates)
                if current_path != shader_path or node_created:
                    shader_parm.set(shader_path)
                    print(f"  Set lens shader on material node parameter '{parm_name}': {shader_path}")
                break

        if not shader_parm:
            print(f"  WARNING: Could not find shader path parameter on Karma Lens Material node")
            print(f"  Available parameters on lens material node:")
            for parm in lens_mat_node.parms():
                print(f"    - {parm.name()}")

        # Set lens material path on camera (USD material reference)
        # The path should match the USD primitive path created by the Karma Lens Material node
        material_path = lens_mat_node.evalParm('matpath') if lens_mat_node.parm('matpath') else '/LensMaterials/lentil_lens_material'
        lens_material_parm.set(material_path)
        print(f"  Assigned lens material path to camera: {material_path}")

        # Load lens database and get polynomial coefficients
        from lens_database import get_lens_database
        db = get_lens_database()

        # Get selected lens model from camera
        lens_model = camera_node.evalParm('lens_model') if camera_node.parm('lens_model') else 'double_gauss_50mm'

        # Get polynomial coefficients from database
        lens_data = db.get_lens(lens_model)
        if lens_data:
            coeffs = lens_data.get('coefficients', {})
            poly_degree = lens_data.get('polynomial_degree', 5)

            # Set lens parameters on the Karma Lens Material node
            # These will be passed to the VEX shader
            _set_lens_material_parameters(
                lens_mat_node,
                camera_node,
                lens_data,
                focal_length,
                fstop,
                focus_distance,
                sensor_width
            )

            print(f"  Loaded lens data: {lens_data.get('name', lens_model)}")
            print(f"  Polynomial degree: {poly_degree}")
            print(f"  Set polynomial coefficients on lens material node")
        else:
            print(f"  WARNING: Lens '{lens_model}' not found in database")

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

    # Clear lens material assignment (try all possible parameter names)
    lens_parm_names = [
        'karma:lens:surface',
        'karma:lens:material',
        'ri:lens:surface',
        'lensMaterial',
        'lensmaterial',
        'karmamaterial',
        'lensshader:surface',
        'lens:shader',
        'lensshader'
    ]

    cleared = False
    for parm_name in lens_parm_names:
        if node.parm(parm_name):
            node.parm(parm_name).set('')
            cleared = True
            print(f"  Cleared lens material from parameter: {parm_name}")
            break

    if not cleared:
        print(f"  Note: No lens material parameter found to clear")

    print(f"  Disabled DOF and lens material")


def on_lens_model_changed(kwargs):
    """
    Called when the lens_model parameter is changed

    This automatically updates lens parameters (focal length, max f-stop, etc.)
    from the selected lens model in the database.
    """
    node = kwargs['node']

    # Get selected lens model
    lens_model = node.evalParm('lens_model')

    # Load lens database
    try:
        from lens_database import get_lens_database
        db = get_lens_database()

        lens_data = db.get_lens(lens_model)
        if lens_data:
            # Update focal length from lens data
            if node.parm('lentil_focal_length') and 'focal_length' in lens_data:
                node.parm('lentil_focal_length').set(lens_data['focal_length'])

            # Update max f-stop if available
            if node.parm('lentil_fstop') and 'max_fstop' in lens_data:
                # Set to max f-stop (widest aperture) by default
                node.parm('lentil_fstop').set(lens_data['max_fstop'])

            print(f"KarmaLentil: Loaded lens '{lens_data.get('name', lens_model)}'")
            print(f"  Focal length: {lens_data.get('focal_length', 'N/A')}mm")
            print(f"  Max aperture: f/{lens_data.get('max_fstop', 'N/A')}")

            # Re-apply lentil if enabled
            if node.evalParm('enable_lentil'):
                apply_lentil_to_camera(node)
        else:
            print(f"KarmaLentil: WARNING - Lens '{lens_model}' not found in database")

    except Exception as e:
        print(f"KarmaLentil: ERROR loading lens model: {e}")
        import traceback
        traceback.print_exc()


def update_lens_parameters(kwargs):
    """
    Called when lens-related parameters change
    Re-applies the lentil settings if enabled
    """
    node = kwargs['node']

    # Only re-apply if lentil is currently enabled
    if node.evalParm('enable_lentil'):
        apply_lentil_to_camera(node)
