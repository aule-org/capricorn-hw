"""
capri-dock v2 — base de escritorio plegable para la placa capri-slate v0.2 táctil (92 x 48 mm) y el panel de tinta
electrónica de 7.5" con táctil capacitivo (Good Display GDEY075T7-T01, 800 x 480, GT911). Paramétrica en build123d.
Misma forma que la v1 (cuello en L, marco con la bisagra escondida), 6 mm más angosta: base y marco de 194 x 138.5; ver ../capri-dock/.

Qué cambia contra la v1:
  - la placa v0.2 no tiene los botones de navegación SW3-SW5: salen el peine G, sus agujeros, postes y empujadores;
  - la tecla ● (H) pasa a apretar SW1, el único pulsador que queda: un émbolo con guía, tope arriba y tope abajo;
  - las ranuras de SW6 (silencio) y SW2 (encendido) se centran en el cuerpo real del interruptor (en la v1 estaban
    centradas en el pad 1 de la huella, a 2.5 mm de la palanca);
  - el panel mide 2.13 mm (táctil) y tiene dos colas: la de 24 pines y la táctil de 6;
  - el táctil baja por los mismos niples y el mismo canal del cuello: 14 hilos en total, hasta un adaptador en J6;
  - todo sale sin soportes en PETG salvo el piso del bolsillo de A; printcheck.py lo controla capa por capa.

Uso:  uv run --python 3.12 --with build123d python -I dock.py [out_dir]
      --board=X.step    otra placa (por omisión ../board/capri-slate-v0.2.2-tactil.step)
      --sin-lente       sin el lente de policarbonato: el panel apoya en el bisel (cambian E y F)
      --colas-derecha   las colas del panel salen del otro extremo del borde (MEDIR en el panel real)
      --nombre=...      otro nombre en la placa N
      --cortes          (con --with matplotlib) sections.png
      --escena=DIR      deja en DIR las piezas armadas, para render.py
      --glb             capri-dock-v2.glb: abierta, una pieza por nodo, para un visor 3D
      --tiempos         cuánto tarda cada sección

Coordenadas: origen en la esquina de adelante, a la izquierda y abajo de la base; x a la derecha, y hacia atrás,
z hacia arriba (sistema derecho). El marco se modela plano en sus propias coordenadas (x desde el centro, y desde su
borde de abajo, z = 0 en la cara del frente y negativo hacia atrás) y pose(t) lo lleva a su lugar: t = 1 abierta,
t = 0 cerrada. La placa va en la base con los componentes hacia arriba y el USB-C hacia la pared derecha:
x = BX0 + ky, y = BY0 + kx (kx, ky = coordenadas KiCad). El control de calce cruza las piezas con el STEP de la placa.

Los STL salen en la orientación de impresión (la cara que va a la cama en z = 0); los STEP, en su lugar.
Los valores marcados MEDIR salen de hojas de datos o son supuestos: confirmarlos con las piezas en la mano.
"""
import sys, math, time
from pathlib import Path
from build123d import *

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
OUT = Path(ARGS[0]) if ARGS else Path(__file__).parent

# ---------- Panel (Good Display GDEY075T7-T01: el GDEY075T7 con táctil capacitivo) ----------
PW, PH, PT = 170.2, 111.2, 2.13       # contorno del panel; 2.13 mm con la capa táctil de PET al frente (sin táctil: 1.18)
AA_W, AA_H = 163.2, 97.92             # área activa
AA_TOP = 3.5                          # MEDIR: borde superior del área activa (el FPC sale por abajo, borde más ancho)
FOAM, FOAM_SQ = 1.5, 0.3              # cinta de espuma detrás del panel; las costillas de F la aprietan FOAM_SQ, no más
LENTE = "--sin-lente" not in sys.argv # EL parámetro del lente: con lente por omisión. PROBAR el táctil a través de él
LENS_T = 1.0 if LENTE else 0.0        # policarbonato antirreflejo de 1 mm delante del panel
GASKET = 0.5                          # junta de espuma entre el bisel (o el lente) y el panel, alrededor del área activa
# Colas del panel. Salen las dos del mismo borde largo (el de arriba, con el panel girado 180°). Según el dibujo de la
# hoja de datos la de 24 pines va centrada a ~47 mm de un extremo y la táctil sale más cerca de ese mismo extremo.
TAIL_END = +1 if "--colas-derecha" in sys.argv else -1   # MEDIR: -1 = extremo izquierdo visto de frente
TAIL_DISP, TAIL_DISP_W = 47.0, 12.5   # MEDIR: centro de la cola de 24 pines desde ese extremo, y su ancho
TAIL_TOUCH, TAIL_TOUCH_W = 20.0, 3.5  # MEDIR: centro de la cola táctil de 6 pines (paso 0.5) desde ese extremo, y su ancho
TAIL_AIR = 4.0                        # aire a cada lado de cada cola en las guías de E y las costillas de F

# ---------- Placa capri-slate v0.2 táctil ----------
BW, BH, BT = 92.0, 48.0, 1.6
KX0 = -26.0                           # borde de adelante de la placa (izquierdo en KiCad)
S = 6.5                               # cara interior de la tapa -> cara de componentes (JST 6 mm, L2 4.5 mm)
BTN_H = 3.8                           # TL3305AF160QG sobre la placa, medido en el STEP de la placa
BTN_TRAVEL = 0.25                     # recorrido del TL3305 (hoja de datos: 0.25 ± 0.1)
SLIDE_BODY, SLIDE_TOP = 3.5, 9.5      # MEDIR: SS12D00G6 = cuerpo ~3.5 mm + palanca de 6 mm
SLIDE_LEVER, SLIDE_TRAVEL = 2.0, 2.0  # MEDIR: palanca de 2 x 2 mm y recorrido de 2 mm
LED_H, MIC_H = 0.8, 1.0

# Piezas de la placa (coordenadas KiCad). Los interruptores van por el CENTRO DEL CUERPO, no por el origen de la
# huella: en SW_Slide_SPDT_YIZHI_SS12D00G6 el origen es el pad 1 y el cuerpo se centra en el pad 2, a 2.5 mm.
BUTTONS = {"SW1": (54.0, 28.5)}                                            # hablar: el único pulsador de la v0.2
SLIDES = {"SW6": ((-17.9, 2.6), "x"), "SW2": ((61.5, 28.0), "y")}         # silencio del micrófono, encendido
LEDS = {"D8": (-11.5, 5.4), "D2": (42.5, 39.1), "D1": (58.0, 24.5), "D4": (42.8, 46.0)}
MICS = {"MK1": (8.265, 44.075), "MK2": (60.5, 37.5)}
J5, J6 = (-21.055, 24.0), (-18.1, 43.0)                   # FPC de 24 pines (abre hacia kx = -26) y táctil de 6 (abre hacia ky = 48)
NAV_V01 = {"SW3": (-21.0, 41.8), "SW4": (-14.6, 41.8), "SW5": (-8.2, 41.8)}   # ya no están: solo para controlar que no estén
H1 = (4.22, 4.22)                                         # M2, el único agujero de la placa
POSTS = [(-24.3, 8.0), (10.0, 31.0), (64.9, 27.0)]        # apoyos sobre zonas libres
USB = 33.0                                                # J1, abre hacia ky = 48
ANT = (9.0, 57.0)                                         # zona de la antena en kx (borde ky = 0)

# ---------- Base ----------
W, D, H = 194.0, 138.5, 36.0          # cerrada, el marco tiene el mismo contorno: un solo bloque. v1 y primera v2: 200 x 140;
                                      # se angostó 3 mm por lado y 1.5 arriba para afinar el bisel del marco
WALL, TOP, FLOOR = 2.4, 2.0, 3.0      # paredes, tapa de arriba y fondo B
R_BASE, EDGE = 12.0, 3.0              # radio de las esquinas y redondeo del borde de arriba
GAP, CLR = 0.4, 0.15                  # holgura del panel; holgura de impresión por lado en piezas que encajan
BAY = 9.0                             # entre el borde USB de la placa y la pared: enchufes JST y el túnel USB
FPC_ROOM = 12.0                       # delante de la placa: lugar para la cinta corta de J5
SPK_D, SPK_T = 28.0, 5.0              # MEDIR: dos parlantes redondos de 28 mm, 8 Ω 2 W, en paralelo (4 Ω)
SPK_X = (36.0, W - 36.0)              # uno detrás de cada rejilla del frente: el sonido sale del medio
SPK_Y0 = WALL + 0.5                   # cara del parlante contra una junta de espuma de 0.5 mm
SPK_Z = (FLOOR + H - TOP) / 2
BATT = (50.0, 80.0, 8.0)              # MEDIR: LiPo 805080 de 3000 mAh (con PCM), acostada a la izquierda
BATT_C = (WALL + CLR + 2.25 + BATT[0] / 2, 42 + BATT[1] / 2)   # pegada a la pared izquierda: su bahía toca el borde del fondo
LASTRE = (57.0, 44.5, 12.7)           # dos platinas de acero de 1¾ x ¼ pulgada de 57 mm, una sobre otra (~253 g). Eran de 60:
                                      # con la base 6 mm más angosta, 57 es lo que cabe entre la batería y los 15 mm de la antena
LASTRE_C = [(BATT_C[0] + BATT[0] / 2 + 4.5 + LASTRE[0] / 2, 36.0), (BATT_C[0] + BATT[0] / 2 + 4.5 + LASTRE[0] / 2, 86.0)]   # contra la bahía de la batería
J5_ADAPTER = (20.0, 14.0, 3.0)        # MEDIR: adaptador FPC 24 pines 0.5 mm -> 2.54 mm, en el piso bajo la placa
FEET = 10.0                           # patas de goma adhesivas Ø12 x 2, sobre los tornillos de las esquinas de B
MASS = {"panel": 50, "batería": 58, "parlantes": 24, "placa y componentes": 25, "driver": 15}   # g, MEDIR
J6_ADAPTER = (12.0, 15.0, 3.0)        # MEDIR: adaptador FPC 6 pines 0.5 mm -> cables (x, y, espesor), en el piso junto a J6
J6_LOOP = 4.6                         # de la pared derecha a la vuelta de la cinta corta de J6 (J6 abre hacia esa pared)
WIRE_D, N_WIRES = 0.8, 14             # MEDIR: cable de silicona AWG 30, ~0.8 mm con aislante; 8 del panel + 6 del táctil
NIP_ID = 6.5                          # MEDIR: paso interior del niple M10 x 1
PACK = {6: 3.0, 8: 3.305, 14: 4.328}  # diámetro del círculo más chico que envuelve n círculos iguales, en diámetros
def bundle_r(n):                      # radio con que se modela un haz de n hilos: empaquetado apretado + 10 %
    return WIRE_D * PACK[n] / 2 * 1.1
PRINT_WALL = 1.2                      # pared mínima: 3 perímetros de boquilla 0.4
# Placa del nombre: una píldora blanca al frente, entre las rejillas, con el nombre del niño o el logo del tutor
NOMBRE = next((a_.split("=", 1)[1] for a_ in sys.argv if a_.startswith("--nombre=")), "Mateo")
NAME_W, NAME_H, NAME_D, NAME_UP = 64.0, 13.0, 1.2, 0.5   # largo, alto, rebaje (= espesor de la placa) y relieve de las letras
FONT = Path("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf")
def text2d(txt, size):
    return Text(txt, font_size=size, font_path=str(FONT)) if FONT.exists() else Text(txt, font_size=size)

# Logo de Aule: el wordmark de aule-org/aule (landing/public/brand/aule-wordmark.svg), trazos de 14 con puntas
# cuadradas y esquinas en inglete, más los dos puntos de la Ë. Coordenadas del SVG (y hacia abajo).
AULE_STROKES = [[(0, 100), (26, 0), (38, 0), (64, 100)], [(15, 62), (49, 62)],          # A
                [(84, 0), (84, 100), (136, 100), (136, 0)],                               # U
                [(172, 0), (172, 100), (212, 100)],                                       # L
                [(276, 0), (232, 0), (232, 100), (276, 100)], [(232, 50), (262, 50)]]     # E
AULE_DOTS, AULE_HW, AULE_BOX = [(240, -24), (268, -24)], 7.0, (-7.0, -32.0, 283.0, 107.0)

