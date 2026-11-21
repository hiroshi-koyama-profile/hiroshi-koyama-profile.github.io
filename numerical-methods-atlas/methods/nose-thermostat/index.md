# Nosé extended-system thermostat / Noséの拡張系

Status: planned

Introduce additional heat-bath degrees of freedom and time scaling: a starting point for deterministic constant-temperature molecular dynamics.

熱浴を表す追加自由度と時間のスケーリングを導入する、決定論的な定温度分子動力学の出発点。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: ノセ, 能勢, Nose thermostat, extended system

Comparison notes: Distinguish the original extended Hamiltonian from the real-time Nosé–Hoover equations. An invariant distribution alone does not establish ergodicity.

元の拡張Hamiltonianと実時間でのNosé–Hoover方程式を区別する。分布の不変性だけでは軌道のエルゴード性は保証されない。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://doi.org/10.1063/1.447334 — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/nose-thermostat/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
