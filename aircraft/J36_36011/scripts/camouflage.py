"""Editable three-tone planform coating, hand traced from the supplied drawing.

The trace deliberately excludes photographed reflections and printed markings.
Coordinates below refer to the reference image, not engineering measurements.
"""
import bpy
import numpy as np


def apply_camouflage(materials):
    size = 4096
    # Linear-light colours. Broad polygon areas stay free of baked lighting.
    palette = np.array([
        [0.045, 0.058, 0.075, 1.0],
        [0.110, 0.135, 0.160, 1.0],
        [0.250, 0.280, 0.320, 1.0],
    ], dtype=np.float32)
    u, v = np.meshgrid((np.arange(size) + 0.5) / size,
                       (np.arange(size) + 0.5) / size)
    # Source nose (101, 248), tail x=574; span projects vertically in source.
    px = 101.0 + v * 473.0
    py = 248.0 - (u * 2.0 - 1.0) * 211.0
    indices = np.ones((size, size), dtype=np.uint8)
    polygons = [
        # Upper half of the supplied plan view, from root to outer panel.
        (0, [(182,216),(213,204),(246,224),(268,225),(245,243),(206,237)]),
        (2, [(238,214),(267,201),(291,193),(308,178),(349,163),
             (327,192),(304,210),(271,249),(259,239)]),
        (0, [(271,181),(305,166),(332,148),(365,124),(398,103),
             (397,127),(355,155),(313,174),(288,188)]),
        (0, [(304,223),(325,196),(351,184),(365,178),(383,191),
             (364,220),(358,246),(328,247)]),
        (2, [(400,103),(418,151),(406,198),(452,174),(459,134),
             (488,131),(499,173),(545,180),(557,204),(497,200),
             (474,187),(448,203),(420,224),(434,245),(397,254),
             (359,226),(379,195),(389,173),(379,152)]),
        (0, [(402,99),(462,59),(464,95),(496,110),(463,110),
             (443,116),(418,108)]),
        (0, [(469,61),(494,37),(502,61),(478,74)]),
        (2, [(502,64),(512,88),(484,83),(477,72)]),
        (0, [(514,114),(529,140),(544,143),(552,167),(510,161),
             (504,135),(494,127),(497,111)]),
        (0, [(453,201),(479,201),(491,212),(552,215),(570,221),
             (558,240),(518,239),(495,226),(471,226)]),
        # Nose and raised central body remain broken up without a glare stripe.
        (0, [(105,248),(148,231),(174,226),(158,248),(179,265),
             (149,266)]),
        (2, [(212,240),(246,242),(267,255),(304,252),(309,267),
             (279,278),(260,270),(224,267)]),
        (0, [(274,231),(302,231),(307,256),(344,258),(344,268),
             (309,265),(298,249),(274,249)]),
        (0, [(363,245),(391,255),(424,251),(440,268),(412,277),
             (386,266),(364,269),(348,257)]),
        (2, [(455,198),(478,211),(518,219),(495,238),(520,256),
             (495,276),(461,273),(434,257),(429,242),(416,225)]),
        # Lower half has a distinct, intentionally asymmetric polygon layout.
        (0, [(188,273),(215,278),(239,294),(264,300),(272,319),
             (247,306),(215,292)]),
        (2, [(242,273),(264,277),(281,294),(280,323),(310,335),
             (338,333),(359,314),(373,300),(402,296),(421,284),
             (440,305),(408,323),(379,338),(338,353),(307,340),
             (276,326),(266,301)]),
        (0, [(308,270),(344,262),(367,272),(391,274),(417,293),
             (399,314),(378,314),(354,338),(336,333),(344,312),
             (335,291),(317,288)]),
        (0, [(421,309),(445,307),(468,323),(448,345),(425,353),
             (410,375),(387,366),(362,349),(383,335)]),
        (2, [(447,349),(472,344),(506,376),(491,404),(488,434),
             (467,423),(445,402),(434,383)]),
        (0, [(455,282),(480,284),(497,297),(525,325),(548,313),
             (538,348),(522,374),(500,360),(483,338),(460,324)]),
        (0, [(490,416),(509,402),(514,413),(495,458),(474,441)]),
        (2, [(526,280),(565,278),(553,307),(531,307),(514,294)]),
        (0, [(518,248),(552,245),(569,254),(573,275),(543,277),
             (528,266)]),
    ]

    for colour, points in polygons:
        inside = np.zeros((size, size), dtype=bool)
        for i, (x0, y0) in enumerate(points):
            x1, y1 = points[(i + 1) % len(points)]
            if y1 == y0:
                continue
            inside ^= ((y0 > py) != (y1 > py)) & (
                px < (x1 - x0) * (py - y0) / (y1 - y0) + x0)
        indices[inside] = colour

    name = 'Reference-derived camouflage • editable palette'
    image = bpy.data.images.new(name, width=size, height=size, alpha=True)
    image.colorspace_settings.name = 'Non-Color'
    image.pixels.foreach_set(palette[indices].ravel())
    image.update()
    image.pack()
    image['source'] = 'references/User_Three_View.png; broad polygons hand traced'
    image['accuracy'] = 'Reference interpretation; not an official paint pattern'
    image['linear_palette'] = str(palette[:, :3].tolist())

    for material in materials:
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
        position = nodes.new('ShaderNodeNewGeometry')
        position.label = 'Planar world coordinates / upper-surface mask'
        position.location = (-860, 20)
        separate = nodes.new('ShaderNodeSeparateXYZ')
        separate.location = (-660, 130)
        links.new(position.outputs['Position'], separate.inputs[0])
        scale_x = nodes.new('ShaderNodeMath')
        scale_x.operation = 'MULTIPLY_ADD'
        scale_x.inputs[1].default_value = 1.0 / 21.2
        scale_x.inputs[2].default_value = 0.5
        scale_x.location = (-465, 220)
        links.new(separate.outputs['X'], scale_x.inputs[0])
        scale_y = nodes.new('ShaderNodeMath')
        scale_y.operation = 'MULTIPLY_ADD'
        scale_y.inputs[1].default_value = 1.0 / 22.65
        scale_y.inputs[2].default_value = 12.0 / 22.65
        scale_y.location = (-465, 70)
        links.new(separate.outputs['Y'], scale_y.inputs[0])
        uv = nodes.new('ShaderNodeCombineXYZ')
        uv.location = (-260, 220)
        links.new(scale_x.outputs[0], uv.inputs['X'])
        links.new(scale_y.outputs[0], uv.inputs['Y'])
        texture = nodes.new('ShaderNodeTexImage')
        texture.image = image
        texture.interpolation = 'Cubic'
        texture.extension = 'EXTEND'
        texture.label = 'Hand-traced cool-grey disruptive camouflage'
        texture.location = (-55, 190)
        links.new(uv.outputs[0], texture.inputs['Vector'])
        normal = nodes.new('ShaderNodeSeparateXYZ')
        normal.location = (-660, -170)
        links.new(position.outputs['Normal'], normal.inputs[0])
        upper = nodes.new('ShaderNodeMapRange')
        upper.clamp = True
        upper.inputs['From Min'].default_value = 0.08
        upper.inputs['From Max'].default_value = 0.42
        upper.location = (-445, -185)
        links.new(normal.outputs['Z'], upper.inputs['Value'])
        mix = nodes.new('ShaderNodeMixRGB')
        mix.blend_type = 'MIX'
        mix.inputs[1].default_value = (0.035, 0.045, 0.056, 1)
        mix.label = 'Charcoal underside / patterned upper skin'
        mix.location = (205, 125)
        links.new(upper.outputs[0], mix.inputs[0])
        links.new(texture.outputs['Color'], mix.inputs[2])
        links.new(mix.outputs[0], bsdf.inputs['Base Color'])
        bsdf.location = (440, 90)
    return image
