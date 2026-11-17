// capri-mini v1.7: BQ24075 (power-path) + buck-boost TPS63000 a 3.37 V + corte térmico de carga U10/Q4, 2026-10-30.
// Contrato de placa para integrar y probar en el firmware; no es un driver.
#ifndef _BOARD_CONFIG_H_
#define _BOARD_CONFIG_H_

#include <driver/gpio.h>

#define AUDIO_INPUT_SAMPLE_RATE     16000
#define AUDIO_OUTPUT_SAMPLE_RATE    24000

// Botones y LEDs
#define BOOT_BUTTON_GPIO            GPIO_NUM_0    // solo en los pads TC2030 J4 (recuperación)
#define USER_BUTTON_GPIO            GPIO_NUM_2    // SW1, activo bajo, RC debounce
#define BUILTIN_LED_GPIO            GPIO_NUM_38   // v1.3: D2 WS2812B-2020 RGB (1 LED, protocolo WS2812 a 800 kHz, VDD = 3V3 = 3.39 V)
#define BUILTIN_LED_NUM             1
// BQ24075: D1 rojo = cargando (/CHG); D4 verde = entrada USB válida (/PGOOD).
// Verde solo = carga terminada o temporizador vencido (rojo parpadea a 2 Hz).
// Ojo: con la carga suspendida por temperatura (TS o U10) /CHG sigue bajo y el
// rojo sigue PRENDIDO (TI SLUS810 §9.3.6). Nada de esto llega al ESP32.
// v1.7: U10 (MCP65R41 + NTC TH2) y Q4 llevan TS a ~0 V entre 39.2 y 43.1 °C
// de placa y lo sueltan bajo 32.7–39.4 °C: la carga se suspende con los
// temporizadores detenidos. Es hardware puro: funciona con el ESP32 apagado y
// con SW2 en OFF. El firmware no lo ve ni lo controla.

// Audio: ES8311 (DAC) + ES7210 (ADC: 2 micrófonos + referencia AEC) + PAM8302A
#define AUDIO_I2S_GPIO_MCLK         GPIO_NUM_12
#define AUDIO_I2S_GPIO_BCLK         GPIO_NUM_13
#define AUDIO_I2S_GPIO_WS           GPIO_NUM_4    // v1.2: movido desde 14
#define AUDIO_I2S_GPIO_DIN          GPIO_NUM_15   // ES7210 SDOUT → ESP32
#define AUDIO_I2S_GPIO_DOUT         GPIO_NUM_16   // ESP32 → ES8311 DSDIN
#define AUDIO_CODEC_PA_PIN          GPIO_NUM_21   // PAM8302A ~SD: alto = encendido; pull-down R14 100k
#define AUDIO_CODEC_ES8311_ADDR     0x18          // CE = GND
#define AUDIO_INPUT_REFERENCE       true          // v1.4: ES7210 captura MIC1, MIC2 y la referencia del parlante (MIC3) → AEC por hardware
// Niveles (docs/v1.7-alimentacion/audio.md, cálculo del 31-oct; confirmar con test/prueba-audio-waveshare.md):
// - La referencia está en MIC3 = canal 2 del TDM ("FL,FR,RE,NA"). Con esp_capture y mic_layout "MR" la máscara
//   sería 1 | 4 (canal 0 = micrófono, canal 2 = referencia). El firmware de Waveshare usa 1 | 2 y la interrupción
//   funciona casi siempre: no cambiarlo sin el ensayo A; en capri-mini confirmar el canal al encenderla.
// - Ganancia por canal, no 30 dB para todos: micrófonos 24 dB (con 30 dB se saturan a 102 dB SPL) y referencia
//   18 dB (con 30 dB se satura desde ~90 % de volumen). esp_codec_dev_set_in_channel_gain() por canal.
// - Volumen máximo 80 % o limitador de picos: con VSYS 3.0 V el PAM8302A recorta cerca del 85 % (73 % si el
//   fondo de escala del ES8311 es por pin), y ese recorte no está en la referencia.
#define AUDIO_CODEC_ES7210_ADDR     0x40          // AD0 = AD1 = GND
#define AUDIO_POWER_EN_GPIO         GPIO_NUM_8    // Q1 load switch AUDIO_3V3: BAJO = códec y mic encendidos (pull-up 100k apaga en sleep)
// Al cerrar Q1, 3V3 cae ~0.1–0.3 V durante unos µs (simulación v1.7b: mínimo 3.09 V). Encender el audio una vez al
// despertar y no conmutarlo seguido; no escribir el WS2812B en ese instante.

