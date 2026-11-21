# Stochastic velocity rescaling (CSVR) / 確率的速度リスケーリング（CSVR）

Status: planned

Use a stochastic global scale factor designed to generate canonical kinetic-energy fluctuations. This is distinct from directly fixing the kinetic energy.

全体の速度に確率的な係数を掛け、正準分布の運動エネルギー揺らぎを生成するよう設計する。単純な速度固定とは別手法。

Comparative reading is available. No dedicated implementation or numerical verification result is provided yet.

Other names: Bussi–Donadio–Parrinello, Bussi thermostat, v-rescale, canonical velocity rescaling, 確率的速度スケーリング

Comparison notes: Assess equilibrium distributions separately from real-time dynamics. State the coupling time, integration step and degree-of-freedom count.

分布の正しさと実時間の運動の再現を別々に調べる。結合時間・積分刻み・自由度数を明記する。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/thermostats/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/thermostats/



- Reference: https://doi.org/10.1063/1.2408420 — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.
- Reference: https://arxiv.org/abs/0803.4060 — Bibliographic entry and introductory comparison; full derivation and numerical reproduction have not been audited.

Next: Add a dedicated formulation and integration recipe, followed by explicit-input distribution and time-correlation checks with stated degrees of freedom, random seeds and step sizes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/stochastic-velocity-rescaling/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
