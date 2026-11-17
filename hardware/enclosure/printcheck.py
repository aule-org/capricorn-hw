"""
printcheck.py — control de impresión sin soportes de los STL de capri-dock v2, capa por capa.

Uso:  uv run --python 3.12 --with trimesh --with shapely --with numpy --with scipy --with networkx --with rtree \
          python -I printcheck.py [carpeta de los STL]

Los STL ya vienen en la orientación de impresión (la cama en z = 0). Cada capa de 0.2 mm se compara con la de abajo:
lo que sobresale más de una capa (0.2 mm, o sea 45°) no tiene apoyo. Cada trozo sin apoyo se clasifica:
  - escalón: menos de 0.5 mm de ancho (una línea de boquilla). Es el borde de un redondeo o el techo de un agujero
    redondo. Pasa si no se repite en más de 8 capas seguidas (1.6 mm): más que eso es una pendiente de más de 45°;
  - puente: tiene apoyo a los dos lados. Pasa si mide 20 mm o menos;
  - voladizo: apoyo de un solo lado. No pasa;
  - isla: nace en el aire, sin tocar la capa de abajo. No pasa;
  - zona con soporte: declarada en impresion.json (la escribe dock.py). Se informa y se imprime con soporte.
Sale con error si alguna pieza tiene un voladizo, un puente largo o una pendiente fuera de las zonas declaradas.
"""
import sys, json, math
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Point, LineString, box as sbox
from shapely.ops import unary_union

DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
LAYER, STEP_W, RUN_MAX, BRIDGE_MAX = 0.2, 0.5, 8, 20.0
info = json.loads((DIR / "impresion.json").read_text())

def polys(g):
    if g.is_empty:
        return []
    return [p for p in (g.geoms if hasattr(g, "geoms") else [g]) if p.geom_type == "Polygon"]

def layers_of(mesh):
    zs = np.arange(LAYER / 2, mesh.bounds[1][2], LAYER)
    secs = mesh.section_multiplane([0, 0, 0], [0, 0, 1], zs)
    out = []
    for s in secs:
        out.append(unary_union([p.buffer(0) for p in s.polygons_full]) if s is not None else None)
    return zs, out

def classify(c, sup):
    """(tipo, medida en mm, punto) de un trozo c que no apoya en sup."""
    if c.distance(sup) > 0.05:
        return "isla en el aire", 0.0, c.representative_point()
    if c.buffer(-STEP_W / 2).is_empty:
        return "escalón", 0.0, c.representative_point()
    x0, y0, x1, y1 = c.bounds
    n = max(2, int(max(x1 - x0, y1 - y0) / 0.5) + 1)
    best, far = -1.0, None
    for x in np.linspace(x0, x1, min(n, 400)):
        for y in np.linspace(y0, y1, min(n, 400)):
            p = Point(x, y)
            if c.contains(p):
                d = sup.distance(p)
                if d > best:
                    best, far = d, p
    if far is None:
        far = c.representative_point(); best = sup.distance(far)
    # Ancho del vano: el par de rayos opuestos más corto que toca apoyo a los dos lados
    span = None
    for ang in range(0, 180, 10):
        ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        ds = []
        for s_ in (1, -1):
            hit = LineString([(far.x, far.y), (far.x + s_ * ux * BRIDGE_MAX * 4, far.y + s_ * uy * BRIDGE_MAX * 4)]).intersection(sup)
            ds.append(None if hit.is_empty else far.distance(hit))
        if None not in ds and (span is None or sum(ds) < span):
            span = sum(ds)
    if span is None:
        return "voladizo", best, far
    return "puente", span, far

total_bad = 0
for name, meta in info["piezas"].items():
    mesh = trimesh.load(DIR / f"{name}.stl")
    zones = [(sbox(z[0], z[1], z[2], z[3]), z[4], z[5], z[6]) for z in meta.get("soporte", [])]
    zs, lay = layers_of(mesh)
    prev, runs = None, []
    stats = {"escalón": 0, "puente": 0, "voladizo": 0, "con soporte": 0}
    worst_bridge, worst_run, bad, sup_area = 0.0, 0, [], {}
    for z, cur in zip(zs, lay):
        if cur is None or cur.is_empty:
            prev, runs = None, []
            continue
        if prev is None:
            if z > LAYER:
                bad.append((z, "isla sin apoyo", cur.area, cur.representative_point()))
            prev = cur
            continue
        sup = prev.buffer(LAYER + 0.03)
        new_runs = []
        for c in polys(cur.difference(sup)):
            if c.area < 0.05:
                continue
            kind, m, pt = classify(c, sup)
            zone = next((zn for zn in zones if zn[1] <= z <= zn[2] and zn[0].intersects(c)), None)
            if kind == "escalón":
                run = 1 + max([r for g, r in runs if g.distance(c) < 0.6], default=0)
                new_runs.append((c, run))
                worst_run = max(worst_run, run)
                stats[kind] += 1
                if run == RUN_MAX + 1 and not zone:
                    bad.append((z, f"pendiente de más de 45° por más de {RUN_MAX} capas", c.area, pt))
            elif zone:
                stats["con soporte"] += 1
                sup_area[zone[3]] = sup_area.get(zone[3], 0) + c.area
            elif kind == "puente" and m <= BRIDGE_MAX:
                stats[kind] += 1
                worst_bridge = max(worst_bridge, m)
            else:
                stats["voladizo"] += 1
                bad.append((z, f"{kind} de {m:.1f} mm", c.area, pt))
        prev, runs = cur, new_runs
    sx, sy, sz = mesh.extents
    print(f"{name}: {sx:.0f} x {sy:.0f} x {sz:.1f} mm, {len(zs)} capas; {meta['orientacion']}")
    print(f"   escalones {stats['escalón']} (el más largo, {worst_run} capas); puentes {stats['puente']} (el más largo, {worst_bridge:.1f} mm); "
          f"sin apoyo {len(bad)}")
    for zn, a_ in sup_area.items():
        print(f"   CON SOPORTE: {zn} ({a_:.0f} mm² de techo)")
    for z, what, area, pt in bad[:12]:
        print(f"   FALLA z {z:.1f}: {what}, {area:.1f} mm², en x {pt.x:.1f}, y {pt.y:.1f}")
    if len(bad) > 12:
        print(f"   ... y {len(bad) - 12} más")
    total_bad += len(bad)
print("PASA: todo sale sin soportes fuera de las zonas declaradas" if not total_bad else f"NO PASA: {total_bad} trozos sin apoyo")
sys.exit(1 if total_bad else 0)
