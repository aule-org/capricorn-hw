"""
render.py — imágenes de capri-dock v2 a partir de la escena que deja `dock.py --escena=DIR`.

Uso:  uv run --python 3.12 --with pyvista python -I render.py DIR [carpeta de salida]
Escribe view.png (armada, abierta), exploded.png y controls.png (la tapa de la base de cerca, entera y cortada
bajo la tapa para ver el collar de la tecla, SW1, las palancas y los LEDs).
"""
import sys, json
from pathlib import Path
import pyvista as pv

pv.OFF_SCREEN = True
ESC = Path(sys.argv[1])
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent
man = json.loads((ESC / "escena.json").read_text())
H = man["H"]
fy, fz = man["frente"]                                 # hacia dónde mira la pantalla, en (y, z)
meshes = {n: pv.read(ESC / f"{n}.stl") for n in man["nodos"]}

def add(pl, name, offset=(0, 0, 0), mesh=None, **kw):
    m = (mesh if mesh is not None else meshes[name]).translate(offset, inplace=False)
    node = man["nodos"][name]
    opts = dict(color=node["color"], smooth_shading=True, split_sharp_edges=True, feature_angle=35, specular=0.15, ambient=0.25)
    if name == "lente":
        opts.update(opacity=0.35)
    opts.update(kw)
    pl.add_mesh(m, **opts)

def plotter(size):
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background("white")
    pl.enable_anti_aliasing("ssaa")
    return pl

# 1. Armada, abierta
pl = plotter((1500, 1300))
for n in meshes:
    add(pl, n)
pl.camera_position = [(430, -420, 330), (100, 70, 95), (0, 0, 1)]
pl.screenshot(OUT / "view.png")

# 2. Explosionada, de frente y de atrás: la base se abre en vertical y el marco a lo largo de su eje
VERT = {"base": 75, "tecla": 125, "placa": 22, "interior": 0, "fondo": -60, "patas": -85, "nombre": 0, "cuello": 75}
FRAME = {"marco": 120, "lente": 80, "panel": 45, "electronica-marco": -5, "tapa-marco": -75}
pl = pv.Plotter(off_screen=True, window_size=(2600, 1700), shape=(1, 2))
pl.set_background("white"); pl.enable_anti_aliasing("ssaa")
for col, cam in ((0, [(760, -700, 520), (100, 50, 130), (0, 0, 1)]), (1, [(-500, 800, 480), (100, 60, 130), (0, 0, 1)])):
    pl.subplot(0, col)
    for n, node in man["nodos"].items():
        g = node["grupo"]
        if g in FRAME:
            off = (0, fy * FRAME[g], fz * FRAME[g] + 115)
        elif g == "nombre":
            off = (0, -40, 75)
        else:
            off = (0, 0, VERT[g])
        add(pl, n, off)
    pl.add_text("de frente: marco E, lente, panel, driver y adaptador, tapa F; tecla H, base A, placa, interior, fondo B" if col == 0 else
                "de atrás: el haz de 14 hilos sube por el cuello y se abre hacia el driver (azul) y el adaptador del táctil (magenta)", font_size=11, color="black")
    pl.camera_position = cam
pl.screenshot(OUT / "exploded.png")

# 3. Controles: la esquina derecha de la tapa, entera y cortada 2.6 mm bajo la cara de arriba
tx, ty = man["tecla"]
pl = pv.Plotter(off_screen=True, window_size=(2200, 1100), shape=(1, 2))
pl.set_background("white"); pl.enable_anti_aliasing("ssaa")
for col, cut in ((0, False), (1, True)):
    pl.subplot(0, col)
    for n in ("A", "H", "placa", "palancas", "N", "letras"):
        m = meshes[n]
        if cut and n == "A":
            m = m.clip(normal="z", origin=(0, 0, H - 2.6), invert=True)
        add(pl, n, mesh=m)
    pl.add_text("tapa entera: tecla ● sobre SW1, ranura de SW2 (encendido), ranura de SW6 (silencio) y ventana de D8" if not cut else
                "cortada bajo la tapa: collar y orejas de la tecla, pies, palancas, tubos de luz y de micrófono", font_size=10, color="black")
    pl.camera_position = [(tx + 60, -75, H + 170), (tx - 16, 62, H - 4), (0, 0, 1)]
pl.screenshot(OUT / "controls.png")
print("view.png, exploded.png, controls.png")