def _stroke_outline(pts, hw):
    """Contorno de una polilínea con trazo de medio ancho hw, puntas cuadradas y esquinas en inglete."""
    def unit(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        n = math.hypot(dx, dy)
        return dx / n, dy / n
    d0, d1 = unit(pts[0], pts[1]), unit(pts[-2], pts[-1])
    pts = [(pts[0][0] - d0[0] * hw, pts[0][1] - d0[1] * hw)] + pts[1:-1] + [(pts[-1][0] + d1[0] * hw, pts[-1][1] + d1[1] * hw)]
    def side(s):
        out = []
        for i, p in enumerate(pts):
            dirs = [unit(pts[j], pts[j + 1]) for j in (i - 1, i) if 0 <= j < len(pts) - 1]
            norms = [(-dy * s, dx * s) for dx, dy in dirs]
            if len(norms) == 1:
                out.append((p[0] + norms[0][0] * hw, p[1] + norms[0][1] * hw))
            else:                                   # inglete: suma de normales escalada por 1 / cos(medio ángulo)
                mx, my = norms[0][0] + norms[1][0], norms[0][1] + norms[1][1]
                k_ = hw / (mx * norms[0][0] + my * norms[0][1])
                out.append((p[0] + mx * k_, p[1] + my * k_))
        return out
    return side(1) + side(-1)[::-1]

def aule_logo(height):
    """Wordmark de Aule centrado en el origen, de `height` mm de alto contando los puntos de la Ë."""
    x0, y0, x1, y1 = AULE_BOX
    s_ = height / (y1 - y0)
    tr = lambda p: ((p[0] - (x0 + x1) / 2) * s_, -(p[1] - (y0 + y1) / 2) * s_)
    sk = Sketch()
    for st in AULE_STROKES:
        sk += Polygon(*[tr(p) for p in _stroke_outline(st, AULE_HW)], align=None)
    for c in AULE_DOTS:
        sk += Pos(*tr(c)) * Circle(8 * s_)
    return sk

BX0 = W - WALL - BAY - BH             # x del borde ky = 0 (antena); el borde USB queda a BAY de la pared derecha
Y_BRD = SPK_Y0 + SPK_T + 3.0 + FPC_ROOM
BY0 = Y_BRD - KX0                     # y = BY0 + kx
Z_FACE = H - TOP - S                  # cara de componentes de la placa (mira hacia arriba)

def k(kx, ky):
    return (BX0 + ky, BY0 + kx)

# Tecla ● (H): la tecla blanca de Ø16 de la v1, ahora sobre SW1. Es un émbolo macizo que entra por abajo antes que la
# placa. No puede ir centrada en SW1: a 5.7 mm está el LED D1 y a 6.3 mm la ranura de SW2. Va corrida TALK_OFF y aprieta
# el pulsador con su cara de abajo, a 4.3 mm de su centro; dos pies la frenan contra la placa.
TALK_R = 8.0                          # radio de la tecla
TALK_OFF = (-3.3, 2.8)                # centro de la tecla respecto de SW1 (kx, ky): lo más cerca que deja D1, SW2 y los JST
CLR_KEY = 0.2                         # holgura por lado de la tecla en su agujero y en su collar
CAP_UP = 1.6                          # cuánto asoma sobre la tapa
PUSH_GAP = 0.2                        # contra su tope de arriba, de la tecla a SW1
TALK_STOP = 0.5                       # MEDIR: tras tocar SW1, cuánto baja hasta que los pies apoyan en la placa
LUG, LUG_UP, LUG_W = 1.2, 1.0, 4.0    # orejas de la tecla: salen 1.2 mm a 45°, entran 1 mm en la tapa, 4 mm de ancho
LUG_ANG = (170.0, 270.0)              # ángulos KiCad de las orejas: hacia donde no hay LED, micrófono, interruptor ni JST
TALK_FEET = [(47.6, 35.6), (44.9, 28.7)]   # pies de tope, sobre placa libre (kx, ky): con SW1 hacen un trípode
FOOT_R = 1.1
SLOT_W, SLOT_L = 2.4, 6.0             # ranura de los interruptores: palanca + 0.2 por lado, y recorrido + 1 por punta
DISH = 1.2                            # chaflán de 45° alrededor de la ranura de SW6: lugar para la yema del dedo
LED_TUBE_R, MIC_TUBE_R = 2.2, 2.6     # tubos de las guías de luz y de los micrófonos: pared de 1.2 mm

# ---------- Marco (E naranja, F tapa) ----------
TILT = 15.0                           # abierta, el panel se inclina hacia atrás
FW, FH = W, D                         # el marco tiene el contorno de la base
FB_BOT = 20.5                         # del borde de abajo del marco al panel: ahí adentro va la bisagra de arriba
FB_TOP, FB_SIDE = FH - FB_BOT - PH, (FW - PW) / 2
FWALL, FFRONT, FD, F_T = 2.4, 2.0, 17.0, 2.5
# El panel va girado 180°: su FPC sale por arriba (el firmware rota la imagen) y deja libre el centro del borde de
# abajo para la bisagra. AA_TOP queda abajo; arriba queda el borde inactivo del lado del FPC.
R_FRAME = 12.0                        # igual que la base
DRIVER = (30.2, 65.0, 5.0)            # MEDIR: Waveshare 13512 sin el conector de 40 pines, DE PIE: su conector FPC va
                                      # en un lado corto y la cola de 24 pines entra por arriba (en la v1 iba acostado)
DRV_FPC_OFF = 0.0                     # MEDIR: del centro del lado corto del driver al centro de su conector FPC
TOUCH_AD = (15.0, 12.0, 3.0)          # MEDIR: adaptador FPC 6 pines 0.5 mm -> cables en el marco (x, y, espesor)

# ---------- Bisagras y cuello (C) ----------
NW2, NT2 = 60.0, 14.0                 # ancho y espesor del cuello
Z_AX = H - NT2 / 2                    # cerrada, el eje de arriba queda a esta altura y el cuello al ras de la tapa
NUT_R = 7.0                           # tuerca moleteada fina M10 x 1 de lámpara, Ø14
Z_H1 = H - TOP - NUT_R - 0.5          # H1 un poco más abajo: su tuerca cabe bajo la tapa; cerrado, el cuello se inclina
GAP_C = 2.5                           # cerrada, de la tapa al frente del marco: 4 topes de goma de 2.5 mm en el bisel
Y_A = 10.0                            # eje de arriba: dentro del bisel de abajo del marco, 10 mm sobre su borde ...
Z_A = -FD / 2                         # ... y a media profundidad
KNUCKLE_R = FD / 2 - 0.2              # la punta del cuello es un cilindro del espesor del marco: tapa el hueco al ras,
                                      # adelante con el marco abierto y arriba con la base cerrada
H2C_Y = D - Y_A                       # cerrada, el borde de abajo del marco coincide con el de atrás de la base
H2C_Z = H + GAP_C - Z_A               # cerrada, el eje queda dentro del marco: la punta del cuello sube en L hasta él
NOTCH_Y = Y_A + KNUCKLE_R + 0.5       # hueco del bisel de abajo donde entra el cuello, a lo ancho del cuello
BLOCK_T = 12.0                        # bloques a cada lado del hueco, dentro del marco: llevan el niple y el pasador
O_OPEN = (60.0, 78.0)                 # abierta: borde de abajo del frente del marco (y, z), como en el render
WASH = 1.0                            # entre el cuello y cada oreja: arandela de PTFE de 1 mm
NIP_D, NIP_TAP = 10.3, 9.0            # niple M10 x 1: paso liso en la oreja o la pared, Ø9 en el cuello (se rosca)
PIN_D = 4.3                           # pasador: tornillo M4 de nylon con tuerca de nylon dentro del cuello
CABLE_D = 7.0                         # canal de los 14 cables dentro del cuello (v1: Ø6 para 8)


def box(x0, y0, z0, x1, y1, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)

def cyl(x, y, z0, z1, r):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(r, z1 - z0)

def ycyl(x, z, y0, y1, r):                            # cilindro a lo largo de y
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, y1 - y0)

def xcyl(x0, x1, y, z, r):                            # cilindro a lo largo de x
    return Pos((x0 + x1) / 2, y, z) * Rot(0, 90, 0) * Cylinder(r, x1 - x0)

def rrect(cx, cy, w, h, r, z0, z1):
    return Pos(cx, cy, z0) * extrude(RectangleRounded(w, h, r), amount=z1 - z0)

