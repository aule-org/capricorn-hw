"""
laminar.py — lamina cada pieza de capri-dock v2 con ElegooSlicer desde la línea de comandos, para la Elegoo Centauri
Carbon con boquilla de 0.4 y PETG, y deja un gcode por cama con su tiempo y sus gramos.

Uso:  python3 -I laminar.py [carpeta de los STL] [carpeta de salida]
      por omisión: esta carpeta y "~/Documents/Aule - impresión" (los gcode no van a git)

Receta: los perfiles del sistema se aplanan (sin `inherits`, con `from: system` y sus `compatible_printers`) y se les
cambia solo lo de abajo. PETG a 250 °C, cama a 70 °C y ventilador de pieza con tope en 25 %: así salió mejor el cubo de
prueba del dueño que con los 240 °C del perfil. Capa de 0.2, 3 perímetros, 20 % de giroide.
  - C-cuello: 5 perímetros (es la pieza que carga las bisagras);
  - A-base: soporte normal solo desde la cama, para el piso del bolsillo del cuello (ver printcheck.py);
  - N-placa-nombre: pausa (M600) al empezar las letras, para cambiar de blanco a negro.
"""
import sys, json, glob, re, shutil, subprocess, tempfile
from pathlib import Path

APP = "/Applications/ElegooSlicer.app/Contents/MacOS/ElegooSlicer"
PROFILES = "/Applications/ElegooSlicer.app/Contents/Resources/profiles/Elegoo"
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
DST = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.home() / "Documents" / "Aule - impresión"
BED = "Textured PEI Plate"

idx = {}
for f in glob.glob(PROFILES + "/**/*.json", recursive=True):
    try:
        j = json.load(open(f))
    except Exception:
        continue
    if isinstance(j, dict) and "name" in j:
        idx.setdefault((j.get("type"), j["name"]), j)
def flat(kind, name):
    j = idx[(kind, name)]
    out = flat(kind, j["inherits"]) if j.get("inherits") else {}
    out.update(j); out.pop("inherits", None); out["from"] = "system"
    return out

FILAMENT = dict(nozzle_temperature=["250"], nozzle_temperature_initial_layer=["250"], textured_plate_temp=["70"],
                textured_plate_temp_initial_layer=["70"], hot_plate_temp=["70"], hot_plate_temp_initial_layer=["70"],
                fan_max_speed=["25"], fan_min_speed=["10"], overhang_fan_speed=["25"])
PROCESS = dict(layer_height="0.2", wall_loops="3", sparse_infill_density="20%", sparse_infill_pattern="gyroid", curr_bed_type=BED)
# Soporte solo desde la cama y solo bajo techos casi planos (10°): lo único que cumple las dos cosas es el piso del bolsillo.
# bridge_no_support va en 0: con 1 el laminador toma ese piso de 62 mm por un puente y no lo apoya.
SUPPORT = dict(enable_support="1", support_type="normal(auto)", support_on_build_plate_only="1", support_threshold_angle="10",
               bridge_no_support="0")
# cama, archivo, pieza, color, cambios al proceso, pausa en z
PLATES = [
    ("1", "A-base", "negro", SUPPORT, None),
    ("2", "B-fondo", "negro", {}, None),
    ("3", "C-cuello", "negro", dict(wall_loops="5"), None),
    ("4", "E-marco", "color del marco", {}, None),
    ("5", "F-tapa-marco", "color del marco", {}, None),
    ("6", "H-tecla-hablar", "blanco", {}, None),
    ("7", "N-placa-nombre", "blanco, y negro desde la pausa", {}, 1.2),
    # Alternativas para armar SIN lente: reemplazan a las camas 4 y 5 (no se suman al total)
    ("4-ALT", "sin-lente/E-marco", "color del marco", {}, None),
    ("5-ALT", "sin-lente/F-tapa-marco", "color del marco", {}, None),
]

def secs(t):
    return sum(int(v) * m for v, m in zip(re.findall(r"(\d+)([dhms])", t) and [x[0] for x in re.findall(r"(\d+)([dhms])", t)],
                                          [{"d": 86400, "h": 3600, "m": 60, "s": 1}[x[1]] for x in re.findall(r"(\d+)([dhms])", t)]))

DST.mkdir(parents=True, exist_ok=True)
for old in list(DST.glob("*.gcode")) + list(DST.glob("laminado.json")):   # no dejar gcodes de una versión anterior
    old.unlink()