// I2C: ES8311 (0x18), ES7210 (0x40), LIS2DH12 (0x19).
// R15/R16 suben a AUDIO_3V3. El bus solo funciona con el audio alimentado,
// incluso para acceder al acelerómetro (que conserva su alimentación 3V3).
#define I2C_SCL_IO                  GPIO_NUM_10
#define I2C_SDA_IO                  GPIO_NUM_11

// Acelerómetro LIS2DH12: wake-on-motion
#define ACCEL_I2C_ADDR              0x19          // SA0 = VDD
#define ACCEL_INT1_GPIO             GPIO_NUM_17   // RTC GPIO: ext wake desde deep sleep (nivel alto)

// Alimentación
// BQ24075 en modo USB500: toma como máximo 450–500 mA del USB; si el sistema
// pide más, la batería aporta el resto (sin diodo, FET BAT→OUT de ~50 mΩ).
// Carga: R4 3.9k → 228 mA típicos (204–250 mA), terminación ~23 mA.
// Temporizador (R31 68k): pre-carga ~54 min, carga rápida ~9 h (6.8–11.3 h);
// se alarga solo si el sistema le quita corriente a la carga. Si vence, D1
// parpadea a 2 Hz y la carga queda suspendida hasta desenchufar y enchufar.
// TH1 10k/B4250 en TS: ventana nominal ~5–45 °C EN TH1 (placa), no en la
// celda (2.4–50 °C con tolerancias); U10/Q4 bajan el corte caliente a 39–43 °C.
// Ver docs/v1.6-alimentacion y docs/v1.7-alimentacion.
// SW2 controla EN de U8: OFF no desconecta la batería; el cargador sigue vivo.
// 3V3 (v1.7): TPS63000 buck-boost, 3.33–3.41 V regulados con VSYS entre 1.8 y
// 5.5 V. Ya no cae con la batería baja: el reinicio por batería baja pasa a
// depender del PCM de la celda y de la caída de VSYS, no de 3V3.
// U8 corre en PWM mientras AUDIO_3V3 está encendido (PS/SYNC = AUDIO_3V3/2) y
// en ahorro de energía con el audio apagado: apagar Q1 en sleep también baja el
// consumo del regulador. No hay nada que configurar.
#define VBAT_SENSE_GPIO             GPIO_NUM_1    // ADC1_CH0, PWR_EN/2 = VSYS/2 cuando SW2 está ON
#define VBAT_SENSE_DIVIDER_RATIO    2.0f
// Sin USB: VSYS = VBAT − ≤50 mV (a 1 A), buena estimación de la batería.
// Con USB: VSYS ≈ VBUS (~4.8–5 V), NO es la batería: no usar para SOC,
// batería llena o terminación. No hay medición directa de BAT_RAW.
#define VBUS_SENSE_GPIO             GPIO_NUM_18   // Q3 aislador/inversor; pull-up R21 a 3V3
#define VBUS_PRESENT_LEVEL          0             // USB conectado = LOW; desconectado = HIGH
// Umbrales digitales ESP32-S3: LOW <= 0.25*VDD, HIGH >= 0.75*VDD.
// A 3.3 V: <=0.825 V / >=2.475 V. Ya NO es un divisor VBUS/2.
// C36 y la descarga de VBUS introducen demora: medir rebotes/retardo en banco.

