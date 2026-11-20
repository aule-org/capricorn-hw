# Software

The firmware for Aule lives in [meet-aule/aule-fw](https://github.com/meet-aule/aule-fw), a fork of [xiaozhi-esp32](https://github.com/78/xiaozhi-esp32) with a LiveKit transport.

This folder holds the contract between the board and the firmware: which pin does what.

| File | What it covers |
|---|---|
| [`aule-v0.2.2-config.h`](aule-v0.2.2-config.h) | What is specific to the Aule board: e-ink panel (SPI), capacitive touch (second I²C bus), microphone mute, talk button |
| [`capri-mini-config.h`](capri-mini-config.h) | What Aule shares with the base audio board: audio codecs and I²S, the audio I²C bus, power, LEDs, accelerometer |

Both are board contracts for integration and testing, not drivers. Comments are in Spanish.