def rect(x0, y0, x1, y1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * Rectangle(x1 - x0, y1 - y0)

def side_extrude(face, x0, x1):                       # cara del plano (y, z) extruida entre x0 y x1
    return Pos(x0, 0, 0) * extrude(Plane.YZ * face, amount=x1 - x0, dir=(1, 0, 0))

def ivol(p_, q_):                                     # volumen del cruce; NaN si OCC no lo puede calcular
    try:
        return (p_ & q_).volume
    except Exception:
        return float("nan")

def segments(x0, x1, gaps):                           # tramos de [x0, x1] que quedan fuera de los huecos (centro, medio ancho)
    segs, a_ = [], x0
    for c_, hw_ in sorted(gaps):
        if c_ - hw_ > a_:
            segs.append((a_, min(c_ - hw_, x1)))
        a_ = max(a_, c_ + hw_)
    if a_ < x1:
        segs.append((a_, x1))
    return [s_ for s_ in segs if s_[1] - s_[0] >= 3.0]

# ---------- Comprobaciones de diseño ----------
T0 = time.time()
def tick(label):                                      # con --tiempos, cuánto tarda cada sección
    if "--tiempos" in sys.argv:
        print(f"[{time.time() - T0:6.1f} s] {label}", flush=True)
checks = []
def check(ok, msg):
    checks.append((ok, msg))

check(W <= 250 and D <= 250 and FW <= 250 and FH <= 250,
      f"base ({W:.0f} x {D:.0f}) y marco ({FW:.1f} x {FH:.1f}) caben en la cama de 256 mm de la Centauri Carbon")
check(SPK_Z - SPK_D / 2 - 1.2 > FLOOR and SPK_Z + SPK_D / 2 + 1.2 < H - TOP, "los parlantes caben de pie en la base")
check(Z_FACE - BT - 2.5 > FLOOR + 1, "bajo la placa hay espacio para las patas THT y los cables")
for name, (kx, ky) in {**BUTTONS, **LEDS, **MICS, "J6": J6, **{n_: p_ for n_, (p_, _) in SLIDES.items()}}.items():
    x, y = k(kx, ky)
    check(WALL < x < W - WALL and Y_BRD < y < Y_BRD + BW, f"{name} cae dentro de la placa")
ax0, ay0, ay1 = BX0, BY0 + ANT[0], BY0 + ANT[1]
check(not any(ANT[0] - 3 < kx < ANT[1] + 3 and ky < 15 for kx, ky in POSTS), "ningún apoyo dentro de la zona de la antena")
bx0, by0 = BATT_C[0] - BATT[0] / 2, BATT_C[1] - BATT[1] / 2
bx1, by1 = BATT_C[0] + BATT[0] / 2, BATT_C[1] + BATT[1] / 2
check(ax0 - bx1 > 15, f"la batería queda a {ax0 - bx1:.0f} mm de la antena")
check(min(WALL, TOP, FLOOR) >= PRINT_WALL, f"paredes de la base: {WALL} / {TOP} / {FLOOR} mm, todas de {PRINT_WALL} mm o más")
check(0.15 <= CLR <= 0.2 and 0.15 <= CLR_KEY <= 0.2, f"holgura entre piezas que encajan: {CLR} mm por lado ({CLR_KEY} en la tecla)")

# ---------- Placa real: el STEP de la v0.2 ----------
# Se carga antes de construir nada: los tubos y el collar de la tecla se recortan contra los componentes reales, y cada
# control de la tapa se alinea con el sólido de su pieza, no con una coordenada copiada.
BOARD_STEP = Path(next((a_.split("=", 1)[1] for a_ in sys.argv if a_.startswith("--board=")),
                       Path(__file__).resolve().parents[1] / "board" / "capri-slate-v0.2.2-tactil.step"))
if not BOARD_STEP.exists():
    sys.exit(f"falta {BOARD_STEP}: sin la placa real no hay control de calce")
brd = Pos(BX0, BY0, Z_FACE - BT) * Rot(0, 0, 90) * import_step(str(BOARD_STEP))
def kbox(s):                                          # caja de un sólido: kx0, kx1, ky0, ky1 y z sobre la cara de componentes
    b_ = s.bounding_box()
    return (b_.min.Y - BY0, b_.max.Y - BY0, b_.min.X - BX0, b_.max.X - BX0, b_.min.Z - Z_FACE, b_.max.Z - Z_FACE)
BRD = [(s, kbox(s)) for s in brd.solids()]
SUBSTRATE = max(BRD, key=lambda sb: sb[1][1] - sb[1][0])[0]
def is_slide(kb):                                     # el SS12D00G6 viene en el STEP como una caja maciza de 8.5 x 3.5 x 8.5
    return sorted(round(v, 1) for v in (kb[1] - kb[0], kb[3] - kb[2], kb[5] - kb[4])) == [3.5, 8.5, 8.5]
def part_at(kx, ky, tol=0.5):                         # el sólido más alto cuyo centro en planta cae a menos de tol de (kx, ky)
    c_ = [sb for sb in BRD if sb[1][1] - sb[1][0] < 60 and abs((sb[1][0] + sb[1][1]) / 2 - kx) < tol
          and abs((sb[1][2] + sb[1][3]) / 2 - ky) < tol]
    return max(c_, key=lambda sb: sb[1][5]) if c_ else None
def near_parts(x, y, r, z_min):                       # cajas, con 0.3 mm de aire, de lo que la placa tiene más alto que z_min a menos de r
    boxes = []
    for s, kb in BRD:
        b_ = s.bounding_box()
        top_ = Z_FACE + SLIDE_BODY if is_slide(kb) else b_.max.Z
        if s is SUBSTRATE or top_ <= z_min:
            continue
        if math.hypot(max(b_.min.X - x, 0, x - b_.max.X), max(b_.min.Y - y, 0, y - b_.max.Y)) < r + 0.3:
            boxes.append(box(b_.min.X - 0.3, b_.min.Y - 0.3, Z_FACE - 0.1, b_.max.X + 0.3, b_.max.Y + 0.3, top_ + 0.3))
    return boxes
sw1 = part_at(*BUTTONS["SW1"], 0.3)
check(sw1 is not None and abs(sw1[1][5] - BTN_H) < 0.15,
      f"STEP: SW1 está en kx {BUTTONS['SW1'][0]}, ky {BUTTONS['SW1'][1]} y mide {sw1[1][5] if sw1 else 0:.2f} mm de alto")
for name, ((kx, ky), axis) in SLIDES.items():
    p_ = part_at(kx, ky, 0.3)
    ok_ = p_ is not None and is_slide(p_[1]) and ((p_[1][1] - p_[1][0] > 8) == (axis == "x"))
    check(ok_, f"STEP: el cuerpo de {name} está centrado en kx {kx}, ky {ky}, con el recorrido a lo largo de {'kx' if axis == 'x' else 'ky'}")
for name, (kx, ky) in LEDS.items():
    check(part_at(kx, ky, 0.3) is not None, f"STEP: el LED {name} está bajo su guía de luz (kx {kx}, ky {ky})")
for name, (kx, ky) in MICS.items():
    check(part_at(kx, ky, 0.5) is not None, f"STEP: el micrófono {name} está bajo su puerto (kx {kx}, ky {ky}, a menos de 0.5 mm)")
j6_solids = [kb for s, kb in BRD if s is not SUBSTRATE and abs((kb[0] + kb[1]) / 2 - J6[0]) < 1.0 and kb[2] > 40 and kb[3] < 48.01 and kb[5] > 1.0]
J6_MOUTH = max((kb[3] for kb in j6_solids), default=0.0)   # ky de la boca de J6
check(len(j6_solids) >= 1 and 46.5 < J6_MOUTH <= BH, f"STEP: J6 está en kx {J6[0]} y su boca queda en ky {J6_MOUTH:.1f}, hacia el borde ky = {BH:.0f}")
check(not any(kb[5] > 2.5 and abs((kb[0] + kb[1]) / 2 - kx) < 2 and abs((kb[2] + kb[3]) / 2 - ky) < 2 for s, kb in BRD for kx, ky in NAV_V01.values()),
      "STEP: en el lugar de SW3, SW4 y SW5 no queda ningún pulsador")
tick("placa cargada")


# ---------- Cinemática de las bisagras ----------
# Cerrada, el cuello va acostado de H1 (adelante) a H2 (atrás) y el marco queda boca abajo: su borde de arriba
# hacia el frente. Abierta, el cuello gira PSI alrededor de H1 y el marco queda a TILT, con su borde de abajo en
# O_OPEN. De esas dos posiciones salen el largo del cuello y el lugar de H1.
th = math.radians(TILT)
UP, FRONT = (math.sin(th), math.cos(th)), (-math.cos(th), math.sin(th))   # abierta, en (y, z)
def add(p, d, s):
    return (p[0] + d[0] * s, p[1] + d[1] * s)
H2O = add(add(O_OPEN, UP, Y_A), FRONT, Z_A)
H2C = (H2C_Y, H2C_Z)
# H1 está a la misma distancia de H2 cerrada y de H2 abierta: sobre la mediatriz de las dos, a la altura Z_H1
Y1 = ((H2O[0] ** 2 - H2C_Y ** 2) + (Z_H1 - H2O[1]) ** 2 - (Z_H1 - H2C_Z) ** 2) / (2 * (H2O[0] - H2C_Y))
AX1 = (Y1, Z_H1)                                      # eje H1
LN = math.dist(AX1, H2C)                              # distancia entre los ejes
PHI0 = math.degrees(math.atan2(H2C_Z - Z_H1, H2C_Y - Y1))           # cerrado, de H1 a H2 en línea recta
PSI = math.degrees(math.atan2(H2O[1] - Z_H1, H2O[0] - Y1)) - PHI0   # giro de H1, de cerrada a abierta
A_OPEN, A_CLOSED = 90.0 - TILT, 180.0                 # giro del marco alrededor de x
def pose(t):                                          # t = 1 abierta, 0 cerrada; los dos giros van parejos
    psi = PSI * t
    h2 = (AX1[0] + LN * math.cos(math.radians(PHI0 + psi)), AX1[1] + LN * math.sin(math.radians(PHI0 + psi)))
    ang = A_CLOSED + (A_OPEN - A_CLOSED) * t
    r = math.radians(ang)
    ay, az = Y_A * math.cos(r) - Z_A * math.sin(r), Y_A * math.sin(r) + Z_A * math.cos(r)
    return psi, h2, Pos(W / 2, h2[0] - ay, h2[1] - az) * Rot(ang, 0, 0)
FRAME_OPEN, FRAME_CLOSED = pose(1)[2], pose(0)[2]
def fw(loc, x, y, z):                                 # punto del marco -> mundo
    return (loc * Pos(x, y, z)).position
o = fw(FRAME_OPEN, 0, 0, 0)
check(abs(o.Y - O_OPEN[0]) < 1e-6 and abs(o.Z - O_OPEN[1]) < 1e-6, "abierta, el marco queda donde se pidió")
check(abs(fw(FRAME_CLOSED, 0, 0, 0).Z - (H + GAP_C)) < 1e-6, "cerrada, el frente del marco queda sobre los topes")

# ---------- A: base (tapa de arriba y paredes) ----------
def facet(c_):                                        # tamaño del chaflán cuya cara de 45° es tangente a un redondeo de radio c_
    return c_ * (2 - math.sqrt(2)) + 0.03
rr = rrect(W / 2, D / 2, W, D, R_BASE, 0, H)
outer = fillet(rr.edges().group_by(Axis.Z)[-1], EDGE)
# La tapa va sobre la cama: la mitad de abajo del redondeo pasa de 45°. Se cambia por una faceta de 45° tangente al
# redondeo (0.9 mm de alto); el resto del canto sigue redondo.
outer += chamfer(rr.edges().group_by(Axis.Z)[-1], facet(EDGE)) & box(-1, -1, H - EDGE * (1 - math.cos(math.radians(45))) - 0.05, W + 1, D + 1, H + 1)
outer = chamfer(outer.edges().group_by(Axis.Z)[0], 1.2)  # chaflán abajo: la base se despega de la mesa y no hace pata de elefante
a = outer - rrect(W / 2, D / 2, W - 2 * WALL, D - 2 * WALL, R_BASE - WALL, -1, H - TOP)
# Hueco para el pulgar al frente, al centro: cerrada, deja levantar el borde del marco sin uñas. Sus paredes bajan a
# 45° (en la v1 era un elipsoide, que sobre la cama pedía soporte).
SCOOP = (44.0, 6.0, 5.8)              # ancho, fondo en y, y alto
a += box(W / 2 - SCOOP[0] / 2 - 2, WALL - 0.01, H - TOP - SCOOP[2] - 1.2, W / 2 + SCOOP[0] / 2 + 2, SCOOP[1] + 2.5, H - TOP + 0.01)
a -= loft([Plane.XY.offset(H + 0.01) * Pos(W / 2, 0) * Ellipse(SCOOP[0] / 2, SCOOP[1]),
           Plane.XY.offset(H - SCOOP[2]) * Pos(W / 2, 0) * Ellipse(SCOOP[0] / 2 - SCOOP[2], SCOOP[1] - SCOOP[2])])

# ---------- Controles de la tapa: tecla ●, interruptores, luces y micrófonos ----------
Z_IN = H - TOP                            # cara interior de la tapa
adds, cuts = [], []                       # primero todo lo que suma y después todo lo que corta
SW1C = k(*BUTTONS["SW1"])
TALK_K = (BUTTONS["SW1"][0] + TALK_OFF[0], BUTTONS["SW1"][1] + TALK_OFF[1])
TALK_C = k(*TALK_K)
Z_PUCK = Z_FACE + BTN_H + PUSH_GAP        # cara de abajo de la tecla, contra su tope de arriba
LUG_LO = Z_IN + LUG_UP - LUG - 1.0        # cara de abajo de las orejas
def lug(theta, grow):                     # oreja de la tecla; con grow > 0, su asiento en la tapa y su ranura en el collar
    th_ = math.radians(theta)
    ux, uy = math.sin(th_), math.cos(th_)                 # un ángulo KiCad, en el mundo: x = ky, y = kx
    pl = Plane(origin=(TALK_C[0], TALK_C[1], 0), x_dir=(ux, uy, 0), z_dir=(uy, -ux, 0))   # (radio, z)
    zt, r1 = Z_IN + LUG_UP, TALK_R + LUG + grow
    z_lo = Z_PUCK - 1 if grow else LUG_LO
    pts = [(TALK_R - 1.5, zt), (TALK_R, zt), (r1, zt - LUG - grow), (r1, z_lo), (TALK_R - 1.5, z_lo)]
    return extrude(pl * Polygon(*pts, align=None), amount=LUG_W / 2 + (CLR_KEY if grow else 0), both=True)
# Collar: sigue la guía de la tecla bajo la tapa, hasta la altura de SW1. Se recorta donde la placa tiene algo más alto.
collar = cyl(*TALK_C, Z_PUCK, Z_IN + 0.01, TALK_R + CLR_KEY + PRINT_WALL)
trim = near_parts(*TALK_C, TALK_R + CLR_KEY + PRINT_WALL, Z_PUCK - 0.3)
adds.append(collar - Compound(trim) if trim else collar)
cuts.append(cyl(*TALK_C, Z_PUCK - 1, H + 1, TALK_R + CLR_KEY))
cuts += [lug(th_, 0.3) for th_ in LUG_ANG]
# Interruptores deslizantes: ranura para la palanca. La de SW6 lleva un chaflán de 45° para la yema del dedo.
for name, ((kx, ky), axis) in SLIDES.items():
    x, y = k(kx, ky)
    lx, ly = (SLOT_W, SLOT_L) if axis == "x" else (SLOT_L, SLOT_W)        # kx corre a lo largo de y
    ch_ = DISH if name == "SW6" else 0.4
    cuts.append(box(x - lx / 2, y - ly / 2, Z_IN - 1, x + lx / 2, y + ly / 2, H + 1))
    cuts.append(Pos(x, y, H - ch_) * extrude(Rectangle(lx, ly), amount=ch_ + 0.01, taper=-45))
    side_, end_ = (SLOT_W - SLIDE_LEVER) / 2, (SLOT_L - SLIDE_LEVER - SLIDE_TRAVEL) / 2
    check(side_ >= 0.2 - 1e-9 and end_ >= 0.5 - 1e-9, f"{name}: la palanca recorre sus {SLIDE_TRAVEL:.0f} mm con {end_:.1f} mm de aire en cada punta y {side_:.1f} a los lados")
    up_ = Z_FACE + SLIDE_TOP - H
    check(0.5 <= up_ <= GAP_C - 0.5, f"{name}: la palanca asoma {up_:.1f} mm sobre la tapa y queda bajo el marco cerrado")
check(TOP - DISH >= 0.8, f"bajo el chaflán de SW6 quedan {TOP - DISH:.1f} mm de tapa")
# LEDs: guía de luz desde la tapa hasta 0.5 mm del LED; D8 verde = micrófono encendido, D4 = carga (junto al USB)
for kx, ky in LEDS.values():
    x, y = k(kx, ky)
    tube = cyl(x, y, Z_FACE + LED_H + 0.5, Z_IN + 0.01, LED_TUBE_R)
    trim = near_parts(x, y, LED_TUBE_R, Z_FACE + LED_H + 0.45)
    adds.append(tube - Compound(trim) if trim else tube)
    cuts.append(cyl(x, y, Z_FACE, H + 1, 1.0))
d8, s6 = k(*LEDS["D8"]), k(*SLIDES["SW6"][0])
check(math.dist(d8, s6) - 1.0 - SLOT_L / 2 - DISH >= 1.0, f"la ventana de D8 queda a {math.dist(d8, s6):.1f} mm de la ranura de SW6, fuera de su chaflán")
# Micrófonos: puerto Ø1.6 y tubo de sellado hasta 0.3 mm del micrófono (con anillo de espuma o silicona)
for kx, ky in MICS.values():
    x, y = k(kx, ky)
    tube = cyl(x, y, Z_FACE + MIC_H + 0.3, Z_IN + 0.01, MIC_TUBE_R)
    trim = near_parts(x, y, MIC_TUBE_R, Z_FACE + MIC_H + 0.25)
    adds.append(tube - Compound(trim) if trim else tube)
    cuts += [cyl(x, y, Z_FACE, H + 1, 0.8), cyl(x, y, Z_FACE, Z_FACE + MIC_H + 1.3, 1.4)]
# Apoyos de la placa y torre de H1 (M2 de nylon desde abajo; nylon por la cercanía de la antena)
for kx, ky in POSTS:
    adds.append(cyl(*k(kx, ky), Z_FACE, Z_IN + 0.01, 1.0))
x, y = k(*H1)
adds.append(cyl(x, y, Z_FACE, Z_IN + 0.01, 2.5))
cuts.append(cyl(x, y, Z_FACE - 1, Z_FACE + 5, 0.8))        # piloto para M2 autorroscante
for s_ in adds:
    a += s_
for s_ in cuts:
    a -= s_
for n_, p_ in (("D1", LEDS["D1"]), ("D2", LEDS["D2"]), ("MK2", MICS["MK2"])):
    web_ = math.dist(TALK_K, p_) - (TALK_R + CLR_KEY) - (1.0 if n_[0] == "D" else 0.8)
    check(web_ >= 0.75, f"entre el agujero de la tecla ● y el de {n_} quedan {web_:.2f} mm de tapa")
web_ = SLIDES["SW2"][0][0] - SLOT_W / 2 - TALK_K[0] - (TALK_R + CLR_KEY)
check(web_ >= PRINT_WALL, f"entre el agujero de la tecla ● y la ranura de SW2 quedan {web_:.1f} mm de tapa")
check(TOP - (LUG_UP - CLR_KEY) >= PRINT_WALL, f"sobre el asiento de las orejas quedan {TOP - LUG_UP + CLR_KEY:.1f} mm de tapa")
# USB-C: túnel por la pared derecha, sobre el espacio de los JST (los cables pasan por debajo)
_, uy = k(USB, 0)
uz = Z_FACE + 1.63
a += box(BX0 + BH + 1.2, uy - 9.0, uz - 5.75, W - WALL + 0.1, uy + 9.0, H - TOP)
a -= box(BX0 + BH - 1, uy - 6.75, uz - 3.75, W + 1, uy + 6.75, uz + 3.75)
# Parlantes: un bloque con media caña que los centra contra el frente y sigue en dos arcos hasta 45° (sobre la cama,
# un aro completo cerraba en voladizo). Delante de cada uno, una rejilla redonda del mismo eje.
GRILLE_R = 10.0                       # círculo de agujeros Ø1.2 en trama hexagonal, dentro del aro sellado
for sx in SPK_X:
    ro, ri = SPK_D / 2 + 0.3 + PRINT_WALL, SPK_D / 2 + 0.3
    holder = box(sx - ro, WALL - 0.01, SPK_Z, sx + ro, WALL + 3.0, H - TOP + 0.01)
    holder += ycyl(sx, SPK_Z, WALL - 0.01, WALL + 3.0, ro) & box(sx - ro, WALL - 0.02, SPK_Z - ri * math.cos(math.radians(45)), sx + ro, WALL + 3.1, SPK_Z + 0.01)
    a += holder - ycyl(sx, SPK_Z, WALL - 0.1, WALL + 3.1, ri)
    region = Pos(sx, SPK_Z) * Circle(GRILLE_R)
    holes = []
    for i in range(-6, 7):
        for j in range(-6, 7):
            hx, hz = sx + 2.2 * (i + 0.5 * (j % 2)), SPK_Z + 1.9 * j
            if (Pos(hx, hz) * Circle(0.6) - region).area < 1e-6:
                holes.append(ycyl(hx, hz, -1, WALL + 1, 0.6))
    a -= Compound(holes)
    check(GRILLE_R < SPK_D / 2 - 2, "la rejilla queda dentro del aro sellado del parlante")
# Rebaje de la placa del nombre, al frente y a la altura de las rejillas. Su canto de abajo sube a 45° (sobre la cama
# ese canto es un techo): la placa N lleva el mismo bisel.
NAME_PL = Plane(origin=(W / 2, NAME_D, SPK_Z), x_dir=(1, 0, 0), z_dir=(0, -1, 0))   # mira hacia afuera del frente
def name_wedge(zb_):                                  # lo que queda sobre el plano de 45° que nace en el frente, a la altura zb_
    return side_extrude(Polygon((-2, zb_ - 2), (4, zb_ + 4), (4, zb_ + 40), (-2, zb_ + 40), align=None), 0, W)
a -= extrude(NAME_PL * SlotOverall(NAME_W + 2 * CLR, NAME_H + 2 * CLR), amount=NAME_D + 1) & name_wedge(SPK_Z - NAME_H / 2 - CLR)
check(WALL - NAME_D >= 1.0, f"detrás de la placa del nombre quedan {WALL - NAME_D:.1f} mm de pared")
check(W / 2 - NAME_W / 2 - CLR > SPK_X[0] + GRILLE_R + 15, "la placa del nombre queda entre las rejillas, con aire a los lados")
# Torres de los tornillos de B (piloto M3 autorroscante desde abajo)
BOSSES = [(10, 10), (W - 10, 10), (10, D - 10), (W - 10, D - 10), (W / 2, 8)]
for x, y in BOSSES:
    a += cyl(x, y, FLOOR, H - TOP, 3.5)
    a -= cyl(x, y, FLOOR - 0.01, FLOOR + 9, 1.3)
# Bolsillo del cuello: una bandeja colgada de la tapa. Adelante gira el cuello alrededor de H1; atrás entran las orejas
# del marco cuando se cierra. Las paredes de los costados son las orejas de H1: el niple a la izquierda, el pasador a la
# derecha, cada uno con un buje por fuera.
xl, xr = W / 2 - NW2 / 2, W / 2 + NW2 / 2             # costados del cuello
KNEE = (H2C_Y, Z_AX)                                  # codo: donde el tramo acostado empieza a subir
POCKET = [(xl - WASH, AX1[0] - 12.0, xr + WASH, H2C_Y + NT2 / 2 + 0.5, Z_H1 - NT2 / 2 - 1.0)]           # cuello
TW = 2.5                                              # pared de la bandeja
for x0, y0, x1, y1, zf in POCKET:
    a += box(x0 - TW, y0 - TW, zf - TW, x1 + TW, y1 + TW, H - TOP + 0.01)
for x0, y0, x1, y1, zf in POCKET:
    a -= box(x0, y0, zf, x1, y1, H + 1)
    # Tope de H1: el borde de adelante del bolsillo llega hasta 0.5 mm del cuello abierto. Si alguien tira la pantalla
    # hacia adelante, el cuello apoya ahí en vez de seguir girando y volcar la base hacia el niño.
    th1 = math.atan2(KNEE[1] - AX1[1], KNEE[0] - AX1[0]) + math.radians(PSI)   # primer tramo del cuello, abierto
    ny_, nz_ = -math.sin(th1), math.cos(th1)
    Y_STOP = AX1[0] + NT2 / 2 * ny_ + (H - TOP - 1 - AX1[1] - NT2 / 2 * nz_) * math.cos(th1) / math.sin(th1) - 0.5
    a += box(x0, y0 - 0.01, H - TOP - 1, x1, Y_STOP, H)
    a -= Pos((x0 + x1) / 2, (Y_STOP + y1) / 2, H - 0.8) * extrude(Rectangle(x1 - x0, y1 - Y_STOP), amount=0.81, taper=-45)  # chaflán del borde
a += xcyl(xl - WASH - TW - 6, xl - WASH - TW + 0.01, *AX1, 9.0) & box(0, 0, 0, W, D, H - TOP + 0.01)   # buje del niple
PIN_BUSH, PIN_HEAD = 3.5, (4.2, 3.2)   # buje del pasador: corto, para no llegar a la placa, y con la cabeza del M4 embutida (radio, fondo)
a += xcyl(xr + WASH + TW - 0.01, xr + WASH + TW + PIN_BUSH, *AX1, 6.0)       # buje del pasador
a += box(xr + WASH + TW - 0.01, AX1[0] - 6.0, AX1[1], xr + WASH + TW + PIN_BUSH, AX1[0] + 6.0, H - TOP + 0.01)   # unido a la tapa: sobre la cama no nace en el aire
a -= xcyl(xl - WASH - TW - 7, xl - WASH + 0.01, *AX1, NIP_D / 2)
a -= xcyl(xr + WASH - 0.01, xr + WASH + TW + 6, *AX1, PIN_D / 2)
a -= xcyl(xr + WASH + TW + PIN_BUSH - PIN_HEAD[1], xr + WASH + TW + PIN_BUSH + 1, *AX1, PIN_HEAD[0])       # cajuela de la cabeza
check(BX0 - (xr + WASH + TW + PIN_BUSH) >= 0.5 and TW + PIN_BUSH - PIN_HEAD[1] >= 2.5,
      f"el buje del pasador de H1 queda a {BX0 - (xr + WASH + TW + PIN_BUSH):.1f} mm del borde de la placa, con la cabeza embutida y {TW + PIN_BUSH - PIN_HEAD[1]:.1f} mm de apoyo")
# Desagüe del bolsillo: un jugo derramado sale por abajo y no sube hasta los pasos del niple
zf = POCKET[0][4]
DRAIN = (W / 2, 118.0)
a += cyl(*DRAIN, FLOOR, zf - TW + 0.01, 3.0)
a -= cyl(*DRAIN, FLOOR - 1, zf + 1, 2.0)
# Costillas que sujetan el lastre de adelante y la batería si la base se cae (1 mm de EVA sobre la batería).
# El lastre de atrás lo sujeta el piso del bolsillo, 0.3 mm encima.
for x in (LASTRE_C[0][0] - 14, LASTRE_C[0][0] + 14):
    a += box(x - 0.8, LASTRE_C[0][1] - 16, FLOOR + LASTRE[2] + 0.5, x + 0.8, LASTRE_C[0][1] + 6, H - TOP + 0.01)
for x in (bx0 + 12, bx1 - 22):
    a += box(x - 0.8, by0 + 6, FLOOR + BATT[2] + 1.0, x + 0.8, by1 - 6, H - TOP + 0.01)
check(zf - TW - (FLOOR + LASTRE[2]) < 0.5, "el piso del bolsillo sujeta el lastre de atrás")
check(xl - WASH < ax0 - 15, f"el niple de H1, de metal, queda a {ax0 - xl + WASH:.0f} mm de la antena; el pasador es de nylon")
check(max(p[3] for p in POCKET) < D - WALL and min(p[0] for p in POCKET) - TW > WALL, "el bolsillo cabe dentro de la base")
check(all(p[2] + TW < BX0 or p[1] - TW > Y_BRD + BW for p in POCKET), "el bolsillo del cuello no llega a la placa")

# ---------- B: fondo ----------
b = rrect(W / 2, D / 2, W - 2 * WALL - 2 * CLR, D - 2 * WALL - 2 * CLR, R_BASE - WALL - CLR, 0, FLOOR)
FOOT_REC = 1.0                                        # las patas van hundidas 1 mm: no se despegan con la uña
def countersunk(part, x, y, z0=0.0):
    part -= cyl(x, y, -1, FLOOR + 1, 1.7)
    return part - Pos(x, y, z0 + 0.85) * Cone(3.4, 1.7, 1.7)   # avellanado a 90° para la cabeza, desde abajo
for i, (x, y) in enumerate(BOSSES):
    if i < 4:                                         # las 4 esquinas llevan pata encima del tornillo
        b -= cyl(x, y, -1, FOOT_REC, 6.3)
    b = countersunk(b, x, y, FOOT_REC if i < 4 else 0.0)
    # Piel de 0.2 mm bajo el avellanado: el techo de la cajuela sale como un puente entero. El tornillo la perfora.
    if i < 4:
        b += cyl(x, y, FOOT_REC, FOOT_REC + 0.2, 6.3)
b -= cyl(*DRAIN, -1, FLOOR + 1, 2.0)                  # salida del desagüe
# Pernos que aprietan la placa contra los apoyos (la cara de abajo de la placa no tiene piezas)
for kx, ky in POSTS:
    x, y = k(kx, ky)
    b += cyl(x, y, FLOOR - 0.01, Z_FACE - BT, 1.5)
# Topes que aprietan cada parlante contra su aro
for sx in SPK_X:
    b += box(sx - 8, SPK_Y0 + SPK_T + 0.1, FLOOR - 0.01, sx + 8, SPK_Y0 + SPK_T + 2.6, SPK_Z)
# Bahía de la batería, con salida del cable hacia atrás (va por detrás de la placa hasta J2)
b += box(bx0 - 2.2, by0 - 2.2, FLOOR - 0.01, bx1 + 2.2, by1 + 2.2, FLOOR + 4) - box(bx0 - 1, by0 - 1, FLOOR - 1, bx1 + 1, by1 + 1, FLOOR + 5)
b -= box(bx1 - 15, by1, FLOOR, bx1 - 5, by1 + 3, FLOOR + 5)
# Lastre: dos bolsillos para las platinas de acero
ballast = []
for cx_, cy_ in LASTRE_C:
    lx0, ly0, lx1, ly1 = cx_ - LASTRE[0] / 2, cy_ - LASTRE[1] / 2, cx_ + LASTRE[0] / 2, cy_ + LASTRE[1] / 2
    b += box(lx0 - 2.2, ly0 - 2.2, FLOOR - 0.01, lx1 + 2.2, ly1 + 2.2, FLOOR + 9) - box(lx0 - 1, ly0 - 1, FLOOR - 1, lx1 + 1, ly1 + 1, FLOOR + 10)
    ballast.append(box(lx0, ly0, FLOOR, lx1, ly1, FLOOR + LASTRE[2]))
    check(lx0 - 2.2 > bx1 + 2.2 and lx1 + 2.2 < ax0 - 15, f"el lastre en y {cy_:.0f} queda entre la batería y la antena, a {ax0 - lx1 - 2.2:.0f} mm de ella")
check(LASTRE_C[0][1] + LASTRE[1] / 2 + 2.2 < LASTRE_C[1][1] - LASTRE[1] / 2 - 2.2, "las dos platinas no se pisan")

# ---------- C: cuello ----------
# En L: cerrado va acostado en el bolsillo y la punta sube hasta el eje de arriba, dentro del marco. Abierto, la L
# queda como el cuello del render: sube de la base y dobla hacia el marco. Se imprime acostado, de costado.
# Adentro corre el canal de los cables entre los dos niples; el agujero del codo ayuda a pasarlos.
def seg(p, q, t):                                     # tramo grueso del plano (y, z)
    L_ = math.dist(p, q)
    ny, nz = -(q[1] - p[1]) / L_ * t / 2, (q[0] - p[0]) / L_ * t / 2
    return Polygon((p[0] + ny, p[1] + nz), (q[0] + ny, q[1] + nz), (q[0] - ny, q[1] - nz), (p[0] - ny, p[1] - nz), align=None)
prof = seg(AX1, KNEE, NT2) + seg(KNEE, H2C, NT2) + Pos(*AX1) * Circle(NT2 / 2) + Pos(*KNEE) * Circle(NT2 / 2) + Pos(*H2C) * Circle(KNUCKLE_R)
ss = side_extrude(prof, xl, xr).solids()             # el perfil sale en 4 trozos: se fusionan antes de redondear
neck_raw = (ss[0].fuse(*ss[1:]) if len(ss) > 1 else ss[0]).clean().solids()[0]
def side_edges(s_, xs):
    return s_.edges().filter_by(lambda e_: any(abs(e_.center().X - x_) < 0.01 for x_ in xs))
neck_c = Part(neck_raw.fillet(2.0, side_edges(neck_raw, (xl, xr))).wrapped)   # cantos redondeados
# Se imprime de costado, con la cara izquierda (x = xl) sobre la cama: ahí el redondeo lleva una faceta de 45°.
neck_c = (neck_c + (box(xl - 1, -50, -50, xl + 2.0 * (1 - math.cos(math.radians(45))) + 0.1, D + 50, 150) & neck_raw)
          ) & (Part() + neck_raw.chamfer(facet(2.0), None, side_edges(neck_raw, (xl,))))
for ax in (AX1, H2C):
    neck_c -= xcyl(xl - 1, xl + 14, *ax, NIP_TAP / 2)                    # el niple se rosca acá
    neck_c -= xcyl(xr - 16, xr + 1, *ax, PIN_D / 2)                      # pasador
neck_c -= box(xr - 9 - 1.7, AX1[0] - 3.6, AX1[1] - NT2 / 2 - 1, xr - 9 + 1.7, AX1[0] + 3.6, AX1[1] + 4.1)   # tuerca M4, desde abajo
neck_c -= box(xr - 9 - 1.7, H2C_Y - 3.6, H2C_Z - 3.6, xr - 9 + 1.7, H2C_Y + NT2 / 2 + 1, H2C_Z + 3.6)       # tuerca M4, desde atrás
# La boca de la ranura de H1 es más ancha que la punta redonda del cuello: sin este rebaje, su techo terminaba en una lengua al aire
neck_c -= box(xr - 9 + 1.69, AX1[0] - 3.6, AX1[1] - NT2 / 2 - 1, xr + 1, AX1[0] + 3.6, AX1[1] - math.sqrt((NT2 / 2) ** 2 - 3.6 ** 2) + 0.2)
for ax in (AX1, H2C):                                 # piel de 0.2 mm sobre cada ranura de tuerca: su techo sale como un puente entero
    neck_c += xcyl(xr - 9 + 1.7, xr - 9 + 1.9, *ax, PIN_D / 2 + 0.2)   # (de costado, el paso del pasador lo partía en dos voladizos); el tornillo la perfora
for p, q in ((AX1, KNEE), (KNEE, H2C)):                                   # canal de los cables
    ang_ = math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))
    neck_c -= Pos(xl + 9, (p[0] + q[0]) / 2, (p[1] + q[1]) / 2) * Rot(ang_ - 90, 0, 0) * Cylinder(CABLE_D / 2, math.dist(p, q))
