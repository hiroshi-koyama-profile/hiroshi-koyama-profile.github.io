# FFT particle–mesh forces / FFT粒子格子力

Status: educational-example

Deposit mass with CIC, solve periodic Poisson with FFTs and interpolate forces back to particles.

CICで格子へ質量を割り当て、FFTで周期Poisson方程式を解き、粒子へ力を戻す例です。

A mesh-Poisson and particle-coupling example; not a near-pair direct-sum benchmark or an Ewald, PME or SPME implementation.

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/particle-gravity/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/particle-gravity/

- Code: https://hrkoyama.github.io/code/numerical-methods-atlas/2026-11-21/numart/particle_gravity.py

- Reference: https://doi.org/10.1038/324446a0 — Cited by the linked chapter; inspect its source-review notes before treating this as a method-specific derivation.
- Reference: https://doi.org/10.1016/0021-9991(87)90140-9 — Cited by the linked chapter; inspect its source-review notes before treating this as a method-specific derivation.
- Reference: https://arxiv.org/abs/astro-ph/0505010 — Cited by the linked chapter; inspect its source-review notes before treating this as a method-specific derivation.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/pm/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
