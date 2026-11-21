# Coulomb and Hartree potentials / Coulomb・Hartreeポテンシャル

Status: educational-example

Solve Poisson for electronic charge with explicit signs, units and boundaries.

電子密度のPoisson解法を、静電気の符号・単位・境界とともに扱う。

Cumulative Coulomb quadrature for isolated spherical densities, checked against analytic exponential densities; not a general 3D or periodic Poisson implementation.

Other names: Hartree potential, 電子密度, Coulomb

Comparison notes: Check the Poisson residual, integrated electron number, far-field behavior and the one-half double-counting factor separately. A charged periodic cell does not directly give an isolated-system energy.

Poisson解の残差、積分した電子数、遠方の挙動、二重計数の1/2を別々に確かめます。周期セルの帯電系を孤立系のエネルギーとして解釈しません。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/quantum-chemistry/#hartree-poisson
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-chemistry/#hartree-poisson



- Reference: https://doi.org/10.1017/S0305004100011919 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.
- Reference: https://doi.org/10.1103/PhysRev.140.A1133 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.

Scoped example: Cumulative Coulomb quadrature for isolated spherical densities, checked against analytic exponential densities; not a general 3D or periodic Poisson implementation.

[
  {
    "id": "helium-ground-state",
    "section": "helium",
    "name": {
      "ja": "He基底状態：閉殻HF・交換のみLDA",
      "en": "Helium ground state: closed-shell HF and exchange-only LDA"
    },
    "result_pointer": "/helium/refinement",
    "figure": "helium.png",
    "reading": {
      "ja": "https://hrkoyama.github.io/numerical-methods-atlas/ja/read/quantum-atoms/#helium",
      "en": "https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-atoms/#helium"
    }
  }
]

Download: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/quantum-atoms-2026-11-21.zip
Verification: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/verification.json
Source: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/atomic_radial.py
Results: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/results/results.json
Commands (from extracted atomic edition):

python -m pytest -q
python run.py --input inputs.json --output output --figures

Next: Small isolated and periodic reference examples.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/hartree-poisson/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