neck_c -= Pos(xl + 9, *KNEE) * Sphere(CABLE_D / 2)
for ax in (AX1, H2C):                                 # cámara donde el haz sale del niple y dobla hacia el canal
    neck_c -= Pos(xl + 9, *ax) * Sphere(NIP_TAP / 2)
neck_c -= Pos(xl + 9, KNEE[0] + NT2 / 2, KNEE[1] - NT2 / 2) * Rot(45, 0, 0) * Cylinder(CABLE_D / 2, NT2 * 1.5)   # paso del codo
def neck_at(t):
    return neck_c.rotate(Axis((0, AX1[0], AX1[1]), (1, 0, 0)), pose(t)[0])
check((NT2 - CABLE_D) / 2 >= 3.0 and 9 - CABLE_D / 2 >= 3.0, f"el canal de Ø{CABLE_D:.0f} deja {(NT2 - CABLE_D) / 2:.1f} mm de pared arriba y abajo y {9 - CABLE_D / 2:.1f} al costado del cuello")
# 14 hilos por el canal del cuello y por el niple
wires_a = N_WIRES * math.pi * WIRE_D ** 2 / 4
for what, bore in (("el canal del cuello", CABLE_D), ("el niple M10 x 1", NIP_ID)):
    fill = wires_a / (math.pi * bore ** 2 / 4)
    check(fill <= 0.40 and WIRE_D * PACK[N_WIRES] <= bore - 1.5,
          f"{N_WIRES} hilos de Ø{WIRE_D} (AWG 30 de silicona) pasan por {what}: haz de Ø{WIRE_D * PACK[N_WIRES]:.1f} en Ø{bore:.1f}, {fill:.0%} de la sección")

# ---------- H: tecla de hablar (●) sobre SW1 ----------
# Blanca, de Ø16 y con el ● grabado. Maciza: su cara de abajo aprieta SW1. Entra por abajo antes que la placa.
#   - guía: el agujero de la tapa y el collar, a lo largo de toda la tecla;
#   - tope de arriba: dos orejas a 45° que asientan en la tapa; también impiden que gire y que la arranquen;
#   - tope de abajo: dos pies que apoyan en la placa TALK_STOP después de tocar SW1.
# Se imprime con la cara de arriba sobre la cama: las orejas crecen a 45° y los pies quedan arriba.
h = cyl(*TALK_C, Z_PUCK, H + CAP_UP, TALK_R)
h = chamfer(h.edges().group_by(Axis.Z)[-1], 0.5)
for th_ in LUG_ANG:
    h += lug(th_, 0)
for kx, ky in TALK_FEET:
    h += cyl(*k(kx, ky), Z_FACE + PUSH_GAP + TALK_STOP, Z_PUCK + 0.01, FOOT_R)
