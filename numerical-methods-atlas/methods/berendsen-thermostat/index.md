# Berendsen weak-coupling thermostat / Berendsen弱結合サーモスタット

Status: planned

Relax the temperature difference over a chosen coupling time using velocity scaling. Fluctuations are suppressed, so this is not a correct canonical sampler.

目標温度との差を緩和時間で減衰させる速度スケーリング。温度の揺らぎが抑制され、正しい正準分布の生成器にはならない。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: ベルンゼン, Berendsen thermostat, weak coupling

Comparison notes: Treat as a historical relaxation method; do not assume correct NVT fluctuations or response properties.

歴史的な温度緩和法として扱い、NVTでの揺らぎ・応答の測定にはそのまま使わない。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://doi.org/10.1063/1.448118 — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.
- Reference: https://manual.gromacs.org/current/reference-manual/algorithms/molecular-dynamics.html — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/berendsen-thermostat/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
