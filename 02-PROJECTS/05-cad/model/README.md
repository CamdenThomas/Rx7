# 05-cad/model - the scripts that build the car model

*Rev 2026-10-12 · owns: what this folder may hold. The project's design is `../data/`; D-477 opened it.*

Scripts only. The model files, and anything made from a found model, stay out of git (D-477, D-418;
01-REFERENCE block REF.01 and 02-APP P55 are open on where they live). The frame is D-418's:
millimetres, x to the car's right, y forward, z up, ground z = 0, front axle y = 0. Nothing here is a
source of facts about the car: a measured number beats the model, and a dimension nobody measured
carries `confirm` (R11).

| File | What | Record rows |
|---|---|---|
| `coverage.py` | A01: what exists for every 00-CAR part - a model file, a placement in the combined model, a factory dimension, a found model by name (a hint), a catalogue figure, or nothing - derived from the tables each time, never typed back | 00-CAR `parts`, `specs`; 01-REFERENCE `cad`, `blend` |