h -= Pos(0, 0, H + CAP_UP - 0.4) * extrude(Pos(*TALK_C) * Circle(3.2), amount=0.41)
ecc = math.dist(TALK_C, SW1C)
check(ecc + 1.5 <= TALK_R - 1.0, f"tecla ●: SW1 queda bajo la tecla, a {ecc:.1f} mm de su centro (radio {TALK_R:.0f})")
gap_sw = Z_PUCK - (Z_FACE + (sw1[1][5] if sw1 else 0))
check(0.1 <= gap_sw <= 0.3, f"tecla ●: en reposo queda a {gap_sw:.2f} mm de SW1 (STEP)")
near_key = Compound([s for s, kb in BRD if s is not SUBSTRATE and (sw1 is None or s is not sw1[0])
                     and math.hypot(max(kb[0] - TALK_K[0], 0, TALK_K[0] - kb[1]), max(kb[2] - TALK_K[1], 0, TALK_K[1] - kb[3])) < TALK_R + 3])
check(ivol(Pos(0, 0, 0.6) * h, a) > 0.5, "tecla ●: tope de arriba, tirada hacia afuera sus orejas chocan con la tapa")
press = Pos(0, 0, -(PUSH_GAP + BTN_TRAVEL + 0.1)) * h
v_a, v_n, v_s, v_b = ivol(press, a), ivol(press, near_key), ivol(press, sw1[0]) if sw1 else 0.0, ivol(press, SUBSTRATE)
check(v_a < 0.05 and v_n < 0.01 and v_b < 0.01 and v_s > 0.5,
      f"tecla ●: hace el recorrido de SW1 ({BTN_TRAVEL} mm, más 0.1) sin rozar la tapa, la placa ni otra pieza ({v_a:.2f} / {v_b:.2f} / {v_n:.2f} mm³)")
stop = Pos(0, 0, -(PUSH_GAP + TALK_STOP + 0.2)) * h
check(ivol(stop, SUBSTRATE) > 0.3 and ivol(stop, near_key) < 0.01 and ivol(stop, a) < 0.05,
      f"tecla ●: tope de abajo, los pies apoyan en placa libre {TALK_STOP} mm después de tocar SW1 y nada más toca")
check(TALK_STOP >= BTN_TRAVEL + 0.2, f"tecla ●: el tope de abajo deja {TALK_STOP - BTN_TRAVEL:.2f} mm tras el clic: con tolerancias, SW1 siempre llega a cerrar")
GUIDE_L = H - Z_PUCK
check(GUIDE_L >= 4.0 and Z_IN - Z_PUCK > PUSH_GAP + TALK_STOP + 0.5,
      f"tecla ●: guía de {GUIDE_L:.1f} mm (tapa + collar); las orejas no salen de sus ranuras en todo el recorrido")
check(H + CAP_UP + 0.5 < H + GAP_C, "cerrada, la tecla ● no toca el marco")

# ---------- E: marco (coordenadas del marco) ----------
e0 = Pos(0, FH / 2, -FD) * extrude(RectangleRounded(FW, FH, R_FRAME), amount=FD)
e = fillet(e0.edges().group_by(Axis.Z)[-1], 1.5)
# El frente va sobre la cama: faceta de 45° en la mitad de abajo del redondeo, como en la base
e += chamfer(e0.edges().group_by(Axis.Z)[-1], facet(1.5)) & box(-FW, -1, -1.5 * (1 - math.cos(math.radians(45))) - 0.05, FW, FH + 1, 1)
e = chamfer(e.edges().group_by(Axis.Z)[0], 1.0)      # canto de atrás: cerrada es el canto de arriba del bloque
e -= Pos(0, FH / 2, -FD - 1) * extrude(RectangleRounded(FW - 2 * FWALL, FH - 2 * FWALL, R_FRAME - FWALL), amount=FD + 1 - FFRONT)
PY0 = FB_BOT                                          # borde de abajo del panel
AAY1 = PY0 + AA_TOP + AA_H                           # borde de arriba del área activa (panel girado)
e -= box(-AA_W / 2 - 0.5, AAY1 - AA_H - 0.5, -FFRONT - 1, AA_W / 2 + 0.5, AAY1 + 0.5, 1)   # ventana
e -= Pos(0, AAY1 - AA_H / 2, -1.2) * extrude(Rectangle(AA_W + 1, AA_H + 1), amount=1.21, taper=-45)   # chaflán de 45°: el bisel se ve más fino
ZPF = -FFRONT - LENS_T - GASKET                       # cara del frente del panel, detrás del lente (si va) y la junta
zp = ZPF - PT - (FOAM - FOAM_SQ)                      # fondo de las guías y punta de las costillas de F: aprietan la espuma FOAM_SQ
X_DISP = TAIL_END * (PW / 2 - TAIL_DISP)              # centro de cada cola, en x del marco
X_TOUCH = TAIL_END * (PW / 2 - TAIL_TOUCH)
TAIL_GAPS = [(X_DISP, TAIL_DISP_W / 2 + TAIL_AIR), (X_TOUCH, TAIL_TOUCH_W / 2 + TAIL_AIR)]
# El panel flota entre espumas: el bisel (o el lente) adelante, la junta, el panel, la espuma y las costillas de F.
soft, rigid = GASKET + FOAM, LENS_T + PT
room = -FFRONT - zp                                   # del bisel a las costillas
check(abs(room - rigid - soft + FOAM_SQ) < 1e-6 and 0.05 <= FOAM_SQ / soft <= 0.25,
      f"panel de {PT} mm{' con lente' if LENTE else ' sin lente'}: entre el bisel y las costillas hay {room:.2f} mm para {rigid:.2f} de rígido y "
      f"{soft:.1f} de espuma, apretada {FOAM_SQ / soft:.0%}: sujeto sin aplastarlo")
ov_ = min((PW - AA_W - 1) / 2, AA_TOP - 0.5, PH - AA_TOP - AA_H - 0.5)
check(ov_ >= 2.5 and FFRONT - 1.2 >= 0.8, f"el bisel pisa el panel {ov_:.1f} mm o más en cada borde, con un labio recto de {FFRONT - 1.2:.1f} mm: lo retiene con o sin lente")
check(min(FWALL, FFRONT, F_T) >= PRINT_WALL, f"paredes del marco: {FWALL} / {FFRONT} / {F_T} mm, todas de {PRINT_WALL} mm o más")
for sgn in (-1, 1):                                   # guías del panel; arriba un hueco para el FPC, abajo la bisagra
    gx0, gx1 = sorted((sgn * (PW / 2 + GAP), sgn * (PW / 2 + GAP + 1.2)))
    e += box(gx0, PY0 + 10, zp, gx1, PY0 + PH - 10, -FFRONT + 0.01)
for x0, x1 in segments(-PW / 2 + 10, PW / 2 - 10, TAIL_GAPS):      # arriba, con un hueco para cada cola
    e += box(x0, PY0 + PH + GAP, zp, x1, PY0 + PH + GAP + 1.2, -FFRONT + 0.01)
for x0, x1 in ((-PW / 2 + 5, -(NW2 / 2 + WASH + BLOCK_T + 1)), (NW2 / 2 + WASH + BLOCK_T + 1, PW / 2 - 5)):
    e += box(x0, PY0 - GAP - 1.2, zp, x1, PY0 - GAP, -FFRONT + 0.01)
# Tornillos del marco desde el frente, bajo los 4 topes de goma: la espalda del marco (la cara de arriba cuando está
# cerrada) queda lisa. M3 x 12 avellanado, por el bisel y un refuerzo, a una torre de F.
BUMPERS = [(sx * (FW / 2 - 6.5), y) for sx in (-1, 1) for y in (10, FH - 10)]   # 3.5 mm más afuera que en la v1: dejan angostar el bisel   # topes de goma transparente Ø8 x 2.5 en el bisel
E_SCREWS = BUMPERS
E_BOSS = -FFRONT - 2.5                                # fondo del refuerzo del avellanado
BUMP_REC = 1.0                                        # los topes van 1 mm hundidos en el bisel
for x, y in E_SCREWS:
    e += cyl(x, y, E_BOSS, -FFRONT + 0.01, 3.5)
    e -= cyl(x, y, E_BOSS - 0.1, 1, 1.7)
    e -= cyl(x, y, -BUMP_REC, 1, 4.2)                 # cajuela del tope: hundido, no se despega con la uña
    e -= Pos(x, y, -BUMP_REC - 0.85) * Cone(1.7, 3.4, 1.7)   # avellanado a 90° desde el frente
    e += cyl(x, y, -BUMP_REC - 0.2, -BUMP_REC, 4.2)      # piel de 0.2 mm: el piso de la cajuela sale como un puente entero
# Logo al frente, centrado en el bisel de arriba: con la pantalla abierta sale en cada foto y en cada video
LOGO_Y = (AAY1 + 0.5 + 1.2 + FH - 1.5) / 2           # entre el chaflán de la ventana y el redondeo del borde
LOGO_H = (FH - 1.5 - 1.0) - (AAY1 + 0.5 + 1.2 + 1.0) - 0.4   # todo el alto del bisel, con 1.2 mm de aire arriba y abajo
logo_front = extrude(Plane(origin=(0, LOGO_Y, 0), x_dir=(1, 0, 0), z_dir=(0, 0, 1)) * aule_logo(LOGO_H), amount=-0.5)
e -= logo_front
lb_ = logo_front.bounding_box()
check(lb_.min.Y > AAY1 + 0.5 + 1.2 + 1.0 and lb_.max.Y < FH - 1.5 - 1.0 and lb_.max.X < FW / 2 - 20,
      f"el logo del frente cabe en el bisel de arriba ({lb_.size.X:.0f} x {lb_.size.Y:.1f} mm)")
check(2 * AULE_HW / (AULE_BOX[3] - AULE_BOX[1]) * LOGO_H >= 0.8,
      f"el trazo del logo del frente sale con dos líneas de boquilla 0.4 ({2 * AULE_HW / (AULE_BOX[3] - AULE_BOX[1]) * LOGO_H:.2f} mm)")
check(all(abs(x) - 3.5 > PW / 2 + GAP or y + 3.5 < PY0 - GAP or y - 3.5 > PY0 + PH + GAP for x, y in E_SCREWS),
      "las torres del marco quedan fuera del panel")      # las guías las controla el cruce de E con F
# Bisagra de arriba escondida: un hueco en el centro del bisel de abajo, del ancho del cuello y de todo el espesor del
# marco (cerrada, el cuello entra por el frente; al girar pasa por abajo; abierta sale por atrás, como en el render).
# A cada lado un bloque macizo dentro del marco: a la izquierda el niple, roscado en el cuello y sin tuerca (por
# adentro siguen los cables hasta el driver); a la derecha un tornillo M4 de acero con arandela de presión y tuerca,
# que da la fricción.
for sgn in (-1, 1):
    bx_0, bx_1 = sorted((sgn * (NW2 / 2 + WASH), sgn * (NW2 / 2 + WASH + BLOCK_T)))
    e += box(bx_0, 0, -FD + F_T + 0.5, bx_1, NOTCH_Y, -FFRONT + 0.01)
NOTCH = box(-(NW2 / 2 + WASH), -1, -FD - 1, NW2 / 2 + WASH, NOTCH_Y, 1)
e -= NOTCH
e -= xcyl(-(NW2 / 2 + WASH + BLOCK_T + 1), -(NW2 / 2 + WASH) + 0.01, Y_A, Z_A, NIP_D / 2)   # paso del niple
e -= xcyl(NW2 / 2 + WASH - 0.01, NW2 / 2 + WASH + BLOCK_T + 1, Y_A, Z_A, PIN_D / 2)       # pasador
nip2_loc = (xcyl(-(NW2 / 2 + WASH + BLOCK_T + 8), -(NW2 / 2 + WASH + BLOCK_T), Y_A, Z_A, 5.0)      # punta del niple
            + xcyl(NW2 / 2 + WASH + BLOCK_T, NW2 / 2 + WASH + BLOCK_T + 7, Y_A, Z_A, 3.6))      # cabeza y arandela del M4
check(NOTCH_Y <= PY0 - GAP - 1.2 and Z_A + KNUCKLE_R <= 0 and Z_A - KNUCKLE_R >= -FD,
      "la punta del cuello cabe en el hueco: bajo el panel y dentro del espesor del marco")
psi_o, h2_o, _ = pose(1)

# ---------- F: tapa del marco ----------
f_ = Pos(0, FH / 2, -FD) * extrude(RectangleRounded(FW - 2 * FWALL - 2 * CLR, FH - 2 * FWALL - 2 * CLR, R_FRAME - FWALL - CLR), amount=F_T)
for x, y in E_SCREWS:
    f_ += cyl(x, y, -FD + F_T - 0.01, E_BOSS - 0.2, 3.5)
    f_ -= cyl(x, y, -FD + F_T + 1, E_BOSS, 1.3)           # piloto M3 autorroscante
# Logo grabado en la espalda, derecho para quien mira la pantalla abierta desde atrás (como en una laptop)
f_ -= extrude(Plane(origin=(0, FH / 2 + 4, -FD), x_dir=(-1, 0, 0), z_dir=(0, 0, -1)) * aule_logo(20), amount=-0.6)
CAB_X = -58.0                                         # el haz sube por aquí, entre el panel y F
ribs = [(x0, PY0 + 2, x1, PY0 + 3.2) for x0, x1 in segments(-PW / 2 + 3, PW / 2 - 3, [(CAB_X, 4.0)])]
ribs += [(x0, PY0 + PH - 3.2, x1, PY0 + PH - 2) for x0, x1 in segments(-PW / 2 + 3, PW / 2 - 3, TAIL_GAPS)]
ribs += [(-PW / 2 + 2, PY0 + 8, -PW / 2 + 3.2, PY0 + PH - 8), (PW / 2 - 3.2, PY0 + 8, PW / 2 - 2, PY0 + PH - 8)]
for x0, y0, x1, y1 in ribs:
    f_ += box(x0, y0, -FD + F_T - 0.01, x1, y1, zp)   # costillas que aprietan el panel contra el bisel
f_ -= NOTCH
E_OUT = Pos(0, FH / 2, -FD) * extrude(RectangleRounded(FW, FH, R_FRAME), amount=FD)
check((f_ - E_OUT).volume < 0.01, "F queda dentro del contorno del marco")
z0_, z1_ = -FD + 1.5, -FFRONT - 0.5                   # entre el chaflán de atrás y el redondeo del frente
ring = (Pos(0, FH / 2, z0_) * extrude(RectangleRounded(FW - 0.2, FH - 0.2, R_FRAME - 0.1), amount=z1_ - z0_)
        - Pos(0, FH / 2, z0_ - 1) * extrude(RectangleRounded(FW - 2 * FWALL + 0.2, FH - 2 * FWALL + 0.2, R_FRAME - FWALL + 0.1), amount=z1_ - z0_ + 2))
