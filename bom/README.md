# Bill of Materials

Everything needed to build one Capricorn: the assembled board, the e-ink panel and the desk dock.

> **Prototype v0.2.2, not yet validated on the bench.** Do not order a batch until the first boards are brought up. Follow the repository for updates.

## Cost reference

Our first order: **5 boards, fully assembled by JLCPCB** (4 layers, ENIG, epoxy-filled vias, through-hole parts hand-soldered), November 2026.

| Item | 5 boards (USD) |
|---|---:|
| PCB fabrication | 83.81 |
| Assembly (includes 99.20 in per-part-type feeder fees and 84.68 in parts) | 246.03 |
| **Per board, before shipping** | **≈ 66** |
| DHL Express to Lima, for the whole order | 52.80 |

Most of the assembly cost is fixed per order (feeder fees are charged per distinct part type, not per part), so the price per board falls quickly with larger batches. Import duties and taxes are not included.

## Off-board parts

| Part | Qty | Notes |
|---|---:|---|
| Good Display GDEY075T7-T01 | 1 | 7.5" e-ink, 800 × 480, 4 grays, GT911 capacitive touch. About US$40 |
| Waveshare e-Paper driver (13512), without its 40-pin header | 1 | Mounted in the dock frame, behind the panel |
| FPC adapter, 24-pin 0.5 mm to 2.54 mm | 1 | For J5 |
| FPC adapter, 6-pin 0.5 mm to solder pads | 2 | For the touch flex and J6 |
| FFC ribbon, 6-pin, 0.5 mm pitch, 50 mm | 1 | For J6 |
| LiPo battery 805080 | 1 | Connects to J2 |
| Speaker, 28 mm, 8 Ω, 2 W | 2 | In parallel on J3 |
| Silicone wire, AWG 30, 450 mm | 14 | 8 for the panel, 6 for the touch controller |
| PETG filament | ~387 g | Seven printed parts, about 13.5 h on a 0.4 mm nozzle |
| Screws, hinges, ballast, rubber feet, optional lens | — | Full list in [hardware/enclosure](../hardware/enclosure/README.md#hardware-list) |

## Board parts

147 parts on 66 lines, as sent to JLCPCB: [`hardware/fab/BOM.csv`](../hardware/fab/BOM.csv) with placement in [`hardware/fab/CPL.csv`](../hardware/fab/CPL.csv). Before paying for assembly, check the placement preview with the [ordering guide](../hardware/ordering/README.md).

### Integrated circuits

| Part | Qty | Designators | Footprint | LCSC |
|---|---:|---|---|---|
| ESP32-S3-WROOM-1-N16R8 | 1 | U1 | `ESP32-S3-WROOM-1` | [C2913202](https://www.lcsc.com/product-detail/C2913202.html) |
| BQ24075 | 1 | U2 | `VQFN-16-1EP_3x3mm_P0.5mm_EP1.68x1.68mm_ThermalVias` | [C15464](https://www.lcsc.com/product-detail/C15464.html) |
| ES8311 | 1 | U4 | `WQFN-20_L3.0-W3.0-P0.40-BL-EP1.7` | [C962342](https://www.lcsc.com/product-detail/C962342.html) |
| USBLC6-2SC6 | 1 | U5 | `SOT-23-6_L2.9-W1.6-P0.95-LS2.8-BL` | [C2687116](https://www.lcsc.com/product-detail/C2687116.html) |
| PAM8302AASCR | 1 | U6 | `MSOP-8_L3.0-W3.0-P0.65-LS5.0-BL` | [C113367](https://www.lcsc.com/product-detail/C113367.html) |
| LIS2DH12TR | 1 | U7 | `LGA-12_L2.0-W2.0-P0.50-BL` | [C110926](https://www.lcsc.com/product-detail/C110926.html) |
| TPS63000 buck-boost 3.45V | 1 | U8 | `Texas_DRC0010J_ThermalVias` | [C24966](https://www.lcsc.com/product-detail/C24966.html) |
| ES7210 4ch ADC | 1 | U9 | `QFN-32_L4.0-W4.0-P0.40-BL-EP2.7` | [C365743](https://www.lcsc.com/product-detail/C365743.html) |
| MCP65R41-1202 thermal cut-off | 1 | U10 | `SOT-23-6` | [C219181](https://www.lcsc.com/product-detail/C219181.html) |

### Microphones

| Part | Qty | Designators | Footprint | LCSC |
|---|---:|---|---|---|
| ZTS6216 | 2 | MK1, MK2 | `MIC-SMD_4P-L2.8-W1.9-P1.84-TL` | [C481302](https://www.lcsc.com/product-detail/C481302.html) |

### Transistors

| Part | Qty | Designators | Footprint | LCSC |
|---|---:|---|---|---|
| SI2301CDS | 2 | Q1, Q6 | `SOT95P237X102-3N` | [C10487](https://www.lcsc.com/product-detail/C10487.html) |
| 2N7002 | 2 | Q3, Q4 | `SOT-23` | [C8545](https://www.lcsc.com/product-detail/C8545.html) |
| Si1308EDL | 1 | Q5 | `SOT-323_SC-70` | [C469327](https://www.lcsc.com/product-detail/C469327.html) |

### Diodes and LEDs

| Part | Qty | Designators | Footprint | LCSC |
|---|---:|---|---|---|
| red LED | 1 | D1 | `LED_0603_1608Metric` | [C2286](https://www.lcsc.com/product-detail/C2286.html) |
| WS2812B-2020 RGB | 1 | D2 | `LED_WS2812B-2020_PLCC4_2.0x2.0mm` | [C52917434](https://www.lcsc.com/product-detail/C52917434.html) |
| green LED mic on | 2 | D4, D8 | `LED_0603_1608Metric` | [C12624](https://www.lcsc.com/product-detail/C12624.html) |
| MBR0530 | 3 | D5, D6, D7 | `D_SOD-123` | [C82046](https://www.lcsc.com/product-detail/C82046.html) |

### Connectors

| Part | Qty | Designators | Footprint | LCSC |
|---|---:|---|---|---|
| USB-C | 1 | J1 | `USB_C_Receptacle_HRO_TYPE-C-31-M-12` | [C165948](https://www.lcsc.com/product-detail/C165948.html) |
| BATT | 2 | J2, J3 | `JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal` | [C173752](https://www.lcsc.com/product-detail/C173752.html) |
| EPD 24P FPC (GDEY075T7) | 1 | J5 | `Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal` | [C202112](https://www.lcsc.com/product-detail/C202112.html) |
| TOUCH 6P FPC (GT911) | 1 | J6 | `Hirose_FH12-6S-0.5SH_1x06-1MP_P0.50mm_Horizontal` | [C202118](https://www.lcsc.com/product-detail/C202118.html) |

### Switches

| Part | Qty | Designators | Footprint | LCSC |
|---|---:|---|---|---|
| TL3305AF160QG | 1 | SW1 | `SW_SPST_TL3305A` | [C2886899](https://www.lcsc.com/product-detail/C2886899.html) |
| SS12D00G6 system enable | 2 | SW2, SW6 | `SW_Slide_SPDT_YIZHI_SS12D00G6_P2.50mm` | [C50377150](https://www.lcsc.com/product-detail/C50377150.html) |

### Inductors

| Part | Qty | Designators | Footprint | LCSC |
|---|---:|---|---|---|
| 2.2uH | 1 | L1 | `L_1008_2520Metric` | [C22471111](https://www.lcsc.com/product-detail/C22471111.html) |
| 10uH | 1 | L2 | `L_Sunlord_SWPA6045S` | [C79272](https://www.lcsc.com/product-detail/C79272.html) |

### Capacitors

| Part | Qty | Designators | Footprint | LCSC |
|---|---:|---|---|---|
| 100nF | 5 | C1, C11, C12, C36, C37 | `C_0603_1608Metric` | [C14663](https://www.lcsc.com/product-detail/C14663.html) |
| 10uF | 3 | C2, C5, C27 | `C_0805_2012Metric` | [C15850](https://www.lcsc.com/product-detail/C15850.html) |
| 4.7uF | 2 | C4, C62 | `C_0805_2012Metric` | [C1779](https://www.lcsc.com/product-detail/C1779.html) |
| 1uF 50V | 11 | C6, C7, C13, C64, C65, C67, C68, C69, C70, C71, C72 | `C_0603_1608Metric` | [C15849](https://www.lcsc.com/product-detail/C15849.html) |
| 100nF | 15 | C14, C15, C16, C28, C32, C33, C38, C39, C40, C51, C58, C59, C73, C75, C77 | `C_0402_1005Metric` | [C307331](https://www.lcsc.com/product-detail/C307331.html) |
| 1uF | 21 | C17, C18, C19, C20, C21, C22, C24, C25, C41, C42, C43, C44, C45, C46, C47, C48, C49, C50, C52, C53, C54 | `C_0402_1005Metric` | [C52923](https://www.lcsc.com/product-detail/C52923.html) |
| 1nF | 2 | C29, C30 | `C_0402_1005Metric` | [C1523](https://www.lcsc.com/product-detail/C1523.html) |
| 47uF | 2 | C31, C35 | `C_0805_2012Metric` | [C16780](https://www.lcsc.com/product-detail/C16780.html) |
| 10uF | 1 | C34 | `C_0603_1608Metric` | [C19702](https://www.lcsc.com/product-detail/C19702.html) |
| 10nF | 2 | C55, C76 | `C_0402_1005Metric` | [C15195](https://www.lcsc.com/product-detail/C15195.html) |
| 2.2uF 25V | 1 | C56 | `C_0402_1005Metric` | [C307418](https://www.lcsc.com/product-detail/C307418.html) |
| 10uF 25V | 1 | C57 | `C_0603_1608Metric` | [C96446](https://www.lcsc.com/product-detail/C96446.html) |
| 39pF | 1 | C60 | `C_0402_1005Metric` | [C1563](https://www.lcsc.com/product-detail/C1563.html) |
| 4.7uF 50V | 1 | C61 | `C_0805_2012Metric` | [C98192](https://www.lcsc.com/product-detail/C98192.html) |
| 10nF 25V C0G | 1 | C78 | `C_0402_1005Metric` | [C3855387](https://www.lcsc.com/product-detail/C3855387.html) |

### Resistors

| Part | Qty | Designators | Footprint | LCSC |
|---|---:|---|---|---|
| 10k | 4 | R1, R8, R39, R42 | `R_0603_1608Metric` | [C25804](https://www.lcsc.com/product-detail/C25804.html) |
| 5.1k | 2 | R2, R3 | `R_0402_1005Metric` | [C25905](https://www.lcsc.com/product-detail/C25905.html) |
| 3.9k | 1 | R4 | `R_0402_1005Metric` | [C51721](https://www.lcsc.com/product-detail/C51721.html) |
| 1k | 2 | R5, R29 | `R_0603_1608Metric` | [C21190](https://www.lcsc.com/product-detail/C21190.html) |
| 100k | 6 | R9, R10, R14, R19, R20, R21 | `R_0603_1608Metric` | [C25803](https://www.lcsc.com/product-detail/C25803.html) |
| 30k | 2 | R12, R13 | `R_0603_1608Metric` | [C22984](https://www.lcsc.com/product-detail/C22984.html) |
| 4.7k | 2 | R15, R16 | `R_0603_1608Metric` | [C23162](https://www.lcsc.com/product-detail/C23162.html) |
| 56k | 1 | R17 | `R_0402_1005Metric` | [C853330](https://www.lcsc.com/product-detail/C853330.html) |
| 9.76k | 1 | R18 | `R_0402_1005Metric` | [C2686425](https://www.lcsc.com/product-detail/C2686425.html) |
| 330R | 1 | R22 | `R_0603_1608Metric` | [C23138](https://www.lcsc.com/product-detail/C23138.html) |
| 27k | 2 | R23, R24 | `R_0603_1608Metric` | [C22967](https://www.lcsc.com/product-detail/C22967.html) |
| 3.3k | 1 | R25 | `R_0402_1005Metric` | [C25890](https://www.lcsc.com/product-detail/C25890.html) |
| 100k | 6 | R28, R33, R34, R37, R38, R48 | `R_0402_1005Metric` | [C25741](https://www.lcsc.com/product-detail/C25741.html) |
| 1.5k | 1 | R30 | `R_0402_1005Metric` | [C25867](https://www.lcsc.com/product-detail/C25867.html) |
| 68k | 1 | R31 | `R_0402_1005Metric` | [C36871](https://www.lcsc.com/product-detail/C36871.html) |
| 49.9k | 1 | R32 | `R_0402_1005Metric` | [C137969](https://www.lcsc.com/product-detail/C137969.html) |
| 100R | 1 | R35 | `R_0402_1005Metric` | [C25076](https://www.lcsc.com/product-detail/C25076.html) |
| 3.3M | 1 | R36 | `R_0402_1005Metric` | [C470023](https://www.lcsc.com/product-detail/C470023.html) |
| 0.47R | 1 | R40 | `R_0603_1608Metric` | [C23411](https://www.lcsc.com/product-detail/C23411.html) |
| 3R | 1 | R41 | `R_0603_1608Metric` | [C23157](https://www.lcsc.com/product-detail/C23157.html) |
| 2.2k | 1 | R46 | `R_0603_1608Metric` | [C4190](https://www.lcsc.com/product-detail/C4190.html) |
| 1M | 1 | R47 | `R_0402_1005Metric` | [C26083](https://www.lcsc.com/product-detail/C26083.html) |
| 4.7k | 2 | R49, R50 | `R_0402_1005Metric` | [C25900](https://www.lcsc.com/product-detail/C25900.html) |
| 10k | 1 | R51 | `R_0402_1005Metric` | [C25744](https://www.lcsc.com/product-detail/C25744.html) |

### Other

| Part | Qty | Designators | Footprint | LCSC |
|---|---:|---|---|---|
| 10k B4250 | 1 | TH1 | `R_0402_1005Metric` | [C236281](https://www.lcsc.com/product-detail/C236281.html) |
| 100k B4250 1% | 1 | TH2 | `R_0402_1005Metric` | [C77130](https://www.lcsc.com/product-detail/C77130.html) |
