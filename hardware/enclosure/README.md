# Capricorn: folding desk dock (capri-dock v2)

This is the second version of the Capricorn desk dock, adapted to the touch board, currently the **capri-slate v0.2.2 touch** (same geometry as v0.2.1: only the value of L2 and the silkscreen text change), and to the **GDEY075T7-T01** panel (7.5", 800 × 480, GT911 capacitive touch), and set up to print in PETG on the Elegoo Centauri Carbon.
The shape is the same (L-shaped neck, frame with the same outline as the base, hidden hinge), **with a thinner bezel**: base and frame measure 194 × 138.5 mm (previously 200 × 140), 36 mm tall. What v1 explains and did not change (folding, hinge hardware, childproofing) is still in its README.

**Status (2026-11-12):** `dock.py` passes its 635 checks against `../board/capri-slate-v0.2.2-tactil.step`, which is its default board (617 with `--sin-lente` (no lens), 635 with `--colas-derecha` (flex tails on the right)). `printcheck.py` passes on all three. The 7 parts and the 2 no-lens alternatives are sliced.
**v0.2.2 STEP:** [`../board/capri-slate-v0.2.2-tactil.step`](../board/capri-slate-v0.2.2-tactil.step) is the assembled board with the 3D models of all its components: 129 solids. The 635 checks pass against it.
**It is not validated with the real panel:** the positions of the flex tails, the adapters and the driver are assumptions marked MEDIR (to be measured).

## What can be printed now and what has to wait

| Part | Now? | What it depends on |
|---|---|---|
| `H-tecla-hablar` (talk key), `N-placa-nombre` (name plate) | **Yes** | Nothing from the panel. H lets you test the SW1 click with the board in your hand (7 minutes) |
| `C-cuello` (neck) | **Yes** | Only on the M10 × 1 nipple (threads into Ø9, bore of 6.5 mm or more) and on the AWG 30 wire |
| `B-fondo` (bottom cover) | **Yes** | On the 805080 battery and on the flat bars, which are now cut to **57 mm** |
| `A-base` (base) | **Yes, with one risk** | It does not depend on the panel. It does depend on the real SS12D00G6 switch (lever and height, currently a box in the STEP) and on the 28 mm speakers. It is the long print (5 h 26 min): better to measure the switch first |
| `E-marco` (frame), `F-tapa-marco` (frame cover) | **No: they wait for the panel** | On where the two flex tails come out, on the driver, on the touch adapter and on whether it is built with a lens. Printing them earlier is betting on the assumptions in the table below |

## Bezel: before and after

| | v1 and first v2 | Now | Change |
|---|---|---|---|
| Frame and base outline | 200 × 140 mm | **194 × 138.5 mm** | −6 and −1.5 |
| From the frame edge to the panel, at the sides | 14.9 mm | **11.9 mm** | −3.0 per side |
| Top | 8.3 mm | **6.8 mm** | −1.5 |
| Bottom (hinge H2 goes inside) | 20.5 mm | 20.5 mm | same |
| Visible bezel, up to the active area: sides / top / bottom | 17.9 / 17.6 / 23.5 mm | **14.9 / 16.1 / 23.5 mm** | |

What had to move for the checks to pass (the previous attempt, only narrowing, broke 10):
- **Frame:** the 4 screw bosses and their bumpers go 3.5 mm further toward the corners, outside the panel.
- **Ballast:** 57 mm flat bars instead of 60 (506 g instead of 533), up against the battery bay: they end up 16 mm from the antenna.
- **Battery:** against the left wall and 2 mm further forward, so it does not overlap the corner boss.
- **H1 pin bushing:** 3.5 mm instead of 5, with the M4 head recessed: it ends up 0.6 mm from the board edge, with 2.8 mm of bearing length (previously 7.5).
- **Cables:** routes tied to the right wall and to the nipple tip, not to fixed coordinates.
- **Stability:** it weighs ~1176 g; pushing on the center of the screen tips it over at 4.6 N (previously 4.9; the minimum is 3).

**Why not more:** at the sides, the Ø7 boss is already between the panel guide and the frame wall, and in the base the ballast was already shortened to keep the 15 mm for the antenna. At the top, the fold of the flex tails uses 3.3 of the 4.4 mm that are left. At the bottom the hinge sets the limit.

![Exploded](exploded.png)

![Controls](controls.png)

![Section views](sections.png)

![Assembled](view.png)

## What changed from v1

| Topic | v1 | v2 |
|---|---|---|
| **Navigation buttons** | Comb G with 3 levers over SW3, SW4 and SW5 | **They are not on the board: all of it is gone.** No part G, none of its 3 holes, no rivet posts, no pushers and no flexures. The cover is closed there |
| **● key (H)** | Over SW4, pushed by the comb | **Over SW1**, the only push button left. It is a solid Ø16 plunger with a guide, an upper stop and a lower stop. The small SW1 cover (part D) no longer exists |
| **SW6 and SW2 slots** | Centered on the footprint origin, which is **pad 1**: they ended up 2.5 mm from the center of the lever | Centered on the real switch body, read from the STEP. The SW6 slot has a 45° chamfer for the fingertip |
| **Panel** | 1.18 mm, one flex tail at the center | 2.13 mm, two flex tails toward one end of the edge. The guides in E are 0.95 mm deeper and the ribs in F are shorter; the frame measures the same |
| **Lens** | Fixed | A parameter: `--sin-lente` (default is with lens) |
| **Panel driver** | Lying flat and centered | **Standing upright**, under the 24-pin flex tail, with the touch adapter next to it |
| **Cables through the hinges** | 8 wires, Ø6 channel | **14 wires** (8 for the panel + 6 for touch), Ø7 channel |
| **Touch in the base** | There was none | 6-pin adapter on the floor and a short ribbon that leaves J6 and turns back next to the right wall |
| **Printing** | "No supports", but it did not print that way (see below) | Checked layer by layer. Only A takes support, in one place |
| **Bezel** | Frame and base of 200 × 140 | 194 × 138.5: 3 mm less per side and 1.5 at the top (see above) |
| **STL** | In assembly position | **In print orientation** (the bed at z = 0). The STEP files are still in assembly position |

`--vista` (view) was not ported: `render.py` replaces it. The model for the 3D viewer was: see [3D viewer](#3d-viewer).

### The ● key over SW1

- **It cannot be centered on SW1:** LED D1 is 5.7 mm away and the SW2 slot is 6.3 mm away. It is offset 4.3 mm (toward the front and toward the USB) and presses the push button with its bottom face. That leaves 0.78 mm of cover up to the D1 hole and 1.4 mm up to the SW2 slot.
- **Guide:** the hole in the cover plus a collar underneath, 4.5 mm in total, with 0.2 mm of clearance per side.
- **Upper stop:** two 45° ears that seat against the cover. They also keep it from rotating and from being pulled out. It goes in from below, before the board.
- **Lower stop:** two Ø2.2 feet that land on bare board 0.5 mm after touching SW1 (`TALK_STOP`). Together with SW1 they form a tripod: the key does not sink or tilt any further. **They do not take load off the push button:** the TL3305 bottoms out at 0.25 mm; a shorter stop risks it not closing.
- **It ends up behind the open screen.** SW1 is at the back right of the base (103 mm from the front); the open frame starts at 60 mm. You reach it from the side. Bringing it to the front means moving the push button on the board.

### What v1 could not print without supports

`printcheck.py` found it in the v1 parts that v2 inherited; everything was fixed except the first one:

| Where | Problem | What was done |
|---|---|---|
| A, floor of the neck pocket | Ceiling of 62 × 75 mm at 17.5 mm from the bed | **It takes support**, only there, from the bed. It comes out in one block |
| A, thumb recess | Ellipsoid: its ceiling was an overhang | Walls at 45° |
| A, speaker rings | The ring closed in mid-air | Block with a half-round groove and two arcs up to 45° |
| A, H1 pin bushing | It started in mid-air | Joined to the cover |
| A, name plate recess | 1.2 mm edge as an overhang | Edge at 45°; plate N has the same bevel |
| A and E, fillet that sits on the bed | The lower half exceeds 45° | 45° facet tangent to the fillet (0.9 mm in A, 0.45 mm in E) |
| C, M4 nut slots | The pin hole split their ceiling | 0.2 mm skin that the screw pierces, and a relief at the mouth of the H1 slot |
| B and E, recesses for feet and bumpers | Ring-shaped ceiling around the countersink | 0.2 mm skin that the screw pierces |
| H, key flange | Ring as an overhang | Ears at 45° |

## Parts

| File | What it is | How it prints | Time | PETG |
|---|---|---|---|---|
| `A-base.stl` | Cover and walls of the base: neck pocket, key hole and collar, SW6 and SW2 slots, light guides, microphone tubes, board rests, USB tunnel, speakers | Cover on the bed. **With support only in the pocket** | 5 h 26 min | 158.7 g |
| `B-fondo.stl` | Bottom cover: ballast pockets, battery bay, board studs | Flat, outside face on the bed | 2 h 28 min | 70.0 g |
| `C-cuello.stl` | L-shaped neck, with the Ø7 channel | On its side, left face on the bed. **5 perimeters** | 1 h 34 min | 44.5 g |
| `E-marco.stl` | Frame: bezel, panel guides, H2 blocks | Front face on the bed | 1 h 46 min | 50.0 g |
| `F-tapa-marco.stl` | Frame cover, with the panel ribs | Back face on the bed | 2 h 04 min | 61.8 g |
| `H-tecla-hablar.stl` | ● key | Top face on the bed | 7 min | 1.0 g |
| `N-placa-nombre.stl` | Name plate (`--nombre=…`) | Face up; pause at 1.2 mm to switch from white to black | 4 min | 1.3 g |
| | **Total (with lens)** | | **13 h 29 min** | **387 g** |
| `sin-lente/E-marco.stl` | Alternative to E for a build without lens | Same as E | 1 h 45 min | 49.5 g |
| `sin-lente/F-tapa-marco.stl` | Alternative to F for a build without lens | Same as F | 2 h 05 min | 62.5 g |

Colors: A, B and C in black (273 g); E and F in the frame color (112 g); H and N in white.
Without lens, swap E and F for the ones in `sin-lente/` (the other parts do not change): the total stays the same, 13 h 29 min and 387 g.

**Slicing:** ElegooSlicer, Centauri Carbon, 0.4 nozzle, textured PEI. PETG at 250 °C, bed at 70 °C, part cooling fan capped at 25 %, 0.2 mm layer, 3 perimeters, 20 % gyroid. The gcode files are not versioned: `laminar.py` generates them with these settings.

### Printing rules and how they are met

| Rule | Result |
|---|---|
| 256 mm bed | The largest part measures 194 × 138.5 mm |
| Walls of 1.2 mm or more | Base 2.4 / 2.0 / 3.0; frame 2.4 / 2.0 / 2.5; ribs, guides, collar and tubes 1.2. **Exceptions:** the D1 light guide drops to 0.45 mm in its bottom 2.5 mm, where it passes between SW1 and SW2; the speaker grille has bars of ~1 mm; under the SW6 chamfer 0.8 mm of cover is left |
| No overhangs over 45° | `printcheck.py`: no overhangs and no islands. Steps of less than one line (0.5 mm) remain in up to 5 consecutive layers: the ceiling of the horizontal round holes (nipple clearance holes Ø10.3, Ø7 channel) |
| Bridges of 20 mm or less | The longest measures 13.0 mm (ceiling of the USB tunnel) |
| Flexures for PETG | **None are left.** The only one in v1 was the key comb's |
| Clearance of 0.15 to 0.2 mm per side | 0.15 for B inside A, F inside E and plate N; 0.2 on the key; 0.15 on the nipple clearance holes |

## Touch and wiring

`dock.py` models each cable as a tube along its route and checks that it does not intersect any part.

| Cable | From | To | Model length |
|---|---|---|---|
| 24-pin flex tail | top edge of the panel, at the back | driver, folded over the edge | 11 mm |
| 6-pin touch flex tail | top edge of the panel, at the front | frame adapter, folded over the edge | 13 mm |
| 8 panel wires | driver (from below) | junction, in the frame | 27 mm |
| 6 touch wires | frame adapter | junction, in the frame | 67 mm |
| Bundle of 14, frame | junction | H2 nipple | 45 mm |
| Bundle of 14, neck | H2 nipple | H1 nipple, through the channel | 130 mm |
| Bundle of 14, base | H1 nipple | junction, over the ballast | 124 mm |
| 8 panel wires | junction | J5 adapter | 25 mm |
| 6 touch wires | junction | J6 adapter | 41 mm |
| Short J5 ribbon | J5 | its adapter, along the front edge of the board | 30 mm |
| Short J6 ribbon | J6 | its adapter, turning back next to the right wall | 31 mm |

- **The 8 panel wires measure 351 mm and the 6 touch wires 407 mm.** Cut all 14 to 450 mm.
- **Assumed wire:** AWG 30 silicone, Ø0.8 mm with insulation. The 14 make a Ø3.5 bundle: they take up 18 % of the neck channel (Ø7) and 21 % of the nipple (Ø6.5 assumed). **With AWG 28 (Ø1.2) they do not fit.**
- **Touch pins:** 1 GND, 2 3V3, 3 RESET, 4 INT, 5 SDA, 6 SCL, one to one between the two adapters.
- **J6 opens toward the right wall.** The ribbon has 5 mm to turn back with a 2.5 radius and goes down to the adapter, on the floor under the board edge. The speaker cable was moved against the wall to make room for it.
- **Lens and touch:** with a lens, the 0.5 mm gasket sits between the polycarbonate and the panel, which means air over the active area. That is the worst case for capacitive touch. It has to be tested before deciding; `--sin-lente` is the way out.

## Hardware list

- **Hinges:**
  - 2 M10 × 1 lamp nipples of ~30 mm, with a thin Ø14 knurled nut and a spring washer; bore of 6.5 mm or more;
  - 1 nylon M4 × 25 screw with a nylon nut (H1), cheese head or pan head of Ø8 or less and 3 mm tall (it sits recessed in its bushing), and 1 steel one with nut and spring washer (H2);
  - 4 PTFE washers of 1 mm (M10 and M4).
- **Base:** 5 M3 × 10 self-tapping screws for plastic, countersunk head, from below.
- **Frame:** 4 M3 × 12 countersunk self-tapping screws, from the front, under the bumpers.
- **Board:** 1 M2 × 6 **nylon** screw at H1, from below.
- **Panel:**
  - Good Display GDEY075T7-T01 (7.5", with GT911 touch);
  - Waveshare 13512 driver, without the 40-pin connector, in the frame;
  - 24-pin FPC to 2.54 mm adapter for J5;
  - 2 6-pin FPC adapters, 0.5 mm pitch, to solder pads, and 1 6-pin FFC ribbon, 0.5 mm pitch, 50 mm long, for J6.
- **Cables:** 14 AWG 30 silicone wires of 450 mm (8 for the panel and 6 for touch); with AWG 28 they do not fit through the hinges. Neutral-cure silicone for strain relief.
- **Ballast:** 4 pieces of 1¾ × ¼ inch (44.5 × 6.35 mm) steel flat bar, **57 mm** long, stacked in pairs and glued with silicone.
- **Battery:** LiPo 805080.
- **Audio:** 2 speakers of 28 mm, 8 Ω, 2 W, in parallel on J3 (4 Ω, within what the PAM8302A accepts).
- **Rubber:**
  - 4 clear bumpers of Ø8 × 3.5 mm for the bezel, which sit 1 mm into their recess (**MEDIR** that this size is available; if not, adjust `GAP_C` and `BUMP_REC`);
  - 4 adhesive feet of Ø12 × 3 mm, sunk 1 mm over the corner screws.
- **Lens (optional):** 1 mm anti-glare polycarbonate, 170.2 × 111.2 mm (laser cut), and a 0.5 mm foam gasket around the active area. Without lens, use the parts in `sin-lente/`.
- **1.5 mm EVA foam:** a strip over the back edge of the panel and a rectangle under the battery.
- **Gaskets:**
  - 2 foam gaskets of 0.5 mm, ring-shaped, for the speakers;
  - 2 rings of Ø2.8 / Ø1.6 × 1.3 mm to seal the microphones.

## Assembly

1. **Cables.**
   1. Solder 8 wires to the J5 adapter and 6 to the J6 adapter.
   2. Bring them together and pass them through the H1 nipple, the neck channel (the hole at the elbow helps) and the H2 nipple.
2. **Board into A.**
   1. Fit the microphone rings.
   2. Insert the ● key (H) from the inside, with the ears in their slots.
   3. Seat the board with the components toward the cover: the SW6 and SW2 levers go into their slots.
   4. Screw in the nylon M2.
   5. Plug the 24-pin ribbon into J5 and the 6-pin one into J6, and each one into its adapter.
3. **H1, speakers, bottom cover B and closing the base:** as in v1.
4. **Frame.**
   1. Place the lens and the gasket (or only the gasket) in E, and the panel face down **with the flex tails pointing up**.
   2. Glue the driver behind the panel, standing upright under the 24-pin flex tail, and the touch adapter under its own. Plug in both flex tails.
   3. Mount H2 as in v1.
   4. Solder the 8 wires to the driver and the 6 to the adapter. The bundle goes up on the left, through the notch in the bottom rib of F.
   5. Silicone on the nipple tips. Close with F.
5. **Rubber and finishing:** as in v1.

## Measure before printing

All of them are at the top of `dock.py`.

| Parameter | Value | What to measure |
|---|---|---|
| `TAIL_END` | −1 (left, seen from the front) | Which end of the edge the flex tails come out of. The other one: `--colas-derecha` (passes the 635 checks) |
| `TAIL_DISP`, `TAIL_DISP_W` | 47 / 12.5 mm | Center and width of the 24-pin flex tail |
| `TAIL_TOUCH`, `TAIL_TOUCH_W` | **20** / 3.5 mm | Center and width of the touch flex tail. **The 20 is an assumption:** the drawing only says "closer to the same end". Each flex tail has 4 mm of air per side |
| `PT` | 2.13 mm | Thickness of the panel with touch |
| `DRIVER`, `DRV_FPC_OFF` | 30.2 × 65 × 5 mm, 0 | The driver and where its FPC connector is. **It is assumed to be on a short side**; if it is on a long one, the driver lies flat and the adapter has to move |
| `TOUCH_AD`, `J6_ADAPTER` | 15 × 12 × 3 and 12 × 15 × 3 mm | The 6-pin adapters you buy |
| `WIRE_D`, `NIP_ID` | 0.8 / 6.5 mm | The wire with insulation and the nipple bore |
| `LENTE`, `LENS_T`, `GASKET`, `FOAM` | with lens, 1 / 0.5 / 1.5 mm | Touch through the lens. The foams you can get |
| `SLIDE_BODY`, `SLIDE_TOP`, `SLIDE_LEVER`, `SLIDE_TRAVEL` | 3.5 / 9.5 / 2 / 2 mm | The real SS12D00G6: height, lever and travel. In the STEP it is a solid box |
| `TALK_STOP` | 0.5 mm | That SW1 clicks before the feet touch the board |
| MK1 and MK2 port | footprint origin | The microphone body in the STEP is offset 0.26 mm from the origin; the tube tolerates 0.5 |
| J6 ribbon | 50 mm, contact side unconfirmed | J6 is bottom-contact; the ribbon reaches the adapter flipped over |

The v1 ones that still apply: `AA_TOP`, `NIP_D`, `NIP_TAP`, `NUT_R`, `GAP_C`, `BUMP_REC`, `SPK_D`, `SPK_T`, `BATT`, `LASTRE`, `MASS`.

## Checks

`dock.py` does not export if any of its **635 checks** fails (617 with `--sin-lente`):
- **real board (STEP):** SW1, the body of SW6 and of SW2, the 4 LEDs, the 2 microphones and J6 are where the enclosure expects them; no push button is left at the location of SW3, SW4 and SW5;
- **● key:** SW1 is under the key; at rest it is 0.18 mm away; it completes its travel without rubbing; upper stop and lower stop; guide; enough cover up to D1, D2, MK2 and SW2;
- **SW6 and SW2:** the lever covers its 2 mm of travel with 1 mm of air per end and 0.2 per side, protrudes 1 mm and stays under the closed frame; the D8 window is outside the chamfer;
- **panel:** 2.13 mm, held with the foam compressed 15 %; the bezel overlaps it by 3 mm or more per edge, with or without lens;
- **touch:** the flex tails do not overlap; the adapter fits next to the driver; 14 wires through the channel and through the nipple; the J6 ribbon has room for the turn;
- **cables:** none intersects a part, the board, the battery, the ballast, the speakers, the adapters, the panel, the lens or the driver;
- **open, closed and at 20, 40, 60 and 80 % of the swing:** 0 interference between all parts and against the board STEP;
- **printing:** each part fits on the bed in its orientation; walls and clearances;
- the v1 ones that still apply: antenna, speakers, name plate, logo, stability and forcing of the hinges.

## 3D viewer

`dock.py --glb` writes `capri-dock-v2.glb`: the dock open, in meters, with one part per node (273 nodes; the board goes in `placa-0` … `placa-N`) and the same `visor {…}` kinematics line as v1. It is not published anywhere.
- **Node names:** `A`, `B`, `C`, `E`, `F`, `H`, `N`, `letras`, `logo`, `panel`, `lente`, `driver`, `adaptador-tactil`, `adaptador-J5`, `adaptador-J6`, `cintas`, `haz-base`, `haz-cuello`, `cables-marco`, `otros-cables`, `palancas`, `bateria`, `lastre`, `parlantes`, `patas`, `topes`.
- **Compared with the v1 GLB:** `D` and `G` do not exist; `nombre` became `N`; the cables and speakers are grouped differently. A viewer that looks for the v1 names has to be adjusted.
- It was verified that it loads and renders (trimesh and pyvista); it was not tested on the viewer page.

`printcheck.py` is a separate check, on the STL files: it compares each 0.2 mm layer with the one below and does not accept overhangs, islands, bridges over 20 mm or slopes over 45° outside the support zone declared in `impresion.json`.

```sh
# from hardware/enclosure/
uv run --python 3.12 --with build123d python -I dock.py                       # parts and checks (~50 s)
uv run --python 3.12 --with build123d python -I dock.py SALIDA --sin-lente    # no lens (create SALIDA first)
uv run --python 3.12 --with build123d python -I dock.py SALIDA --colas-derecha
uv run --python 3.12 --with build123d python -I dock.py SALIDA --board=../board/OTRA.step
uv run --python 3.12 --with build123d --with matplotlib python -I dock.py --cortes --escena=/tmp/escena --glb   # + capri-dock-v2.glb
uv run --python 3.12 --with pyvista python -I render.py /tmp/escena           # view.png, exploded.png, controls.png
uv run --python 3.12 --with trimesh --with shapely --with numpy --with scipy --with networkx --with rtree python -I printcheck.py
cp SALIDA/E-marco.st* SALIDA/F-tapa-marco.st* sin-lente/                      # after running --sin-lente: these are the two parts that change
python3 -I laminar.py                                                         # gcode in ~/Documents/Capricorn - impresión/ (deletes the previous ones)
```
