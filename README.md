# Capricorn Hardware

<p>
  <a href="https://github.com/aule-org/capricorn-hw"><img src="https://img.shields.io/badge/Hardware-Capricorn-1f6feb.svg" alt="Capricorn hardware"></a>
  <a href="https://github.com/aule-org/capricorn-sw"><img src="https://img.shields.io/badge/Software-capricorn--sw-2da44e.svg" alt="Capricorn software"></a>
  <a href="https://github.com/aule-org/capricorn-app"><img src="https://img.shields.io/badge/App-capricorn--app-8250df.svg" alt="Capricorn app"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="Apache 2.0"></a>
</p>

(English | [Español](README.es.md))

**Capricorn is the open-source AI tutor.** A calm, dedicated device for children: an e-ink page, a voice that listens, and a tutor that knows what the child already understands and what comes next. No feed, no ads, no glowing screen.

Every child deserves a patient tutor. Today, AI tutors are closed apps running on devices built for something else. We think a tutor for children should be the opposite: something families and schools can inspect, repair and improve. So we build Capricorn in the open: hardware, firmware and app.

This repository holds the hardware: the board, the enclosure, the bill of materials and the fabrication files.

## The device

| | Prototype v0.2.2 |
|---|---|
| Processor | ESP32-S3 (16 MB flash, 8 MB PSRAM), Wi-Fi and Bluetooth LE |
| Display | 7.5" e-ink, 800 × 480, 4 grays, capacitive touch |
| Audio | ES7210 microphone ADC + ES8311 codec with echo cancellation, built-in speaker |
| Controls | Talk, microphone mute and power: three physical buttons. Touch replaces navigation buttons |
| Sensors | Accelerometer, to wake when picked up |
| Power | Works plugged in or on battery |
| Board | 92 × 48 mm, 4 layers |
| Enclosure | Folding desk dock, 3D printed in PETG |

## Status

- **v0.2.2:** the first five assembled boards are in production (November 2026). They have not been tested on the bench yet.
- **Design files:** KiCad sources, BOM, placement files and enclosure models will be published here after the first boards are brought up and validated. Publishing files we have not tested would waste your time and money.

Follow the repository to know when they land.

## How the pieces fit

```
capricorn-hw   the device: board, e-ink, audio, enclosure          (this repository)
capricorn-sw   firmware: xiaozhi-esp32 + a LiveKit (WebRTC) transport
capricorn-app  the family app: set up the device, see progress, privacy controls
     │
     └── talks to a tutor service over LiveKit (Aule runs one; you can run your own)
```

## Principles

- **Open by default.** Hardware, firmware and app are public. If you can buy it, you can build it.
- **Built on standards, not islands.** Firmware based on [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32), voice over [LiveKit](https://github.com/livekit/client-sdk-esp32), common parts you can source anywhere.
- **Children first.** A physical microphone-mute button. Parental consent. Children's data is not used to train models.
- **Repairable.** Standard connectors, a printable enclosure, and a parts list with real part numbers.

## Contributing

Issues and ideas are welcome now. Pull requests for the design will make sense once the source files are published here.

## License

Apache License 2.0. See [LICENSE](LICENSE).

---

Made in Lima, Peru by [Aule](https://meetaule.com) · admin@meetaule.com
