# Generalized Langevin equation (GLE) / 一般化Langevin・GLE

Status: planned

Use memory kernels and colored noise, or auxiliary variables representing them, to tailor the frequency response of a heat bath.

記憶核と有色雑音、またはそれを表す補助変数を使い、周波数ごとの熱浴応答を設計する。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: 一般化ランジュバン, colored-noise thermostat, 有色雑音

Comparison notes: Separate classical equilibrium fluctuation–dissipation settings from nonequilibrium approximations to nuclear quantum effects; neither is an electronic-structure solver.

古典平衡用の揺動散逸関係と、核の量子効果を近似する非平衡設定を分ける。量子化学ソルバーそのものではない。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://doi.org/10.1103/PhysRevLett.102.020601 — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.
- Reference: https://docs.lammps.org/fix_gle.html — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/generalized-langevin/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