// Reglas de firmware
// 1. Con AUDIO_3V3 presente, configurar LIS2DH12 para wake-on-motion;
//    terminar transacciones I2C y detener los periféricos I2S antes de apagar.
// 2. PA_PIN=LOW. SCL/SDA sin pull-ups internos (entrada sin pulls o drenador
//    abierto LOW). MCLK/BCLK/WS/DOUT=LOW retenidos durante deep sleep.
//    Retener también PA_PIN=LOW y AUDIO_POWER_EN_GPIO=HIGH para apagar Q1.
// 3. Con Q1 apagado NO ejecutar I2C, incluidos accesos al LIS2DH12.
//    Verificar en banco que ninguna señal inyecte corriente a AUDIO_3V3.
// 4. Al despertar: mantener PA en LOW, encender Q1, esperar estabilización de
//    AUDIO_3V3 e inicializar ES8311/ES7210 antes de reanudar audio.
//    Esperar al menos 10 ms de VDD estable en PAM8302A antes de habilitar PA.
//    Recalibrar volumen/AEC: ganancia analógica con R12/R13=30k es ~3.75 V/V.
// 5. Wake USB ahora por nivel LOW, movimiento por nivel HIGH. Configurar una
//    API de wake compatible con polaridades distintas (p. ej. ext0 en GPIO18
//    nivel 0 + ext1 ANY_HIGH en GPIO17); probar ambas fuentes.
//    No entrar a sleep con wake USB armado si ya está conectado (bucle wake).
// 6. Con USB ausente: si la estimación de batería (medida con el parlante
//    callado) baja de 3.5 V, limitar el volumen a ~0.5 W; si baja de 3.4 V,
//    avisar, apagar radio y dormir. v1.7: 3V3 ya no cae (simulación: 3.37 V
//    con la celda a 3.3 V y volumen máximo; VSYS baja a ~2.9 V). La regla
//    pasa a ser prudencia: cuida la celda y evita que abra su PCM en los
//    picos. El umbral real del PCM depende de la batería elegida; no asumir
//    2.5 V.
// 7. Probar enchufar/desenchufar USB con batería baja, Wi-Fi y audio activos.
// 8. Recomendada, ya no imprescindible (v1.7). Batería casi vacía + USB: la
//    entrada está limitada a 500 mA y en los picos del parlante la batería
//    pone el resto. En v1.6 3V3 caía y el equipo se reiniciaba; en v1.7 el
//    buck-boost sostiene 3V3 (simulación: VSYS mínimo 2.77 V con la celda a
//    3.0 V) y el riesgo que queda es que abra el PCM de la celda. Con USB
//    presente:
//    a) Al arrancar sin una estimación de batería reciente (guardar la última
//       medida sin USB, con su hora, en RTC/NVS), limitar el volumen a ~0.5 W
//       durante los primeros 20 min con USB.
//    b) Mientras suena el parlante, leer GPIO1 cada ~10 ms. Con USB, VSYS
//       normal es ≥ 4.2 V (en DPPM el BQ24075 lo regula a 4.3 V). Si baja de
//       4.1 V, la batería está aportando y VSYS ≈ VBAT bajo carga; si además
//       baja de 3.5 V, limitar el volumen a ~0.5 W en ese mismo ciclo.
//    c) Mantener el límite al menos 20 min con USB (la carga sube la celda);
//       después probar de nuevo y liberar si en los picos VSYS no baja de 3.6 V.
//    /CHG y /PGOOD no llegan al ESP32. Ya no hace falta exigir un cargador de
//    2 A: alcanza una fuente de 5 V que entregue al menos 500 mA (un puerto
//    USB 2.0 de PC sirve; uno de 100 mA no). Ensayo 14 de prueba-termica.md:
//    primero sin esta regla.


// Memoria v1.7d: N16R8 / C2913202; PSRAM Octal de 8 MiB.
#define CAPRI_ESP32_MODULE "ESP32-S3-WROOM-1-N16R8"
#define CAPRI_FLASH_SIZE_BYTES (16u * 1024u * 1024u)
#define CAPRI_PSRAM_SIZE_BYTES (8u * 1024u * 1024u)
// Perfil de memoria: nebu-firmware-esp32s3/sdkconfig.capri16mb.defaults
// Particiones: partitions.capri16mb.csv. Dos slots de 4 MiB.
// No implementa el cliente OTA ni el BSP de Capri.

#endif // _BOARD_CONFIG_H_
