# Nosé–Hoover chains / Nosé–Hoover chain

Status: planned

Couple heat-bath variables to further heat baths in a chain. This extension addresses sampling problems of a single thermostat.

熱浴変数にも別の熱浴を結合し、鎖状の拡張系を作る。単一熱浴での標本化の問題を改善するための発展形。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: ノセ・フーバー鎖, NHC, Nose-Hoover chain

Comparison notes: Chain length, masses and substeps matter. Adding a chain does not universally guarantee ergodicity.

鎖の長さ、質量、サブステップに依存する。鎖を加えるだけで任意の系のエルゴード性を保証するものではない。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://doi.org/10.1063/1.463940 — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.
- Reference: https://docs.lammps.org/fix_nh.html — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/nose-hoover-chains/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
