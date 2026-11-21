# Nosé–Hoover thermostat / Nosé–Hooverサーモスタット

Status: planned

A deterministic method with a dynamically adjusted heat-bath friction variable. The canonical distribution is invariant, but small systems can fail to explore it ergodically.

熱浴変数により摩擦係数を動的に調整する決定論的手法。正準分布を不変分布に持つが、小自由度系では十分に探索できない場合がある。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: のせフーバー, ノセフーバー, ノセ・フーバー, 能勢・フーバー, Nose-Hoover

Comparison notes: Check nonergodicity in systems such as harmonic oscillators and dependence on bath mass or coupling time. Mean temperature is insufficient validation.

調和振動子などでの非エルゴード性、熱浴質量・結合時間の依存性を確認する。温度の平均値だけを合格条件にしない。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://doi.org/10.1103/PhysRevA.31.1695 — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.
- Reference: https://manual.gromacs.org/current/reference-manual/algorithms/molecular-dynamics.html — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/nose-hoover/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
