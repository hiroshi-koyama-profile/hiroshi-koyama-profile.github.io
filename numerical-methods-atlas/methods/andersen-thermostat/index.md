# Andersen thermostat / Andersenサーモスタット

Status: planned

Represent stochastic heat-bath collisions by redrawing selected particle velocities from a Maxwell–Boltzmann distribution.

熱浴との確率的衝突を表し、選ばれた粒子の速度をMaxwell–Boltzmann分布から引き直す。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: アンダーセン, stochastic collisions

Comparison notes: Canonical sampling and physical time correlations are separate criteria. Independent velocity redraws alter total momentum and transport.

正準分布の標本化と物理的な時間相関は別の評価軸。独立な速度再抽選は全運動量や輸送特性を変える。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://doi.org/10.1063/1.439486 — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.
- Reference: https://manual.gromacs.org/current/reference-manual/algorithms/molecular-dynamics.html — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/andersen-thermostat/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