corners = Compound([box(x0_, y0, -FD, x0_ + R_FRAME, y0 + R_FRAME, 0) for x0_ in (-FW / 2, FW / 2 - R_FRAME) for y0 in (0, FH - R_FRAME)])
check((ring & corners).volume > 0 and ((ring & corners) - e).volume < 0.01, "las esquinas del marco tienen la pared completa")
# Detrás del panel: el driver de pie bajo la cola de 24 pines y el adaptador del táctil bajo la suya, los dos con su
# conector hacia arriba, a 4 mm del borde del panel.
ZB = ZPF - PT - 0.5                                   # 0.5 mm detrás del panel
Y_TOP = PY0 + PH - 4
drv_x = X_DISP - DRV_FPC_OFF
driver_loc = box(drv_x - DRIVER[0] / 2, Y_TOP - DRIVER[1], ZB - DRIVER[2], drv_x + DRIVER[0] / 2, Y_TOP, ZB)
check(ZB - DRIVER[2] > -FD + F_T + 0.3, f"el driver del panel cabe entre el panel y la tapa F ({ZB - DRIVER[2] + FD - F_T:.1f} mm de sobra)")
# El adaptador del táctil va bajo su cola; si eso lo mete en el driver, se corre hacia el extremo del panel
ad_x = X_TOUCH
if abs(ad_x - drv_x) < DRIVER[0] / 2 + TOUCH_AD[0] / 2 + 2:
    ad_x = drv_x + TAIL_END * (DRIVER[0] / 2 + TOUCH_AD[0] / 2 + 2)
touch_ad_loc = box(ad_x - TOUCH_AD[0] / 2, Y_TOP - TOUCH_AD[1], ZB - TOUCH_AD[2], ad_x + TOUCH_AD[0] / 2, Y_TOP, ZB)
check(abs(ad_x - X_TOUCH) <= 5.0 and abs(ad_x) + TOUCH_AD[0] / 2 <= PW / 2 - 4,
      f"el adaptador del táctil cabe junto al driver, a {abs(ad_x - X_TOUCH):.1f} mm de su cola y a {abs(ad_x - drv_x) - DRIVER[0] / 2 - TOUCH_AD[0] / 2:.1f} mm del driver")
check(abs(X_DISP - X_TOUCH) >= (TAIL_DISP_W + TAIL_TOUCH_W) / 2 + 2, f"las dos colas no se pisan: {abs(X_DISP - X_TOUCH):.0f} mm entre centros")
panel_loc = box(-PW / 2, PY0, ZPF - PT, PW / 2, PY0 + PH, ZPF)
lens_loc = box(-PW / 2, PY0, -FFRONT - 1.0, PW / 2, PY0 + PH, -FFRONT)      # entra en las mismas guías que el panel (solo con LENTE)
bumpers = Compound([cyl(x, y, -BUMP_REC, GAP_C, 4.0) for x, y in BUMPERS])
feet = Compound([cyl(x, y, -2.0, FOOT_REC, 6.0) for x, y in BOSSES[:4]])   # patas de Ø12 x 3 sobre los tornillos de las esquinas

# ---------- N: placa del nombre ----------
# Blanca, a ras del frente, con el nombre en letras negras de 0.5 mm de relieve: se imprime boca arriba con cambio de
# filamento al empezar las letras y se pega con cinta VHB. Mide más de 57 mm: no entra en el cilindro de piezas
# chicas aunque se despegue. Otro nombre: --nombre=Valentina
plate = extrude(NAME_PL * SlotOverall(NAME_W, NAME_H), amount=NAME_D) & name_wedge(SPK_Z - NAME_H / 2 + CLR * (math.sqrt(2) - 1))
fs_ = 8.5
bb_n = text2d(NOMBRE, fs_).bounding_box()
fs_ = min(fs_, fs_ * (NAME_W - 14) / bb_n.size.X, fs_ * (NAME_H - 4) / bb_n.size.Y)
letters = extrude(Plane(origin=(W / 2, 0, SPK_Z), x_dir=(1, 0, 0), z_dir=(0, -1, 0)) * text2d(NOMBRE, fs_), amount=NAME_UP)
bb_n = letters.bounding_box()
check(fs_ >= 5.0 and bb_n.size.X <= NAME_W - 13.9 and bb_n.size.Z <= NAME_H - 3.9,
      f"«{NOMBRE}» cabe en la placa del nombre con letra de {fs_:.1f} mm")
check(NAME_W > 57.1, "la placa del nombre es más larga que el cilindro de piezas chicas (57.1 mm)")
nameplate = plate + letters

# ---------- Control de calce ----------
J6_AD_X1 = BX0 + BH - 0.5                             # el adaptador de J6 va en el piso, bajo el borde de la placa
j6x, j6y = k(*J6)
obstacles = {
    "batería": box(bx0, by0, FLOOR, bx1, by1, FLOOR + BATT[2]),
    "lastre": ballast[0] + ballast[1],
    "parlante izquierdo": ycyl(SPK_X[0], SPK_Z, SPK_Y0, SPK_Y0 + SPK_T, SPK_D / 2),
    "parlante derecho": ycyl(SPK_X[1], SPK_Z, SPK_Y0, SPK_Y0 + SPK_T, SPK_D / 2),
    "niple y tuerca de H1": xcyl(xl - WASH - TW - 6 - 12, xl - WASH - TW - 6, *AX1, NUT_R),   # tuerca moleteada Ø14
    "adaptador de J5": box(BX0 + 14, Y_BRD + 2, FLOOR + 0.5, BX0 + 14 + J5_ADAPTER[0], Y_BRD + 2 + J5_ADAPTER[1], FLOOR + 0.5 + J5_ADAPTER[2]),
    "adaptador de J6": box(J6_AD_X1 - J6_ADAPTER[0], j6y - J6_ADAPTER[1] / 2, FLOOR + 0.5, J6_AD_X1, j6y + J6_ADAPTER[1] / 2, FLOOR + 0.5 + J6_ADAPTER[2]),
}
check(ivol(obstacles["adaptador de J5"], obstacles["adaptador de J6"]) < 0.01, "los dos adaptadores caben en el piso sin pisarse")
# El modelo de SS12D00G6 que trae la placa es una caja maciza de 8.5 x 3.5 x 8.5 mm: se cambia por la forma real,
# cuerpo de 3.5 mm y la palanca barriendo su recorrido.
solids = [s for s, kb in BRD if not is_slide(kb)]
check(len(BRD) - len(solids) == len(SLIDES), "los dos interruptores deslizantes se cambiaron por su forma real")
obstacles["placa y componentes"] = Compound(solids)
_, uy = k(USB, 0)
uz = Z_FACE + 1.63
usb = [s for s in solids if s.bounding_box().size.X > 6 and abs(s.center().Y - uy) < 2 and s.bounding_box().max.X > BX0 + BH - 3]
check(bool(usb) and all(abs((s.bounding_box().min.Z + s.bounding_box().max.Z) / 2 - uz) < 0.8 for s in usb),
      "el túnel USB queda a la altura del receptáculo")
for name, ((kx, ky), axis) in SLIDES.items():
    x, y = k(kx, ky)
    sw_ = SLIDE_LEVER + SLIDE_TRAVEL
    bl, bw, hl, hw = (3.5, 8.5, SLIDE_LEVER, sw_) if axis == "x" else (8.5, 3.5, sw_, SLIDE_LEVER)   # (x, y)
    obstacles[f"interruptor {name}"] = (box(x - bl / 2, y - bw / 2, Z_FACE, x + bl / 2, y + bw / 2, Z_FACE + SLIDE_BODY)
                                        + box(x - hl / 2, y - hw / 2, Z_FACE + SLIDE_BODY, x + hl / 2, y + hw / 2, Z_FACE + SLIDE_TOP))

tick("piezas listas")
# ---------- Cables ----------
# Todos como tubos por su recorrido, con curvas de 3 a 4 mm. Los que cruzan una bisagra se parten en el eje: el tramo
# de la base termina en la punta del niple de H1, el del cuello va por dentro de los dos niples y el canal, y el del
# marco empieza en la punta del niple de H2. Como cada unión cae sobre un eje, el cable solo se tuerce al plegar.
CAB_R, PAIR_R = 1.6, 1.2              # MEDIR: haz de 8 cables de silicona de 30 AWG; par de 24 a 26 AWG
def route(points, bend):                              # recorrido de rectas y arcos tangentes de radio `bend`
    P = [Vector(*p_) for p_ in points]
    edges, start = [], P[0]
    for i in range(1, len(P) - 1):
        pa, pb, pc = P[i - 1], P[i], P[i + 1]
        u, v = (pa - pb).normalized(), (pc - pb).normalized()
        phi = math.acos(max(-1.0, min(1.0, u.dot(v))))
        if phi > math.radians(178):
            continue
        dd = min(bend / math.tan(phi / 2), (pb - pa).length / 2, (pc - pb).length / 2)
        rho = dd * math.tan(phi / 2)
        q0, q2 = pb + u * dd, pb + v * dd
        if (q0 - start).length > 1e-3:
            edges.append(Edge.make_line(start, q0))
        edges.append(Edge.make_three_point_arc(q0, pb + (u + v).normalized() * (rho / math.sin(phi / 2) - rho), q2))
        start = q2
    edges.append(Edge.make_line(start, P[-1]))
    return Wire(edges)
def cable(points, r, bend=4.0):
    w_ = route(points, bend)
    return sweep(Plane(origin=points[0], z_dir=w_.tangent_at(0)) * Circle(r), path=w_), w_.length
def ribbon(points, wd, t, bend=2.0, wdir=(1, 0, 0)):  # cinta FPC: su ancho va a lo largo de wdir
    w_ = route(points, bend)
    return sweep(Plane(origin=points[0], x_dir=wdir, z_dir=w_.tangent_at(0)) * Rectangle(wd, t), path=w_), w_.length
j5x = BX0 + 14 + J5_ADAPTER[0] / 2                    # J5 y el adaptador quedan en la misma x
check(abs(j5x - k(*J5)[0]) < 0.5, "el adaptador de 24 pines queda alineado bajo J5")
JST = {"J2": 103.85, "J3": 96.75}                      # y de los receptáculos JST PH (centro, del STEP de la placa)
Z_JST = Z_FACE + 2.45
CAB14_R, CAB8_R, CAB6_R, PAIR_R = bundle_r(14), bundle_r(8), bundle_r(6), 1.2   # haces de 14, 8 y 6 hilos; par de 24 a 26 AWG
lengths = {}
fpc_j5, lengths["cinta corta de J5"] = ribbon([(j5x, 23.3, 28.5), (j5x, 19.5, 28.5), (j5x, 16.5, 24.0), (j5x, 19.0, 18.0),
                                               (j5x, 22.5, 6.0), (j5x, Y_BRD + 2 - 0.05, 5.0)], 13.0, 0.2)
# Cinta corta de J6: sale hacia la pared derecha, da la vuelta en el espacio de los JST y vuelve por abajo de la placa
X_MOUTH, X_LOOP, AD_Z = BX0 + J6_MOUTH, W - WALL - J6_LOOP, FLOOR + 0.5 + J6_ADAPTER[2] / 2
J6_BEND = 2.5
ffc_j6, lengths["cinta corta de J6"] = ribbon([(X_MOUTH + 0.1, j6y, Z_FACE + 0.9), (X_LOOP, j6y, Z_FACE + 0.9), (X_LOOP, j6y, AD_Z),
                                               (J6_AD_X1 + 0.05, j6y, AD_Z)], TAIL_TOUCH_W, 0.2, J6_BEND, wdir=(0, 1, 0))
check(X_LOOP - X_MOUTH >= J6_BEND + 1.5 and J6_LOOP - 0.1 >= 2 * PAIR_R + 1.5,
      f"la cinta de J6 tiene {X_LOOP - X_MOUTH:.1f} mm para dar la vuelta con radio {J6_BEND} y deja {J6_LOOP - 0.1:.1f} mm contra la pared para el cable de los parlantes")
# Haces de la base: 8 hilos del adaptador de J5 y 6 del de J6 se juntan y van como uno de 14 hasta el niple de H1
JN = (BX0 + 9.4, 50.0, 18.0)
NIP1_TIP = (xl - WASH - TW - 6 - 12, *AX1)
h8_base, lengths["8 hilos del panel, de J5 a la unión"] = cable([(j5x, Y_BRD + 2 + J5_ADAPTER[1] + 0.1, 5.0), (j5x, 46, 7), JN], CAB8_R)
h6_base, lengths["6 hilos del táctil, de J6 a la unión"] = cable([(J6_AD_X1 - J6_ADAPTER[0] / 2, j6y + J6_ADAPTER[1] / 2 + 0.1, AD_Z),
                                                                  (J6_AD_X1 - J6_ADAPTER[0] / 2, 45, 7), (BX0 + 25.4, 50, 14), JN], CAB6_R)
trunk_base, lengths["haz de 14, base"] = cable([JN, (NIP1_TIP[0] + 21.5, 50, 19.5), (NIP1_TIP[0] + 5.5, 52, 21), (NIP1_TIP[0] - 6.5, 62, 25),
                                                (NIP1_TIP[0] - 6, AX1[0] - 3.5, AX1[1]), (NIP1_TIP[0] - 3.5, *AX1), NIP1_TIP], CAB14_R)
CHX = xl + 9                                          # canal del cuello
NIP2_TIP = (-(NW2 / 2 + WASH + BLOCK_T + 8), Y_A, Z_A)
neck_cable, lengths["haz de 14, cuello"] = cable([NIP1_TIP, (CHX, *AX1), (CHX, *KNEE), (CHX, *H2C), (W / 2 + NIP2_TIP[0], *H2C)], CAB14_R, 3.0)
# En el marco: el haz sube por la izquierda y se abre en 8 hilos al driver (por abajo) y 6 al adaptador del táctil
drv_mid, ad_mid = ZB - DRIVER[2] / 2, ZB - TOUCH_AD[2] / 2
SPLIT = (CAB_X, 50.0, -11.0)
trunk_frame, lengths["haz de 14, marco"] = cable([NIP2_TIP, (-56, Y_A, Z_A), (CAB_X, Y_A + 8, -11), SPLIT], CAB14_R)
yd0, ya0 = Y_TOP - DRIVER[1] - 0.05, Y_TOP - TOUCH_AD[1] - 0.05
if TAIL_END < 0:
    pts8 = [SPLIT, (CAB_X + 6, 55, -10.5), (drv_x, 57, drv_mid), (drv_x, yd0, drv_mid)]
    pts6 = [SPLIT, (CAB_X - 3, 58, -11), (ad_x, 68, -11), (ad_x, 108, -9), (ad_x, ya0, ad_mid)]
else:
    pts8 = [SPLIT, (CAB_X + 8, 55, -10.5), (drv_x - 8, 55, -10.5), (drv_x, 58, drv_mid), (drv_x, yd0, drv_mid)]
    pts6 = [SPLIT, (CAB_X + 8, 52, -11.5), (ad_x - 8, 52, -11.5), (ad_x, 60, -11), (ad_x, 108, -9), (ad_x, ya0, ad_mid)]
