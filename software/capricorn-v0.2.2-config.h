// Capricorn, placa v0.2.2 (capri-slate v0.2.2 táctil): mapa de pines. La v0.2.2 solo cambia L2 respecto de la
// v0.2.1, así que los pines son los mismos. Lo que no está aquí está en capri-mini-config.h.
//
// capri-slate v0.2 táctil: capri-mini v1.7d + tinta electrónica + táctil capacitivo + interruptor de silencio del
// micrófono, 2026-11-11.
// Cambios contra v0.1 (2026-11-03): salen los 3 botones de navegación (SW3-SW5 y su escalera en IO5) y entra el
// conector J6 del panel táctil (GT911) en IO5, IO40, IO41 e IO42.
// Contrato de placa para integrar y probar en el firmware; no es un driver.
// Todo lo que no aparece aquí es igual que en capri-mini-config.h (audio, I2C, alimentación, LEDs).

// Tinta electrónica: panel SPI de 24 pines por FPC (J5, Hirose FH12, contacto inferior).
// Panel previsto: Good Display GDEY075T7 de 7.5" (800x480, UC8179, 4 grises).
// Circuito de alto voltaje (Q5, L2, D5-D7) copiado del e-Paper Driver HAT V2.2 de Waveshare.
// JP2 elige la resistencia RESE: puenteado 1-2 = 0.47 Ω (7.5"); cortar y puentear 2-3 = 3 Ω (4.2").
// BS = GND: SPI de 4 hilos.
#define EPD_SPI_SCK_GPIO            GPIO_NUM_7
#define EPD_SPI_MOSI_GPIO           GPIO_NUM_9
#define EPD_CS_GPIO                 GPIO_NUM_14   // pull-up R42 10k: el panel queda deseleccionado durante el arranque
#define EPD_DC_GPIO                 GPIO_NUM_47
#define EPD_RST_GPIO                GPIO_NUM_48   // activo bajo
#define EPD_BUSY_GPIO               GPIO_NUM_39   // UC8179: BAJO = ocupado
#define EPD_SPI_SCLK_HZ             (10 * 1000 * 1000)  // empezar en 4 MHz si hay errores; la pista mide unos 40 mm

// Táctil capacitivo: GT911 del panel GDEY075T7-T01, por FPC de 6 pines (J6, Hirose FH12-6S-0.5SH(55), paso 0.5 mm,
// contacto inferior). Pines de J6: 1 GND, 2 3V3, 3 RST, 4 INT, 5 SDA, 6 SCL. Alimentación directa de 3V3 (C77 100 nF).
// Va en un SEGUNDO bus I2C, separado del de audio (I2C_SCL_IO / I2C_SDA_IO, IO10 / IO11): el bus de audio se apaga
// con AUDIO_3V3 (Q1) y el táctil no. Pull-ups en la placa: R50 4.7k (SCL) y R49 4.7k (SDA) a 3V3.
#define TOUCH_I2C_PORT              I2C_NUM_1
#define TOUCH_I2C_SCL_GPIO          GPIO_NUM_40   // J6.6, R50 4.7k a 3V3
#define TOUCH_I2C_SDA_GPIO          GPIO_NUM_41   // J6.5, R49 4.7k a 3V3
#define TOUCH_I2C_FREQ_HZ           (400 * 1000)
#define TOUCH_RST_GPIO              GPIO_NUM_42   // J6.3, activo bajo, pull-up R51 10k a 3V3
#define TOUCH_INT_GPIO              GPIO_NUM_5    // J6.4, RTC GPIO (ext0/ext1). SIN resistencia en la placa
#define TOUCH_I2C_ADDR              0x5D          // la fija el firmware con la secuencia de abajo
#define TOUCH_I2C_ADDR_ALT          0x14          // la otra dirección posible del GT911: sondearla si 0x5D no responde
// Dirección I2C del GT911: la toma del nivel de INT en el flanco de subida de RST. La placa NO tiene pull-down en
// INT a propósito, así que al encender (R51 sube RST con 3V3 mientras IO5 está en alta impedancia) la dirección
// queda indefinida. El firmware SIEMPRE hace esta secuencia antes de hablarle, también al volver de deep sleep si
// reinicia el táctil:
//   1. TOUCH_RST_GPIO y TOUCH_INT_GPIO como salida, los dos en BAJO. Esperar >= 10 ms.
//   2. Con INT todavía en BAJO (BAJO = 0x5D; ALTO = 0x14), esperar >= 100 us y soltar RST a ALTO.
//   3. Mantener INT en BAJO >= 5 ms después de subir RST.
//   4. TOUCH_INT_GPIO pasa a entrada (sin pull): desde aquí el GT911 lo maneja.
//      Esperar >= 50 ms DESDE ese cambio a entrada antes de configurar o acceder por I2C
//      (GT911 Programming Guide Rev.10, sección 4.3).
//   5. Leer el ID de producto (registro 0x8140, "911") en 0x5D; si no responde, probar 0x14 y registrar el fallo.
// IO5 ya no es ADC de botones: es la interrupción del táctil y una fuente de wake.
//   - Despierto: interrupción por flanco. El GT911 da un pulso por cada barrido con dedos; la polaridad la define
//     la configuración del panel (registro 0x804D). Leer el estado en 0x814E y escribirle 0 para rearmar.
//   - Deep sleep: GPIO5 es RTC GPIO y sirve como fuente ext0/ext1. Como INT no tiene resistencia en la placa, fijar
//     su nivel de reposo con el pull interno del dominio RTC. La polaridad tiene que ser compatible con las otras
//     fuentes de wake (regla 5 de capri-mini-config.h). El GT911 solo avisa por INT si queda despierto: en su modo
//     sleep (comando 0x05 en 0x8040) no genera INT al tocar. Polaridad y consumo se validan en banco con el panel.
// IO40, IO41 e IO42 son los pines JTAG (MTDO, MTDI, MTMS): no quemar eFuses que seleccionen JTAG por pines; la
// depuración sigue por USB-JTAG.

// Botones de navegación: NO EXISTEN en v0.2 (SW3, SW4, SW5, R43, R44, R45 y C74 quitados). La navegación es táctil.
// NAV_BUTTONS_ADC_GPIO y los umbrales NAV_BUTTON_*_MAX_MV de v0.1 se eliminan: el firmware no debe leer IO5 como ADC.
// SW1 (GPIO2) sigue siendo el botón de acción.

// Interruptor de silencio del micrófono (SW6, deslizable): hardware puro.
// SW6 en A (GND) = micrófono habilitado: Q6 (SI2301 P-MOSFET) conecta MICBIAS12 a los dos micrófonos y D8 verde se enciende.
// SW6 en B (3V3) = silencio: Q6 abre, R47 1M descarga MIC_VDD y D8 se apaga. El firmware no puede encender los micrófonos ni el LED.
// La palabra de activación corre en el ESP32 solo con el micrófono habilitado.
#define MIC_ENABLED_N_GPIO          GPIO_NUM_6    // BAJO = micrófono habilitado (lectura digital, C76 10 nF de filtro)

// GPIO libres que quedan: ninguno de uso general. IO40, IO41 e IO42 pasaron al táctil.
// Sin rutear en el módulo: IO3, IO45 e IO46 (pines de arranque: no usarlos sin revisar su nivel al encender) e
// IO35, IO36 e IO37 (los usa la PSRAM octal del ESP32-S3-WROOM-1-N16R8: no están disponibles).
