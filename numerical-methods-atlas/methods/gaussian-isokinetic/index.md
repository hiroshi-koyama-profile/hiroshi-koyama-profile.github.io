# Gaussian isokinetic thermostat / Gaussian isokineticサーモスタット

Status: planned

Constrain kinetic energy continuously using a constraint force, connecting nonequilibrium molecular dynamics with constrained mechanics.

拘束力により運動エネルギーを連続時間で一定に保つ。非平衡分子動力学と拘束力学を結ぶ手法。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: ガウス等運動エネルギー, isokinetic constraint

Comparison notes: Distinguish fixed kinetic energy from the fluctuating canonical kinetic energy at finite system size. Configurational and full phase-space distributions differ.

有限自由度で運動エネルギーが揺らぐ正準分布とは区別する。配置分布と位相空間全体の分布を混同しない。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://press-files.anu.edu.au/downloads/press/p47571/html/ch05s02.html — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/gaussian-isokinetic/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