rows = []
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    json.dump({**flat("machine", "Elegoo Centauri Carbon 0.4 nozzle"), "curr_bed_type": BED}, open(tmp / "machine.json", "w"), indent=1)
    json.dump({**flat("filament", "Elegoo PETG PRO @ECC"), **FILAMENT}, open(tmp / "filament.json", "w"), indent=1)
    for n, part, color, extra, pause_z in PLATES:
        json.dump({**flat("process", "0.20mm Standard @Elegoo CC 0.4 nozzle"), **PROCESS, **extra}, open(tmp / "process.json", "w"), indent=1)
        alt = part.startswith("sin-lente/")
        out = tmp / part.replace("/", "-"); out.mkdir()
        log = subprocess.run([APP, "--debug", "1", "--load-settings", f"{tmp / 'machine.json'};{tmp / 'process.json'}",
                              "--load-filaments", str(tmp / "filament.json"), "--arrange", "1", "--slice", "0",
                              "--outputdir", str(out), str(SRC / f"{part}.stl")], capture_output=True, text=True)
        g = out / "plate_1.gcode"
        if not g.exists():
            sys.exit(f"{part}: ElegooSlicer no dejó gcode\n{log.stdout[-1500:]}\n{log.stderr[-1500:]}")
        text = g.read_text()
        note = ""
        if pause_z is not None:                           # pausa al empezar la primera capa por encima de pause_z
            zs = [(m.start(), float(m.group(1))) for m in re.finditer(r"^;Z:([\d.]+)$", text, re.M)]
            pos, z = next((p, z) for p, z in zs if z > pause_z + 0.01)
            text = text[:pos] + "M600 ; pausa: cambiar a filamento negro para las letras\n" + text[pos:]
            note = f"pausa M600 al empezar la capa de z = {z:.1f} mm"
        t = re.search(r"estimated printing time \(normal mode\) = (.+)", text).group(1).strip()
        grams = float(re.search(r"total filament used \[g\] = ([\d.]+)", text).group(1))
        nt = re.findall(r"^; nozzle_temperature = (\d+)", text, re.M)
        bt = re.findall(r"^; textured_plate_temp = (\d+)", text, re.M)
        body = text[:text.find("\nM106 S255 ;Cooling nozzle")]      # el gcode de fin pone el ventilador al 100 % para enfriar la boquilla
        fan = [int(float(v)) for v in re.findall(r"^M106 S([\d.]+)", body, re.M)]
        sup = len(re.findall(r"^;TYPE:Support", text, re.M))
        # dónde quedó el soporte, respecto de la esquina de la pieza
        box_ = {}
        kind = None
        for ln in body.split("\n"):
            if ln.startswith(";TYPE:"):
                kind = "s" if ln.startswith(";TYPE:Support") else "m" if "wall" in ln else None
            elif kind and ln.startswith("G1 X") and " E" in ln:
                m_ = re.match(r"G1 X([\d.]+) Y([\d.]+)", ln)
                if m_:
                    b_ = box_.setdefault(kind, [1e9, 1e9, -1e9, -1e9])
                    x_, y_ = float(m_.group(1)), float(m_.group(2))
                    b_[0], b_[1], b_[2], b_[3] = min(b_[0], x_), min(b_[1], y_), max(b_[2], x_), max(b_[3], y_)
        if "s" in box_:
            s_, m_ = box_["s"], box_["m"]
            note = f"soporte solo en x {s_[0] - m_[0]:.0f}..{s_[2] - m_[0]:.0f}, y {s_[1] - m_[1]:.0f}..{s_[3] - m_[1]:.0f} mm de la pieza"
        name = f"{n}-{part.split('/')[-1]}{'-SIN-LENTE' if alt else ''}-PETG-0.2mm.gcode"
        (DST / name).write_text(text)
        rows.append(dict(cama=n, alternativa=alt, archivo=name, pieza=part, color=color, tiempo=t, segundos=secs(t), gramos=grams, nota=note,
                         boquilla=nt[0] if nt else "?", camaT=bt[0] if bt else "?", fan_max=round(max(fan) / 255 * 100) if fan else 0,
                         soporte=sup, perimetros=extra.get("wall_loops", PROCESS["wall_loops"])))
        print(f"{name}: {t}, {grams:.1f} g, boquilla {rows[-1]['boquilla']} °C, cama {rows[-1]['camaT']} °C, "
              f"ventilador de pieza hasta {rows[-1]['fan_max']} %, tramos de soporte {sup} {note}")
main = [r for r in rows if not r["alternativa"]]
tot = sum(r["segundos"] for r in main)
print(f"total (camas 1 a 7, con lente): {tot // 3600} h {tot % 3600 // 60} min, {sum(r['gramos'] for r in main):.1f} g")
(DST / "laminado.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
