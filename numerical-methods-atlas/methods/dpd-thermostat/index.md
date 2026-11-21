# DPD pair thermostat / DPDサーモスタット

Status: planned

Control temperature using dissipative and random pair forces. Standard symmetric pair forces conserve the pair’s total momentum.

粒子対に散逸力と確率力を加えて温度を制御する。標準的な対称な対力は対の全運動量を保存する。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: 散逸粒子動力学, dissipative particle dynamics, pairwise thermostat

Comparison notes: Relevant when momentum transport matters. Verify matched friction/noise, radial weights and finite-step effects.

流体的な運動量輸送を扱う場合の候補。摩擦・雑音の対応、距離重み、有限刻みの影響を検証する。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://doi.org/10.1209/0295-5075/30/4/001 — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.
- Reference: https://docs.lammps.org/pair_dpd.html — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/dpd-thermostat/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