h8_frame, lengths["8 hilos del panel, al driver"] = cable(pts8, CAB8_R)
h6_frame, lengths["6 hilos del táctil, al adaptador del marco"] = cable(pts6, CAB6_R)
# Las dos colas doblan sobre el borde de arriba del panel: la de 24 pines sale de atrás, la táctil del frente
yb = PY0 + PH
fpc_panel, lengths["cola de 24 pines"] = ribbon([(X_DISP, yb + 0.05, ZPF - PT + 0.15), (X_DISP, yb + 1.5, ZPF - PT + 0.15), (X_DISP, yb + 2.8, ZPF - PT - 1.6),
                                                 (X_DISP, yb + 1.5, drv_mid), (X_DISP, Y_TOP + 0.05, drv_mid)], TAIL_DISP_W, 0.2, 1.2)
fpc_touch, lengths["cola táctil de 6 pines"] = ribbon([(X_TOUCH, yb + 0.05, ZPF - 0.3), (X_TOUCH, yb + 3.2, ZPF - 0.3), (X_TOUCH, yb + 3.2, ad_mid),
                                                       (X_TOUCH, Y_TOP + 0.05, ad_mid)], TAIL_TOUCH_W, 0.2, 1.8)
check(FB_TOP - FWALL - 3.3 >= 1.0, f"sobre el borde del panel hay {FB_TOP - FWALL:.1f} mm para el doblez de las colas (usan 3.3)")
frame_cables = trunk_frame + h8_frame + h6_frame + fpc_panel + fpc_touch
batt_cable, lengths["batería a J2"] = cable([(48, by1 + 0.05, FLOOR + 5), (48, 128.5, FLOOR + 3), (W - 24, 128.5, FLOOR + 3), (W - 6.5, 121, FLOOR + 5),
                                             (W - 6.5, 108, 20), (W - 6.5, JST["J2"], 27), (W - 6.5, JST["J2"], Z_JST), (BX0 + BH + 1.55, JST["J2"], Z_JST)], PAIR_R)
spk_a, lengths["parlante a parlante"] = cable([(SPK_X[0] + 11, SPK_Y0 + SPK_T + 0.55, SPK_Z), (SPK_X[0] + 13, 13.5, SPK_Z + 1),
                                               (SPK_X[1] - 13, 13.5, SPK_Z + 1), (SPK_X[1] - 12, SPK_Y0 + SPK_T + 0.55, SPK_Z)], PAIR_R)
X_SPK = W - WALL - PAIR_R - 0.5                       # pegado a la pared derecha: por fuera de la vuelta de la cinta de J6
spk_b, lengths["parlantes a J3"] = cable([(SPK_X[1] - 10, SPK_Y0 + SPK_T + 0.55, SPK_Z), (SPK_X[1] - 10, 13.5, SPK_Z - 1), (W - 15, 13.5, SPK_Z - 2),
                                          (X_SPK, 21, 14), (X_SPK, 62, 14), (W - 6.5, 70, 16), (W - 6.5, 92, 20), (W - 6.5, JST["J3"], 27), (W - 6.5, JST["J3"], Z_JST),
                                          (BX0 + BH + 1.55, JST["J3"], Z_JST)], PAIR_R)
plugs = Compound([box(BX0 + BH - 0.5, y - 2.9, Z_FACE + 0.1, BX0 + BH + 1.5, y + 2.9, Z_FACE + 4.7) for y in JST.values()])
base_cables = {"cinta corta de J5": fpc_j5, "cinta corta de J6": ffc_j6, "8 hilos del panel en la base": h8_base,
               "6 hilos del táctil en la base": h6_base, "haz de 14 en la base": trunk_base, "cable de la batería": batt_cable,
               "cables de los parlantes": spk_a + spk_b, "enchufes JST": plugs}
obstacles.update(base_cables)
# Los cables no pisan la placa, la batería, el lastre, los parlantes, los adaptadores, el panel ni el driver
solid_obs = {n_: o_ for n_, o_ in obstacles.items() if n_ not in base_cables}
tick("cables armados")
for cn, cb in base_cables.items():
    for on, ob in solid_obs.items():
        v = ivol(cb, ob)
        check(v < 1.0, f"{cn} no se mete en {on} ({v:.2f} mm³)")
        if not v < 1.0:
            for s in ob.solids():
                vs = ivol(cb, s)
                if vs > 0.05:
                    bb_ = (cb & s).bounding_box()
                    print(f"     {cn} choca {vs:.2f} mm³ en x {bb_.min.X:.1f}..{bb_.max.X:.1f}, y {bb_.min.Y:.1f}..{bb_.max.Y:.1f}, z {bb_.min.Z:.1f}..{bb_.max.Z:.1f}")
v = ivol(ffc_j6, spk_a + spk_b)
check(v < 0.01, f"la cinta de J6 y el cable de los parlantes no se cruzan en la bahía ({v:.2f} mm³)")
frame_obs = [("panel", panel_loc), ("driver", driver_loc), ("adaptador del táctil", touch_ad_loc), ("niple de H2", nip2_loc)] + ([("lente", lens_loc)] if LENTE else [])
for cn, cb in (("haz de 14 en el marco", trunk_frame), ("8 hilos al driver", h8_frame), ("6 hilos al adaptador del táctil", h6_frame),
               ("cola de 24 pines", fpc_panel), ("cola táctil", fpc_touch)):
    for on, ob in frame_obs:
        v = ivol(cb, ob)
        check(v < 1.0, f"{cn} no se mete en {on} ({v:.2f} mm³)")
check(ivol(driver_loc, touch_ad_loc) < 0.01, "el driver y el adaptador del táctil no se pisan")
check((neck_cable & neck_c).volume < 1.0, f"el haz de 14 va por dentro del canal del cuello ({(neck_cable & neck_c).volume:.2f} mm³)")
tick("cables controlados")

def report(p, q, inter):
    bb = inter.bounding_box()
    print(f"     choque {p}-{q} en x {bb.min.X:.1f}..{bb.max.X:.1f}, y {bb.min.Y:.1f}..{bb.max.Y:.1f}, z {bb.min.Z:.1f}..{bb.max.Z:.1f}")
MOVING_PARTS = ("C", "E", "F", "topes")
def moving_parts(t):
    loc = pose(t)[2]
    mp = {"C": neck_at(t), "E": loc * e, "F": loc * f_, "topes": loc * bumpers, "panel": loc * panel_loc,
          "driver": loc * driver_loc, "adaptador del táctil": loc * touch_ad_loc, "niple y tuerca de H2": loc * nip2_loc,
          "cables del marco": loc * frame_cables, "cable del cuello": neck_cable.rotate(Axis((0, AX1[0], AX1[1]), (1, 0, 0)), pose(t)[0])}
    if LENTE:
        mp["lente"] = loc * lens_loc
    return mp
fixed = {"A": a, "B": b, "H": h, "N": nameplate, "patas": feet}
for label, t in (("abierta", 1.0), ("cerrada", 0.0)):
    mv = moving_parts(t)
    parts = {**fixed, **{n_: mv[n_] for n_ in MOVING_PARTS}}
    obs = {**obstacles, **{n_: s_ for n_, s_ in mv.items() if n_ not in MOVING_PARTS}}
    for pname, part in parts.items():
        if label == "cerrada" and pname in fixed:
            continue                                   # lo fijo ya se controló con la base abierta
        for oname, ob in obs.items():
            v = ivol(part, ob)
            check(v < 1.0, f"{label}: {pname} no se mete en {oname} ({v:.2f} mm³)")
            if v >= 1.0 and oname.startswith("placa"):
                for s in ob.solids():
                    vs = (part & s).volume
                    if vs > 0.05:
                        cx, cy, cz = s.center()
                        print(f"     {pname} choca {vs:.2f} mm³ con un sólido en kx {cy - BY0:.1f}, ky {cx - BX0:.1f}")
    names = list(parts)
    for i, p in enumerate(names):
        for q in names[i + 1:]:
            if label == "cerrada" and p in fixed and q in fixed:
                continue
            inter = parts[p] & parts[q]
            check(inter.volume < 1.0, f"{label}: {p} y {q} no se interpenetran ({inter.volume:.2f} mm³)")
            if inter.volume >= 1.0:
                report(p, q, inter)
tick("abierta y cerrada controladas")
# Al plegarla, el cuello y el marco no rozan la base ni se rozan entre sí
for t in (0.2, 0.4, 0.6, 0.8):
    mv = moving_parts(t)
    for p in ("C", "E", "F", "topes"):
        for q, part in (("A", a), ("H", h)):
            inter = mv[p] & part
            check(inter.volume < 1.0, f"a mitad del giro ({t:.0%}): {p} no roza {q} ({inter.volume:.2f} mm³)")
            if inter.volume >= 1.0:
                report(p, q, inter)
    for p in ("E", "F"):
        inter = mv["C"] & mv[p]
        check(inter.volume < 1.0, f"a mitad del giro ({t:.0%}): el cuello no roza {p} ({inter.volume:.2f} mm³)")
        if inter.volume >= 1.0:
            report("C", p, inter)
# Cerrada: los topes del bisel apoyan sobre tapa lisa, y el marco no sale de la base
for x, y in BUMPERS:
    pt = fw(FRAME_CLOSED, x, y, 0)
    solid = (a & cyl(pt.X, pt.Y, H - 0.5, H, 4.0)).volume
    check(solid > 0.97 * math.pi * 16 * 0.5, f"cerrada, el tope del bisel en x {pt.X:.0f}, y {pt.Y:.0f} apoya sobre tapa lisa")
E_C = FRAME_CLOSED * e
bb = E_C.bounding_box()
check(bb.min.Y > -0.01 and bb.max.Y < D + 0.01 and bb.min.X > -0.01 and bb.max.X < W + 0.01,
      f"cerrada, el marco no sale de la base ({bb.size.X:.1f} x {bb.size.Y:.1f} sobre {W:.0f} x {D:.0f})")
closed_h = max(bb.max.Z, (FRAME_CLOSED * f_).bounding_box().max.Z)
E_O = FRAME_OPEN * e
z_frame = min(v.Z for v in E_O.vertices())
check(z_frame > H + 25, f"abierta, el marco queda {z_frame - H:.0f} mm sobre la base")

tick("giro controlado")
# ---------- Estabilidad sobre la mesa (abierta) ----------
# Piezas impresas en PETG macizo, acero 7.85 g/cm³ y el resto con las masas de MASS. Se vuelca hacia atrás si alguien
# empuja la pantalla; el pivote son las patas de atrás.
mv = moving_parts(1.0)
C_O, F_O = mv["C"], mv["F"]
masses = [(p.volume / 1000 * 1.27, p.center(CenterOf.MASS)) for p in (a, b, h, C_O, E_O, F_O)]
masses += [(LASTRE[0] * LASTRE[1] * LASTRE[2] / 1000 * 7.85, p.center(CenterOf.BOUNDING_BOX)) for p in ballast]
masses += [(MASS["panel"], mv["panel"].center(CenterOf.BOUNDING_BOX)), (MASS["driver"], mv["driver"].center(CenterOf.BOUNDING_BOX)),
           (MASS["batería"], obstacles["batería"].center(CenterOf.BOUNDING_BOX))]
masses += [(MASS["parlantes"] / 2, obstacles[s].center(CenterOf.BOUNDING_BOX)) for s in ("parlante izquierdo", "parlante derecho")]
if "placa y componentes" in obstacles:
    masses.append((MASS["placa y componentes"], obstacles["placa y componentes"].center(CenterOf.BOUNDING_BOX)))
M = sum(m for m, _ in masses)
com = (sum(m * v.Y for m, v in masses) / M, sum(m * v.Z for m, v in masses) / M)
aa_mid = fw(FRAME_OPEN, 0, AAY1 - AA_H / 2, 0)
top = fw(FRAME_OPEN, 0, FH, 0)
F_mid = M / 1000 * 9.81 * (D - FEET - com[0]) / aa_mid.Z
F_top = M / 1000 * 9.81 * (D - FEET - com[0]) / top.Z
F_fwd = M / 1000 * 9.81 * (com[0] - FEET) / top.Z
check(FEET + 20 < com[0] < D - FEET - 20, f"el centro de masa cae sobre la base (y {com[0]:.0f} entre patas en {FEET:.0f} y {D - FEET:.0f})")
check(F_mid > 3.0, f"empujar el centro de la pantalla hacia atrás necesita {F_mid:.1f} N para volcarla")
# ---------- Si alguien fuerza la pantalla más allá de abierta ----------
# Las bisagras son de fricción: si se fuerzan, patinan en vez de romperse. Esto mide cuánto pueden pasarse antes de
# que algo choque, que es donde frena.
def contact(movers, fixed_):
    return any((m_ & f_).volume > 1.0 for m_ in movers for f_ in fixed_)
ax_h1, ax_h2 = Axis((0, AX1[0], AX1[1]), (1, 0, 0)), Axis((0, h2_o[0], h2_o[1]), (1, 0, 0))
STEPS = (2, 4, 6, 8, 10, 15, 20, 30, 45, 60, 90)
over_h1 = next((dd for dd in STEPS if contact([neck_c.rotate(ax_h1, PSI + dd), E_O.rotate(ax_h1, dd), F_O.rotate(ax_h1, dd)], [a])), None)
check(over_h1 is not None and over_h1 <= 10, f"si se tira la pantalla hacia adelante, H1 frena antes de {over_h1}°")
over_h2 = next((dd for dd in STEPS if contact([E_O.rotate(ax_h2, -dd), F_O.rotate(ax_h2, -dd)], [C_O, a])), None)
tick("forzado medido")
# Torque que tienen que aguantar las bisagras: el peso, más 3 N empujando el centro de la pantalla hacia atrás
mf = (E_O.volume + F_O.volume) / 1000 * 1.27 + MASS["panel"] + MASS["driver"]
cf = sum(m * v.Y for m, v in masses if v.Z > H + 10 and m in (MASS["panel"], MASS["driver"])) / (MASS["panel"] + MASS["driver"])
T2 = mf / 1000 * 9.81 * (cf - h2_o[0]) / 1000
T2p = 3.0 * (aa_mid.Z - h2_o[1]) / 1000
T1 = 3.0 * (aa_mid.Z - AX1[1]) / 1000

# ---------- Orientación de impresión ----------
# Cada STL sale como va en la cama (z = 0). Los STEP salen en su lugar (A, B, C y H con la base cerrada; E y F planos).
PRINTS = {
    "A-base": (Pos(0, D, H) * Rot(180, 0, 0) * a, "tapa sobre la cama"),
    "B-fondo": (b, "plano, la cara de afuera sobre la cama"),
    "C-cuello": (Rot(0, -90, 0) * Pos(-xl, 0, 0) * neck_c, "de costado, la cara izquierda sobre la cama"),
    "E-marco": (Rot(0, 180, 0) * e, "cara del frente sobre la cama"),
    "F-tapa-marco": (Pos(0, 0, FD) * f_, "cara de atrás sobre la cama"),
    "H-tecla-hablar": (Pos(-TALK_C[0], TALK_C[1], H + CAP_UP) * Rot(180, 0, 0) * h, "cara de arriba sobre la cama"),
    "N-placa-nombre": (Pos(-W / 2, -SPK_Z, NAME_D) * Rot(-90, 0, 0) * nameplate, "boca arriba, la espalda sobre la cama"),
}
STEPS = {"A-base": a, "B-fondo": b, "C-cuello": neck_c, "E-marco": e, "F-tapa-marco": f_, "H-tecla-hablar": h, "N-placa-nombre": nameplate}
BED = 250.0                                           # cama de 256 mm de la Centauri Carbon, con 3 mm de margen por lado
for name, (shape, _) in PRINTS.items():
    bb = shape.bounding_box()
    check(bb.size.X <= BED and bb.size.Y <= BED and bb.size.Z <= BED and abs(bb.min.Z) < 0.02,
          f"{name} cabe en la cama: {bb.size.X:.0f} x {bb.size.Y:.0f} x {bb.size.Z:.0f} mm, apoyada en z = 0")

