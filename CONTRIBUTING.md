# Contributing to Capricorn Hardware

Thank you for helping build an open AI tutor for children. Capricorn combines electronics, mechanical design, firmware and teaching, so clear contributions matter. Issues and pull requests are welcome in English or Spanish.

## Ways to contribute

- Report problems building, ordering, printing or assembling the device.
- Share results from real builds: measurements, photos, what worked and what did not. This is the most valuable contribution while the design is a prototype.
- Improve documentation, diagrams and assembly notes, or translate them.
- Propose equivalent parts, better sourcing or corrected prices for the [BOM](bom/README.md), especially from suppliers outside China.
- Adapt the enclosure to other panels, printers or classrooms.
- Contribute firmware in [aule-org/capricorn-sw](https://github.com/aule-org/capricorn-sw) and the family app in [aule-org/capricorn-app](https://github.com/aule-org/capricorn-app).

## Before you start

Small fixes can go straight to a pull request. For larger changes, open an issue first so we can agree on the intent, compatibility and how to validate it. Larger changes include:

- Any change to the schematic or the layout.
- Part substitutions that affect footprints, power, audio or the e-ink booster.
- Changes to the enclosure geometry shared by several parts.
- Anything that touches how the device listens, records or stores audio.

## Hardware changes

- Use **KiCad 10** and keep the project rules in `hardware/pcb/esp32-audio-module.kicad_dru`.
- Run DRC and ERC and attach the reports. A change should not add errors.
- Regenerate the files in `hardware/fab/` from the same commit, and say what you changed in the BOM and CPL.
- Every part needs an orderable LCSC number. If you change a part, include its datasheet link and stock at the time.
- Say what you measured on a real board and what you did not. "Not tested" is a fine answer; an unstated one is not.

## Enclosure changes

- Edit `hardware/enclosure/dock.py`, not the exported STEP or STL files, and regenerate them.
- `dock.py` and `printcheck.py` must still pass.

## Children's safety and privacy

Capricorn is used by children. Changes must keep the physical microphone mute working in hardware, keep batteries protected (charger limits, thermal cut-off) and avoid small detachable parts. When in doubt, open an issue.

## License

By contributing, you agree that your contribution is released under the [Apache License 2.0](LICENSE).
