# Direct velocity rescaling / 単純な速度スケーリング

Status: planned

Multiply velocities by a common factor to set the kinetic energy at each application. Simple deterministic rescaling does not reproduce canonical kinetic-energy fluctuations.

全粒子の速度に共通係数を掛け、適用時の運動エネルギーを目標値に合わせる。単純な決定論的操作では正準分布の運動エネルギー揺らぎを再現しない。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: ベロシティースケーリング, ベロシティスケーリング, velocity scaling, simple velocity rescaling

Comparison notes: A comparison case for distinguishing temperature control from canonical sampling. Ratio-based rescaling is undefined at T=0; the application interval also matters.

温度への到達と正準分布の標本化を区別するための比較対象。T=0では比による再スケーリングを定義できず、適用間隔も結果に影響する。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://manual.gromacs.org/current/reference-manual/algorithms/molecular-dynamics.html — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/velocity-rescaling/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
