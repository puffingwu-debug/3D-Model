"""Photo-guided exterior detail for the first-prototype J-36 underside."""

import math


def build_ventral_detail(env):
    collection = env['collection']
    mesh = env['mesh']
    curve = env['curve']
    path_surface = env['path_surface']
    patch = env['patch']
    bottom = env['bottom']
    trailing = env['trailing']
    mats = env['materials']
    paint, edge, dark = mats['paint'], mats['edge'], mats['dark']

    coll = collection('08 • Ventral exterior refinements')
    coll['basis'] = 'Visible exterior cues in user underside photographs; dimensions are interpretation.'

    # The broad belly stays sealed. The perimeter alone suggests the closed doors.
    bay = [(.075, -3.68), (.62, -3.47), (.81, -3.25), (1.09, -3.10),
           (1.37, -2.75), (1.43, 4.48), (1.20, 4.71), (1.00, 4.56),
           (.78, 4.77), (.57, 4.63), (.34, 4.83), (.075, 4.69)]
    for s, side in ((-1, 'Port'), (1, 'Starboard')):
        xy = [(s*x, y) for x, y in bay]
        path_surface(side+' • sealed central bay sawtooth perimeter', xy, dark,
                     r=.0032, lower=True, closed=True, offset=.004)

        # Longitudinal chine/keel transitions are shallow, not protruding fins.
        vs, fs = [], []
        steps = 96
        for j in range(steps+1):
            u = j/steps
            y = -2.60+8.90*u
            x0 = s*(1.50+.075*math.sin(math.pi*u))
            taper = math.sin(math.pi*u)**.45
            for dx, dz in ((-.052, -.002), (-.018, -.028), (.018, -.028), (.052, -.002)):
                x = x0+s*dx*taper
                vs.append((x, y, bottom(x, y)+dz*taper-.002))
        for j in range(steps):
            for k in range(3):
                a = j*4+k
                face = (a, a+1, a+5, a+4)
                fs.append(tuple(reversed(face)) if s>0 else face)
        rail = mesh(side+' • shallow ventral keel shoulder', vs, fs, paint, True)
        rail['exterior_only'] = True

        # Three modest fairings per wing are visible ahead of the trailing edge.
        # Each is a rounded tapered shell with its mounting perimeter buried in skin.
        for number, (xc, length, width, height) in enumerate(
                ((4.40, 1.36, .155, .175),
                 (5.65, 1.23, .145, .160),
                 (6.90, 1.09, .132, .145)), 1):
            center = s*xc
            rear = trailing(center)-.62
            front = rear-length
            vs, fs = [], []
            nu, nv = 36, 28
            vs.append((center, front, bottom(center, front)+.005))
            for j in range(1, nu):
                u = j/nu
                y = front+length*u
                # Fuller nose, a narrow aft tip, and no razor-edged vertical plate.
                taper = math.sin(math.pi*u)**.74*(1.12-.36*u)
                w = width*taper
                h = height*math.sin(math.pi*u)**.9*(1.16-.40*u)
                for k in range(nv):
                    angle = 2*math.pi*k/nv
                    x = center+w*math.cos(angle)
                    z = bottom(x, y)-h*(.34+.66*math.sin(angle))
                    vs.append((x, y, z))
            aft = len(vs)
            vs.append((center, rear, bottom(center, rear)+.005))
            for k in range(nv):
                fs.append((0, 1+(k+1)%nv, 1+k))
            for j in range(nu-2):
                for k in range(nv):
                    a = 1+j*nv+k
                    b = 1+j*nv+(k+1)%nv
                    fs.append((a, b, b+nv, a+nv))
            last = 1+(nu-2)*nv
            for k in range(nv):
                fs.append((last+k, last+(k+1)%nv, aft))
            fairing = mesh(side+' • lower control actuator fairing %02d'%number,
                           vs, fs, paint, True)
            fairing['basis'] = 'Small streamlined underside bulge visible in supplied photographs.'
            # Restrained service split at the shoulder; only the outer lower shell is visible.
            seam = []
            for j in range(1, 35):
                u = j/36
                y = front+length*u
                taper = math.sin(math.pi*u)**.74*(1.12-.36*u)
                x = center+s*width*taper*.72
                h = height*math.sin(math.pi*u)**.9*(1.16-.40*u)
                seam.append((x, y, bottom(x, y)-h*(.34+.66*math.sqrt(1-.72**2))-.002))
            curve(side+' • fairing %02d shell split'%number, seam, .0015, edge)

        # Fine lower trailing shell edge follows the existing planform.
        xs = [3.37+(8.12-3.37)*i/72 for i in range(73)]
        strip = [(s*x, trailing(x)-.052) for x in xs]
        strip += [(s*x, trailing(x)-.148) for x in reversed(xs)]
        patch(side+' • lower trailing edge laminate lip', strip, edge,
              lower=True, offset=.006)
        path_surface(side+' • lower trailing edge seal',
                     [(s*x, trailing(x)-.046) for x in xs], dark,
                     r=.003, lower=True, closed=False, offset=.006)

        # A few flush access hatches visible as quiet tonal outlines, away from wheel bays.
        for idx, y in enumerate((-.85, .88, 5.72)):
            x = s*3.47
            hatch = [(x-s*.13, y-.21), (x+s*.13, y-.21),
                     (x+s*.16, y+.15), (x-s*.11, y+.20)]
            path_surface(side+' • lower flush service cover %02d'%idx,
                         hatch, edge, r=.0024, lower=True, closed=True, offset=.004)

    return coll
