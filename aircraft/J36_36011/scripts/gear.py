"""Visible landing gear for the first J-36 demonstrator, public-photo reconstruction.

Overall arrangement follows photographed 36011. Small mechanical features are
visually plausible approximations and are not a claim of measured geometry.
"""
import bpy
from math import pi, sin, cos
from mathutils import Vector


def build_gear(materials):
    collection = bpy.data.collections.new('05 • Landing gear')
    bpy.context.scene.collection.children.link(collection)
    collection['basis'] = 'Public photo reconstruction; small mechanical details inferred.'
    created = []

    def own(obj, name, material):
        obj.name = name
        for current in list(obj.users_collection):
            current.objects.unlink(obj)
        collection.objects.link(obj)
        if material:
            obj.data.materials.append(material)
        obj['basis'] = 'Public photo reconstruction; small mechanical details inferred.'
        created.append(obj)
        return obj

    def material(name, color, metallic=0.0, roughness=0.4):
        mat = bpy.data.materials.new(name)
        mat.diffuse_color = (*color, 1)
        mat.use_nodes = True
        shader = mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Base Color'].default_value = (*color, 1)
        shader.inputs['Metallic'].default_value = metallic
        shader.inputs['Roughness'].default_value = roughness
        return mat

    enamel = material('Gear • warm ceramic white', (.68, .72, .73), .28, .29)
    tire_sidewall = material('Gear • satin rubber sidewall', (.018, .022, .025), .0, .67)
    recess = material('Gear • bay shadow', (.032, .039, .046), .12, .58)
    label = material('Gear • subtle casting highlight', (.25, .28, .29), .6, .32)
    paint = materials['paint']
    metal = materials['steel']
    titanium = materials['titanium']
    rubber = materials['rubber']
    dark = materials['dark']

    def smooth(obj):
        for face in obj.data.polygons:
            face.use_smooth = True
        return obj

    def rod(name, a, b, radius, mat, vertices=32):
        a, b = Vector(a), Vector(b)
        delta = b - a
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius,
            depth=delta.length, location=(a + b) * .5)
        obj = own(bpy.context.object, name, mat)
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = delta.to_track_quat('Z', 'Y')
        bevel = obj.modifiers.new('Machined edge radius', 'BEVEL')
        bevel.width = min(radius * .12, .007)
        bevel.segments = 2
        return smooth(obj)

    def ring(name, center, radius, thickness, mat):
        bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=10,
            location=center, rotation=(0, pi / 2, 0),
            major_radius=radius, minor_radius=thickness)
        return smooth(own(bpy.context.object, name, mat))

    def panel(name, coords, mat, thickness=.025):
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(coords, [], [tuple(range(len(coords)))])
        mesh.update()
        obj = own(bpy.data.objects.new(name, mesh), name, mat)
        if thickness:
            solid = obj.modifiers.new('Panel skin', 'SOLIDIFY')
            solid.thickness = thickness
            bevel = obj.modifiers.new('Panel edge break', 'BEVEL')
            bevel.width = .006
            bevel.segments = 2
        return obj

    def hose(name, points, thickness=.012):
        curve = bpy.data.curves.new(name, 'CURVE')
        curve.dimensions = '3D'
        curve.resolution_u = 14
        curve.bevel_depth = thickness
        curve.bevel_resolution = 3
        spline = curve.splines.new('BEZIER')
        spline.bezier_points.add(len(points) - 1)
        for point, co in zip(spline.bezier_points, points):
            point.co = co
            point.handle_left_type = 'AUTO'
            point.handle_right_type = 'AUTO'
        return own(bpy.data.objects.new(name, curve), name, rubber)

    def wheel(name, center, radius, width, sign):
        xc, yc, zc = center
        # Closed revolved tire section: rounded shoulders and molded tread grooves.
        profile = [(-.50, .51), (-.54, .67), (-.52, .81), (-.46, .92),
                   (-.36, .979), (-.29, .994), (-.26, .981), (-.23, .997),
                   (-.12, 1), (-.09, .985), (-.06, 1), (.06, 1),
                   (.09, .985), (.12, 1), (.23, .997), (.26, .981),
                   (.29, .994), (.36, .979), (.46, .92), (.52, .81),
                   (.54, .67), (.50, .51), (.34, .48), (-.34, .48)]
        vertices, faces = [], []
        segments = 96
        for xx, rr in profile:
            for i in range(segments):
                t = 2 * pi * i / segments
                vertices.append((xc + xx * width, yc + radius * rr * sin(t),
                                 max(.014, zc + radius * rr * cos(t))))
        for j in range(len(profile)):
            for i in range(segments):
                faces.append((j * segments + i, j * segments + (i + 1) % segments,
                    ((j + 1) % len(profile)) * segments + (i + 1) % segments,
                    ((j + 1) % len(profile)) * segments + i))
        mesh = bpy.data.meshes.new(name + ' • tire mesh')
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        tire = smooth(own(bpy.data.objects.new(name + ' • molded tire', mesh), name + ' • molded tire', rubber))
        tire.data.materials.append(tire_sidewall)
        for j in (0, 1, 2, 3, 18, 19, 20, 21, 22, 23):
            for face in tire.data.polygons[j * segments:(j + 1) * segments]:
                face.material_index = 1
        for side in (-1, 1):
            xx = xc + side * width * .50
            ring(name + ' • bead lip', (xx, yc, zc), radius * .49, radius * .018, metal)
            rod(name + ' • wheel web', (xx - .018, yc, zc), (xx + .018, yc, zc), radius * .458, enamel, 64)
            ring(name + ' • recessed rim', (xx + side * .022, yc, zc), radius * .402, radius * .015, titanium)
            # The black pockets suggest open web spokes without implausibly large bolts.
            for i in range(10):
                t = 2 * pi * i / 10
                hy = yc + cos(t) * radius * .295
                hz = zc + sin(t) * radius * .295
                rr = radius * .063
                rod(name + ' • brake ventilation pocket',
                    (xx + side * .022, hy, hz), (xx + side * .026, hy, hz), rr, recess, 16)
                hy2 = yc + cos(t) * radius * .175
                hz2 = zc + sin(t) * radius * .175
                rod(name + ' • hub fastener',
                    (xx + side * .027, hy2, hz2), (xx + side * .037, hy2, hz2), radius * .019, metal, 6)
            rod(name + ' • axle cap', (xx, yc, zc), (xx + side * .055, yc, zc), radius * .13, titanium, 40)
            ring(name + ' • bearing seal', (xx + side * .054, yc, zc), radius * .105, radius * .009, dark)
            ring(name + ' • sidewall molding', (xc + side * width * .535, yc, zc), radius * .70, radius * .0035, tire_sidewall)
        # Separate dark brake pack at inboard face.
        bx = xc - sign * width * .55
        rod(name + ' • brake pack', (bx, yc, zc), (bx - sign * .07, yc, zc), radius * .37, dark, 48)
        for i in range(3):
            ring(name + ' • brake disc edge', (bx - sign * i * .019, yc, zc), radius * .34, .007, metal)
        return tire

    def bay(name, coords):
        lower_z = 2.36 if name.startswith('NLG') else 2.25
        rim = [(x, y, lower_z) for x, y, z in coords]
        ceiling = [(x, y, 2.55) for x, y, z in coords]
        panel(name + ' • recessed ceiling', ceiling, recess, .009)
        for i, p in enumerate(rim):
            next_i = (i + 1) % len(rim)
            panel(name + ' • shallow bay side',
                  [p, rim[next_i], ceiling[next_i], ceiling[i]], recess, .009)
            rod(name + ' • perimeter lip', p, rim[next_i], .014, titanium, 16)

    for sign, suffix in ((-1, 'L'), (1, 'R')):
        x = sign * 2.35
        sx = sign * 2.08
        for y, tag in ((2.9, 'forward'), (4.1, 'aft')):
            wheel(f'MLG {suffix} {tag}', (x, y, .53), .52, .36, sign)
            rod(f'MLG {suffix} {tag} • axle', (sign * 1.96, y, .57), (sign * 2.42, y, .53), .072, titanium)
        rod(f'MLG {suffix} • tandem bogie beam', (sx, 2.79, .60), (sx, 4.21, .60), .095, enamel)
        rod(f'MLG {suffix} • bogie trunnion', (sign * 1.91, 3.5, .67), (sign * 2.24, 3.5, .67), .15, enamel)
        rod(f'MLG {suffix} • oleo outer barrel', (sx, 3.5, 1.28), (sign * 2.19, 3.54, 2.25), .116, enamel, 48)
        rod(f'MLG {suffix} • polished piston', (sx, 3.5, .76), (sx, 3.5, 1.40), .077, metal, 48)
        for z, r in ((1.30, .13), (1.38, .127), (2.12, .132)):
            rod(f'MLG {suffix} • oleo collar', (sx, 3.5, z - .035), (sx, 3.5, z + .035), r, enamel, 48)
        rod(f'MLG {suffix} • piston wiper', (sx, 3.5, 1.265), (sx, 3.5, 1.30), .12, dark, 48)
        rod(f'MLG {suffix} • diagonal drag brace', (sign * 1.31, 4.18, 2.24), (sx, 3.58, 1.04), .055, enamel)
        rod(f'MLG {suffix} • drag brace sliding section', (sign * 1.31, 4.18, 2.24), (sign * 1.64, 3.92, 1.75), .071, enamel)
        rod(f'MLG {suffix} • lateral stay', (sign * 2.91, 3.76, 2.25), (sx, 3.52, 1.33), .049, enamel)
        # Two parallel torque-link cheeks and their cross-pins.
        for offset in (-.075, .075):
            xx = sx + offset
            a, b, c = (xx, 3.36, 1.48), (xx, 3.12, 1.14), (xx, 3.35, .87)
            rod(f'MLG {suffix} • upper torque link', a, b, .032, enamel, 24)
            rod(f'MLG {suffix} • lower torque link', b, c, .034, enamel, 24)
        for y, z in ((3.36, 1.48), (3.12, 1.14), (3.35, .87)):
            rod(f'MLG {suffix} • torque link pin', (sx - .105, y, z), (sx + .105, y, z), .036, metal, 24)
        hose(f'MLG {suffix} • brake hydraulic line', [(sx + sign * .13, 3.58, 2.17),
             (sx + sign * .14, 3.64, 1.49), (sx + sign * .20, 3.76, 1.04),
             (sx + sign * .09, 3.87, .73), (x - sign * .19, 4.10, .58)], .011)
        hose(f'MLG {suffix} • forward brake branch', [(sx + sign * .09, 3.62, .76),
             (sx + sign * .10, 3.15, .80), (x - sign * .20, 2.9, .61)], .009)
        bay(f'MLG {suffix} bay', [(sign * 1.89, 2.18, 2.27), (sign * 2.95, 2.18, 2.27),
             (sign * 2.95, 4.76, 2.27), (sign * 1.89, 4.76, 2.27)])
        # Open long outboard doors: angular outer skin and visible inner stiffeners.
        door = [(sign * 2.96, 2.14, 2.24), (sign * 3.12, 2.33, 2.00),
                (sign * 3.40, 2.47, 1.64), (sign * 3.40, 4.56, 1.64),
                (sign * 3.31, 4.76, 1.78), (sign * 2.96, 4.79, 2.24)]
        panel(f'MLG {suffix} • open outboard door', door, paint, .035)
        for y in (2.63, 3.32, 4.06, 4.52):
            rod(f'MLG {suffix} • door inner rib', (sign * 2.98, y, 2.22), (sign * 3.35, y, 1.70), .018, enamel, 16)
        for y in (2.45, 4.46):
            rod(f'MLG {suffix} • door hinge', (sign * 2.95, y - .095, 2.22), (sign * 2.95, y + .095, 2.22), .033, titanium)
        rod(f'MLG {suffix} • door actuator', (sign * 2.67, 3.94, 2.22), (sign * 3.25, 3.94, 1.89), .022, metal)
        # Compact rectangular mount lugs stay within the shadowed opening.
        for y in (3.35, 3.72):
            rod(f'MLG {suffix} • upper mounting pin', (sign * 1.97, y, 2.20), (sign * 2.38, y, 2.20), .063, enamel)

    for sign in (-1, 1):
        wheel('NLG ' + ('L' if sign < 0 else 'R'), (sign * .24, -7.2, .35), .34, .19, sign)
    rod('NLG • transverse axle', (-.40, -7.2, .35), (.40, -7.2, .35), .052, titanium)
    rod('NLG • outer shock strut', (0, -6.98, 1.18), (0, -6.96, 2.40), .087, enamel, 48)
    rod('NLG • polished oleo', (0, -7.07, .65), (0, -6.99, 1.30), .056, metal, 48)
    rod('NLG • seal collar', (0, -6.99, 1.17), (0, -6.99, 1.28), .103, enamel, 48)
    rod('NLG • lower fork bridge', (-.145, -7.10, .66), (.145, -7.10, .66), .067, enamel)
    for sign in (-1, 1):
        rod('NLG • fork cheek', (sign * .125, -7.10, .71), (sign * .135, -7.20, .36), .042, enamel)
        rod('NLG • rear drag stay', (sign * .20, -6.11, 2.37), (sign * .09, -7.00, 1.15), .035, enamel)
        rod('NLG • torque upper link', (sign * .057, -6.90, 1.47), (sign * .057, -6.76, 1.17), .024, enamel, 20)
        rod('NLG • torque lower link', (sign * .057, -6.76, 1.17), (sign * .057, -6.96, .91), .024, enamel, 20)
    rod('NLG • torque central pin', (-.085, -6.76, 1.17), (.085, -6.76, 1.17), .027, metal)
    rod('NLG • steering sleeve', (0, -6.98, 1.71), (0, -6.98, 1.88), .112, enamel, 40)
    rod('NLG • steering actuator', (-.19, -7.01, 1.77), (.19, -7.01, 1.77), .032, metal)
    hose('NLG • flexible hydraulic loop', [(.09, -6.95, 2.29), (.13, -6.93, 1.65),
         (.17, -6.95, 1.20), (.14, -7.14, .89), (.08, -7.16, .63)], .008)
    bay('NLG bay', [(-.46, -7.80, 2.41), (.46, -7.80, 2.41),
                    (.46, -6.20, 2.41), (-.46, -6.20, 2.41)])
    for sign in (-1, 1):
        coords = [(sign * .46, -7.78, 2.39), (sign * .62, -7.62, 1.95),
                  (sign * .62, -6.32, 1.95), (sign * .46, -6.20, 2.39)]
        panel('NLG • open side door ' + str(sign), coords, paint, .025)
        for y in (-7.46, -6.57):
            rod('NLG • door stiffener', (sign * .47, y, 2.35), (sign * .60, y, 2.00), .013, enamel, 16)
        rod('NLG • door hinge', (sign * .46, -7.55, 2.38), (sign * .46, -6.42, 2.38), .018, titanium)
    return created
