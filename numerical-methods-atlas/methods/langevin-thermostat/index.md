# Langevin thermostat / Langevinサーモスタット

Status: planned

Add friction and random forces to the equations of motion. The fluctuation–dissipation relation connects friction and noise at the target equilibrium temperature.

摩擦と確率力を運動方程式に加える。平衡の温度を指定するには摩擦と雑音を揺動散逸関係で結ぶ。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: ランジュバン, ランジュヴァン, friction and noise

Comparison notes: Friction changes dynamical correlations and diffusion. Finite-step sampling errors must be assessed together with the integration scheme.

摩擦は実時間の相関・拡散に影響する。有限刻みでの標本化誤差は積分法と刻み幅も含めて調べる。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://doi.org/10.1103/PhysRevE.75.056707 — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.
- Reference: https://docs.lammps.org/fix_langevin.html — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/langevin-thermostat/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