# ---------- Salida ----------
fails = [m for ok, m in checks if not ok]
for ok, m in checks:
    print(("ok   " if ok else "FALLA ") + m)
print(f"{len(checks) - len(fails)} de {len(checks)} controles pasan")
if fails:
    sys.exit(f"{len(fails)} comprobaciones fallaron")
OUT.mkdir(parents=True, exist_ok=True)
for name, (shape, how) in PRINTS.items():
    export_stl(shape, str(OUT / f"{name}.stl"))
    export_step(STEPS[name], str(OUT / f"{name}.step"))
import json
# Para printcheck.py y para el laminador: cómo va cada pieza y dónde se acepta soporte (en coordenadas de impresión).
# El único techo que no sale solo es el piso del bolsillo del cuello, de 62 mm de ancho: lleva soporte desde la cama.
px0, py0, px1, py1, pzf = POCKET[0]
(OUT / "impresion.json").write_text(json.dumps({"piezas": {n_: {"orientacion": how, "soporte": (
    [[px0 - 0.5, D - py1 - 0.5, px1 + 0.5, D - py0 + 0.5, H - pzf - 0.3, H - pzf + 0.3, "piso del bolsillo del cuello"]] if n_ == "A-base" else [])}
    for n_, (_, how) in PRINTS.items()}}, indent=1, ensure_ascii=False))
print(f"placa: {BOARD_STEP.name}")
print(f"configuración: {'con' if LENTE else 'SIN'} lente; colas del panel en el extremo {'izquierdo' if TAIL_END < 0 else 'derecho'}")
print(f"base {W:.0f} x {D:.0f} x {H:.0f} mm; marco {FW:.1f} x {FH:.1f} x {FD:.0f} mm")
print(f"abierta: alto {top.Z:.0f} mm, borde de abajo del marco en y {O_OPEN[0]:.0f}, z {O_OPEN[1]:.0f}; "
      f"cerrada: {W:.0f} x {D:.0f} x {closed_h:.0f} mm")
print(f"bisagras: H1 en y {AX1[0]:.1f}, z {AX1[1]:.1f}; cuello de {LN:.1f} mm entre ejes; H1 gira {PSI:.1f}° y H2 "
      f"{A_CLOSED - A_OPEN + PSI:.1f}°; H2 abierta en y {h2_o[0]:.1f}, z {h2_o[1]:.1f}")
print(f"torques: H2 sostiene {T2:.2f} N·m de peso y {T2p:.2f} N·m con 3 N en la pantalla; "
      f"H1 necesita {T1:.2f} N·m de fricción para que 3 N no la cierren")
print(f"si se fuerza: H1 se pasa hasta {over_h1}° antes de que el cuello toque la base; H2 se echa {over_h2}° más atrás antes de tocar el cuello o la base")
print("cables: " + ", ".join(f"{n_} {l_:.0f} mm" for n_, l_ in lengths.items()))
print(f"placa en x {BX0:.1f}..{BX0 + BH:.1f}, y {Y_BRD:.1f}..{Y_BRD + BW:.1f}, cara de componentes en z {Z_FACE:.1f}; "
      f"USB-C a {uy:.0f} mm del frente")
for name, part in STEPS.items():
    print(f"{name}: {part.volume / 1000:.1f} cm³ (~{part.volume / 1000 * 1.27:.0f} g de PETG macizo); se imprime {PRINTS[name][1]}")
print(f"masa total ~{M:.0f} g (lastre 2 x {LASTRE[0] * LASTRE[1] * LASTRE[2] / 1000 * 7.85:.0f} g); centro de masa en y {com[0]:.0f}, "
      f"z {com[1]:.0f}; se vuelca hacia atrás con {F_mid:.1f} N en el centro de la pantalla o {F_top:.1f} N arriba, "
      f"y hacia adelante con {F_fwd:.1f} N arriba")

# ---------- Escena para render.py: cada pieza en su lugar, abierta, como STL ----------
ESC = next((a_.split("=", 1)[1] for a_ in sys.argv if a_.startswith("--escena=")), None)
GLB = "--glb" in sys.argv
if ESC or GLB:
    import json
    mv = moving_parts(1.0)
    levers = Compound([obstacles[f"interruptor {n_}"] for n_ in SLIDES])
    nodes = {   # nombre: (sólido, color, grupo)
        "A": (a, "#26282c", "base"), "B": (b, "#26282c", "fondo"), "H": (h, "#f2f0ea", "tecla"),
        "N": (plate, "#f2f0ea", "nombre"), "letras": (letters, "#1f2124", "nombre"), "patas": (feet, "#3a3c40", "patas"),
        "placa": (obstacles["placa y componentes"], "#2f9d5f", "placa"), "palancas": (levers, "#d9d9d9", "placa"),
        "bateria": (obstacles["batería"], "#3b6fb6", "interior"), "lastre": (obstacles["lastre"], "#8d9096", "interior"),
        "parlantes": (obstacles["parlante izquierdo"] + obstacles["parlante derecho"], "#55595f", "interior"),
        "adaptador-J5": (obstacles["adaptador de J5"], "#7a3fb0", "interior"), "adaptador-J6": (obstacles["adaptador de J6"], "#b03f8c", "interior"),
        "cintas": (fpc_j5 + ffc_j6, "#e8a23a", "interior"), "haz-base": (h8_base + h6_base + trunk_base, "#e6e6e0", "interior"),
        "otros-cables": (batt_cable + spk_a + spk_b + plugs, "#c9453f", "interior"),
        "C": (mv["C"], "#26282c", "cuello"), "haz-cuello": (mv["cable del cuello"], "#e6e6e0", "cuello"),
        "E": (mv["E"], "#ec7a2d", "marco"), "topes": (mv["topes"], "#d9c9b0", "marco"),
        "panel": (mv["panel"], "#efeee9", "panel"), "driver": (mv["driver"], "#2c6fb0", "electronica-marco"),
        "adaptador-tactil": (mv["adaptador del táctil"], "#b03f8c", "electronica-marco"),
        "cables-marco": (mv["cables del marco"], "#e6e6e0", "electronica-marco"), "F": (mv["F"], "#c9661f", "tapa-marco"),
    }
    if LENTE:
        nodes["lente"] = (mv["lente"], "#bfe3f2", "lente")
if ESC:
    esc = Path(ESC); esc.mkdir(parents=True, exist_ok=True)
    man = {"frente": list(FRONT), "arriba": list(UP), "H": H, "tecla": list(TALK_C), "sw6": list(k(*SLIDES["SW6"][0])), "sw2": list(k(*SLIDES["SW2"][0])),
           "d8": list(k(*LEDS["D8"])), "sw1": list(SW1C), "nodos": {}}
    for n_, (s_, c_, g_) in nodes.items():
        export_stl(s_, str(esc / f"{n_}.stl"), tolerance=0.05, angular_tolerance=0.3)
        man["nodos"][n_] = {"color": c_, "grupo": g_}
    (esc / "escena.json").write_text(json.dumps(man, indent=1))
    print(f"escena en {esc}")

# ---------- Modelo armado para un visor 3D (glTF), abierta: una pieza por nodo ----------
if GLB:
    def tinted(shape, name, rgb):
        shape.label, shape.color = name, Color(*rgb)
        return shape
    def board_part(s):                                   # sustrato verde, módulo ESP32 metálico, el resto oscuro
        sz = s.bounding_box().size
        big = sorted((sz.X, sz.Y, sz.Z))
        if big[2] > 80:
            return (0.12, 0.42, 0.23)
        if big[1] > 17 and big[2] > 24:
            return (0.78, 0.78, 0.80)
        return (0.16, 0.16, 0.18)
    hexrgb = lambda h_: tuple(int(h_[i:i + 2], 16) / 255 for i in (1, 3, 5))
    gl = [tinted(s_, n_, hexrgb(c_)) for n_, (s_, c_, g_) in nodes.items() if n_ != "placa"]   # nombres ASCII: el visor no lee bien las tildes
    gl += [tinted(s, f"placa-{i}", board_part(s)) for i, s in enumerate(solids)]
    # Relleno de pintura blanca en el logo del frente
    logo_fill = extrude(Plane(origin=(0, LOGO_Y, -0.5), x_dir=(1, 0, 0), z_dir=(0, 0, 1)) * aule_logo(LOGO_H), amount=0.3)
    gl.append(tinted(FRAME_OPEN * logo_fill, "logo", hexrgb("#f2f0ea")))
    export_gltf(Compound(children=gl), str(OUT / "capri-dock-v2.glb"), binary=True, linear_deflection=0.2, angular_deflection=0.5)
    print("capri-dock-v2.glb")
    # Cinemática para el visor (mm y grados): mismos campos que la v1
    print("visor " + json.dumps({"ax1": [round(AX1[0], 3), round(AX1[1], 3)], "phi0": round(PHI0, 3), "psi": round(PSI, 3), "ln": round(LN, 3),
                                 "aOpen": A_OPEN, "aClosed": A_CLOSED, "ya": Y_A, "ez": Z_A, "cx": W / 2,
                                 "aa": [AA_W, AA_H, round(AAY1 - AA_H / 2, 3), round(ZPF + 0.1, 3)]}))

# ---------- Cortes: lateral por el cuello abierta y cerrada, y la tapa vista desde arriba ----------
if "--cortes" in sys.argv:
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    def section(shape, plane, to_xy):
        tris = []
        cut_ = shape.intersect(plane)
        for fc in (cut_.faces() if cut_ is not None else []):
            verts, idx = fc.tessellate(0.05)
            tris += [[to_xy(verts[i]) for i in tr] for tr in idx]
        return tris
    def layers(t):
        mv = moving_parts(t)
        ls = [(a, "#3a3d42"), (b, "#6b7078"), (mv["C"], "#16181b"), (h, "#e9e6dc"), (mv["E"], "#ec7a2d"),
              (mv["F"], "#c9661f"), (mv["panel"], "#d8d6cf"), (mv["driver"], "#2c6fb0"), (mv["adaptador del táctil"], "#b03f8c"),
              (obstacles["batería"], "#3b6fb6"), (obstacles["lastre"], "#8d9096"),
              (obstacles["parlante izquierdo"] + obstacles["parlante derecho"], "#55595f"),
              (obstacles["adaptador de J5"], "#7a3fb0"), (obstacles["adaptador de J6"], "#b03f8c"),
              (obstacles["placa y componentes"], "#2f9d5f"), (Compound([obstacles[f"interruptor {n_}"] for n_ in SLIDES]), "#9aa0a6"),
              (ffc_j6 + fpc_j5, "#e8a23a"), (mv["cables del marco"], "#b9b9b0"), (mv["cable del cuello"], "#b9b9b0")]
        if LENTE:
            ls.append((mv["lente"], "#9fd3ea"))
        return ls
    def through(p_, q_):                                 # plano vertical por dos puntos de la planta, y su proyección
        L_ = math.dist(p_, q_)
        ux, uy = (q_[0] - p_[0]) / L_, (q_[1] - p_[1]) / L_
        return Plane(origin=(p_[0], p_[1], 0), x_dir=(ux, uy, 0), z_dir=(uy, -ux, 0)), lambda v: ((v.X - p_[0]) * ux + (v.Y - p_[1]) * uy, v.Z)
    fig = plt.figure(figsize=(13, 19))
    xcut = W / 2 + 3
    pk, tk = through(TALK_C, SW1C)
    ps, ts = through(k(*SLIDES["SW6"][0]), k(*LEDS["D8"]))
    pj, tj = Plane.XZ.offset(-j6y), lambda v: (v.X, v.Z)
    cuts_ = [(fig.add_axes((0.04, 0.70, 0.44, 0.28)), 1.0, Plane.YZ.offset(xcut), lambda v: (v.Y, v.Z),
              f"abierta, corte por el cuello (x = {xcut:.0f})", None),
             (fig.add_axes((0.54, 0.70, 0.44, 0.28)), 0.0, Plane.YZ.offset(xcut), lambda v: (v.Y, v.Z),
              "cerrada, el mismo corte: el cuello en su bolsillo y el marco boca abajo", (-5, D + 5, 0, 70)),
             (fig.add_axes((0.04, 0.36, 0.92, 0.32)), 1.0, Plane.XY.offset(H - 1.0), lambda v: (v.X, v.Y),
              "la base desde arriba (corte a 1 mm bajo la tapa): bolsillo, tecla ●, ranuras de SW6 y SW2, luces y micrófonos", (0, W, 0, D)),
             (fig.add_axes((0.04, 0.19, 0.44, 0.15)), 1.0, pk, tk,
              "corte por la tecla ● y SW1: collar, tope de arriba y pulsador", (-14, 14, Z_FACE - 3, H + 3)),
             (fig.add_axes((0.54, 0.19, 0.44, 0.15)), 1.0, ps, ts,
              "corte por SW6 y D8: ranura con chaflán, palanca y guía de luz", (-9, 14, Z_FACE - 3, H + 3)),
             (fig.add_axes((0.04, 0.02, 0.44, 0.15)), 1.0, pj, tj,
              "corte por J6: la cinta corta da la vuelta junto a la pared y baja al adaptador", (165, W + 1, 0, H + 1)),
             (fig.add_axes((0.54, 0.02, 0.44, 0.15)), 0.0, Plane.YZ.offset(W / 2 + X_TOUCH), lambda v: (v.Y, v.Z),
              "corte del marco cerrado por la cola táctil: bisel, lente, panel, cola y adaptador", (-1, 30, H, H + GAP_C + FD + 1))]
    for ax, t, plane, to_xy, title, lim in cuts_:
        for shape, color in layers(t):
            tris = section(shape, plane, to_xy)
            if tris:
                ax.add_collection(PolyCollection(tris, facecolors=color, edgecolors=color, linewidths=0.2))
        ax.set_aspect("equal"); ax.autoscale_view(); ax.set_title(title, fontsize=9); ax.tick_params(labelsize=7)
        if lim:
            ax.set_xlim(lim[0], lim[1]); ax.set_ylim(lim[2], lim[3])
    fig.savefig(OUT / "sections.png", dpi=110); print("sections.png")

