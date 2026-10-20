"""Editable cinematic exhaust study; appearance is artistic, not measured hardware data."""

import math

import bpy


def _volume_material(name, color, strength, density, noisy=True):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    volume = nodes.new('ShaderNodeVolumePrincipled')
    volume.inputs['Color'].default_value = (*color, 1)
    volume.inputs['Anisotropy'].default_value = .12
    links.new(volume.outputs['Volume'], out.inputs['Volume'])
    coord = nodes.new('ShaderNodeTexCoord')
    separate = nodes.new('ShaderNodeSeparateXYZ')
    links.new(coord.outputs['Generated'], separate.inputs['Vector'])

    def math_node(operation, first, second=None):
        node = nodes.new('ShaderNodeMath')
        node.operation = operation
        for index, value in enumerate((first, second)):
            if value is None:
                continue
            if isinstance(value, (int, float)):
                node.inputs[index].default_value = value
            else:
                links.new(value, node.inputs[index])
        return node.outputs[0]

    x = math_node('MULTIPLY', math_node('SUBTRACT', separate.outputs['X'], .5), 2)
    z = math_node('MULTIPLY', math_node('SUBTRACT', separate.outputs['Z'], .5), 2)
    radius = math_node('SQRT', math_node('ADD', math_node('MULTIPLY', x, x), math_node('MULTIPLY', z, z)))
    radial = math_node('POWER', math_node('MAXIMUM', math_node('SUBTRACT', 1, radius), 0), 1.15)
    axial = math_node('POWER', math_node('MAXIMUM', math_node('SUBTRACT', 1, separate.outputs['Y']), 0), .65)
    envelope = math_node('MULTIPLY', radial, axial)
    if noisy:
        stretch = nodes.new('ShaderNodeVectorMath')
        stretch.operation = 'MULTIPLY'
        stretch.inputs[1].default_value = (2.0, 7.0, 2.0)
        links.new(coord.outputs['Generated'], stretch.inputs[0])
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 5.7
        noise.inputs['Detail'].default_value = 2
        noise.inputs['Roughness'].default_value = .67
        links.new(stretch.outputs['Vector'], noise.inputs['Vector'])
        breakup = math_node('ADD', math_node('MULTIPLY', noise.outputs['Fac'], .8), .22)
        envelope = math_node('MULTIPLY', envelope, breakup)
    links.new(math_node('MULTIPLY', envelope, density), volume.inputs['Density'])
    links.new(math_node('MULTIPLY', envelope, strength), volume.inputs['Emission Strength'])
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .1
    ramp.color_ramp.elements[0].color = (*color, 1)
    ramp.color_ramp.elements[1].position = 1
    ramp.color_ramp.elements[1].color = (1.0, .20, .04, 1)
    links.new(radial, ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], volume.inputs['Emission Color'])
    mat.diffuse_color = (*color, .2)
    return mat


def _ring_material():
    mat = bpy.data.materials.new('FX | faint orange compression rims')
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    emission = nodes.new('ShaderNodeEmission')
    emission.inputs['Color'].default_value = (1, .18, .025, 1)
    emission.inputs['Strength'].default_value = 4
    transparent = nodes.new('ShaderNodeBsdfTransparent')
    mix = nodes.new('ShaderNodeMixShader')
    mix.inputs[0].default_value = .16
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(emission.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs['Surface'])
    return mat


def build_exhaust_fx(env):
    """Build three switchable plumes; optional exhaust_centers overrides exit geometry.

    Each override is (x, y, z, width, height, length), in aircraft coordinates.
    No renderer, compositor, camera, save path or other collections are changed.
    """
    coll = env['collection']('07 • Exhaust effects')
    coll['description'] = 'Red-orange cinematic exhaust with shock-cell motifs; optional visual effect.'
    coll['accuracy'] = 'Illustration only. Plume state, color and shock pattern are not verified prototype observations.'
    root = env['aircraft_root']
    make_mesh, make_curve = env['mesh'], env['curve']
    outer = _volume_material('FX | transparent turbulent vermilion gas', (1, .025, .004), 4.6, .018)
    hot = _volume_material('FX | soft incandescent shock cells', (1, .065, .009), 6.5, .008, False)
    throat = _volume_material('FX | recessed orange exit glow', (1, .08, .008), 20, .012, False)
    rims = _ring_material()
    centers = env.get('exhaust_centers')
    if centers is None:
        centers = [(x, env['trailing'](x) + .025, 2.64, 1.10, .33, 4.2 if x else 4.5)
                   for x in (-1.95, 0, 1.95)]

    def volume_shape(name, center, length, width, height, radii, mat, irregular=False):
        x0, y0, z0 = center
        verts, faces = [], []
        segments = 32
        for j, (t, r) in enumerate(radii):
            exponent = .52 + .4 * t if irregular else 1
            for k in range(segments):
                a = math.tau * k / segments
                c, s = math.cos(a), math.sin(a)
                wobble = 1 + (.035 * math.sin(k * 2.3 + j * 1.1) * t if irregular else 0)
                xx = math.copysign(abs(c) ** exponent, c) * width * .5 * r * wobble
                zz = math.copysign(abs(s) ** exponent, s) * height * .5 * r * wobble
                verts.append((x0 + xx, y0 + length * t, z0 + zz - .025 * t))
        for j in range(len(radii) - 1):
            for k in range(segments):
                a = j * segments + k
                b = j * segments + (k + 1) % segments
                faces.append((a, a + segments, b + segments, b))
        faces.append(tuple(range(segments)))
        faces.append(tuple((len(radii) - 1) * segments + k for k in reversed(range(segments))))
        ob = make_mesh(name, verts, faces, mat, True)
        ob.parent = root
        ob.visible_shadow = False
        return ob

    for engine, (x, y, z, width, height, length) in enumerate(centers, 1):
        volume_shape('FX %d | transparent red-orange turbulent plume' % engine,
                     (x, y, z), length, width, height,
                     [(j / 24, max(.008, (1 - j / 24) ** .42) * (1 + .055 * math.sin(j * 1.9))) for j in range(25)],
                     outer, True)
        volume_shape('FX %d | hot nozzle exit volume' % engine,
                     (x, y - .075, z), .28, width * .79, height * .79,
                     [(0, .88), (.25, 1), (.65, .8), (1, .02)], throat)
        for cell in range(5):
            offset = .2 + .68 * cell
            fade = 1 - cell * .095
            volume_shape('FX %d | soft shock diamond %02d' % (engine, cell + 1),
                         (x, y + offset, z), .62 + cell * .025,
                         width * .56 * fade, height * .67 * fade,
                         [(j / 16, max(.015, math.sin(math.pi * j / 16) ** 1.2)) for j in range(17)], hot)
            if cell < 4:
                rim_y = y + offset + .30
                rim = [(x + width * .27 * fade * math.cos(math.tau * k / 64),
                        rim_y + .009 * math.cos(math.tau * k / 16),
                        z + height * .31 * fade * math.sin(math.tau * k / 64) - .01)
                       for k in range(64)]
                ob = make_curve('FX %d | faint compression ring %02d' % (engine, cell + 1),
                                rim, .0035, rims, True)
                ob.parent = root
                ob.visible_shadow = False
        light = bpy.data.lights.new('FX %d | local warm exhaust bounce' % engine, 'POINT')
        light.energy = 38
        light.color = (1, .085, .012)
        light.shadow_soft_size = .32
        ob = bpy.data.objects.new(light.name, light)
        coll.objects.link(ob)
        ob.location = (x, y + .12, z + .08)
        ob.parent = root
    return coll
