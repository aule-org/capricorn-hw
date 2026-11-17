# Capricorn Hardware

<p>
  <a href="https://github.com/aule-org/capricorn-hw"><img src="https://img.shields.io/badge/Hardware-Capricorn-1f6feb.svg" alt="Hardware de Capricorn"></a>
  <a href="https://github.com/aule-org/capricorn-sw"><img src="https://img.shields.io/badge/Software-capricorn--sw-2da44e.svg" alt="Software de Capricorn"></a>
  <a href="https://github.com/aule-org/capricorn-app"><img src="https://img.shields.io/badge/App-capricorn--app-8250df.svg" alt="App de Capricorn"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/Licencia-Apache%202.0-blue.svg" alt="Apache 2.0"></a>
</p>

([English](README.md) | Español)

**Capricorn es el tutor de IA de código abierto.** Un aparato tranquilo y dedicado para niños: una página de tinta electrónica, una voz que escucha y un tutor que sabe qué entiende ya el niño y qué le toca después. Sin feed, sin anuncios, sin una pantalla que brilla.

Todo niño merece un tutor paciente. Hoy los tutores de IA son apps cerradas que corren en aparatos hechos para otra cosa. Creemos que un tutor para niños debería ser lo contrario: algo que las familias y los colegios puedan revisar, reparar y mejorar. Por eso construimos Capricorn a la vista: hardware, firmware y app.

Este repositorio tiene el hardware: la placa, la carcasa, la lista de materiales y los archivos de fabricación.

## El aparato

| | Prototipo v0.2.2 |
|---|---|
| Procesador | ESP32-S3 (16 MB de flash, 8 MB de PSRAM), Wi-Fi y Bluetooth LE |
| Pantalla | Tinta electrónica de 7.5", 800 × 480, 4 grises, táctil capacitiva |
| Audio | ES7210 para los micrófonos + códec ES8311 con cancelación de eco, parlante integrado |
| Controles | Hablar, silenciar el micrófono y encendido: tres botones físicos. El táctil reemplaza los botones de navegación |
| Sensores | Acelerómetro, para despertar al levantarlo |
| Energía | Funciona enchufado o con batería |
| Placa | 92 × 48 mm, 4 capas |
| Carcasa | Base de escritorio plegable, impresa en 3D en PETG |

## Estado

- **v0.2.2:** las primeras cinco placas ensambladas están en producción (noviembre de 2026). Todavía no se han probado en el banco.
- **Archivos de diseño:** las fuentes de KiCad, la lista de materiales, los archivos de colocación y los modelos de la carcasa se publicarán aquí cuando las primeras placas estén encendidas y validadas. Publicar archivos que no hemos probado te haría perder tiempo y dinero.

Sigue el repositorio para enterarte cuando lleguen.

## Cómo encajan las piezas

```
capricorn-hw   el aparato: placa, tinta electrónica, audio, carcasa   (este repositorio)
capricorn-sw   firmware: xiaozhi-esp32 + transporte LiveKit (WebRTC)
capricorn-app  la app para familias: configurar el aparato, ver el avance, privacidad
     │
     └── habla con un servicio de tutor por LiveKit (Aule tiene uno; puedes correr el tuyo)
```

## Principios

- **Abierto por defecto.** Hardware, firmware y app son públicos. Si lo puedes comprar, lo puedes construir.
- **Sobre estándares, no islas.** Firmware basado en [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32), voz con [LiveKit](https://github.com/livekit/client-sdk-esp32), piezas comunes que se consiguen en cualquier parte.
- **Primero los niños.** Un botón físico para silenciar el micrófono. Consentimiento de los padres. Los datos de los niños no se usan para entrenar modelos.
- **Reparable.** Conectores estándar, carcasa imprimible y una lista de materiales con números de pieza reales.

## Contribuir

Los issues y las ideas son bienvenidos desde ya. Los pull requests al diseño tendrán sentido cuando los archivos fuente estén publicados aquí.

## Licencia

Apache License 2.0. Ver [LICENSE](LICENSE).

---

Hecho en Lima, Perú, por [Aule](https://meetaule.com) · admin@meetaule.com
