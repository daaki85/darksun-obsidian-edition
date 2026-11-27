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
