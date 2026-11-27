"""Short skin highlights and their turning edges, registered on individual cels."""


def joint_highlights(body, strokes, ramp, registered, protected, edits):
    for x, y, dx, dy in strokes:
        # A two-pixel ridge follows the limb instead of cutting across it.
        # The contact shadow sits toward the lower right of the ridge.
        sx, sy = (0, 1) if dy == 0 else (1, 0)
        for xx, yy, step in ((x, y, 3), (x+dx, y+dy, 2),
                             (x+sx, y+sy, -2), (x+dx+sx, y+dy+sy, -2)):
            u, v = registered(xx, yy)
            if (u, v) in protected or not (0 <= v < len(body) and 0 <= u < len(body[v])):
                continue
            raw = edits.get((u, v), body[v][u])
            if raw not in ramp or raw == ramp[0]:
                continue
            rank = ramp.index(raw)
            # Borrow light for the ridge, keeping dark contours intact and
            # leaving the brightest native glints on their own short crests.
            edits[u, v] = ramp[max(1, min(len(ramp)-1, rank+step))]


def quiet_highlights(body, ramp, protected, edits):
    """Soften isolated bright points while leaving adjacent muscle ridges lit."""
    # Read the completed joint and rib accents as a single surface before
    # adjusting anything. Neighbour order must not influence the next cel.
    tones = {(x, y): ramp.index(colour)
             for y, row in enumerate(body) for x, base in enumerate(row)
             if (colour := edits.get((x, y), base)) in ramp}
    for (x, y), rank in tones.items():
        if rank < 8 or (x, y) in protected:
            continue
        adjacent = [tones[p] for p in ((x-1,y), (x+1,y), (x,y-1), (x,y+1)) if p in tones]
        if len(adjacent) >= 3 and max(adjacent) <= rank-3:
            edits[x, y] = ramp[rank-2]


def exposed_skin(rows, edits):
    """Cloth keeps its authored lighting where it occludes the painted skin."""
    body = rows["Body base"]
    for role, outfit in rows.items():
        if role not in ("Original", "Body base"):
            for (u, v), shade in edits.items():
                if outfit[v][u] == body[v][u]:
                    outfit[v][u] = shade
    for (u, v), shade in edits.items():
        body[v][u] = shade
    return rows
