# Lowe–Andersen thermostat / Lowe–Andersenサーモスタット

Status: planned

Stochastically redraw a component of a nearby pair’s relative velocity while preserving the pair’s center-of-mass momentum.

近傍粒子対の相対速度の一成分を確率的に再抽選し、対の重心運動量を保つ衝突型の温度制御。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: ロウ・アンダーセン, Lowe Andersen

Comparison notes: Distinguish from independent-particle Andersen collisions. Collision frequency and neighbor radius affect transport such as viscosity and diffusion.

独立な粒子速度を引き直すAndersen法と区別する。衝突頻度や近傍半径は粘性・拡散などの輸送に影響する。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://doi.org/10.1209/epl/i1999-00365-x — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/lowe-andersen/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
