# Schrodinger eigenproblems / Schrödinger固有値問題

Status: educational-example

Start with one-electron discretization, eigenvalues and eigenfunctions.

1電子の問題から離散化と固有値・固有関数の誤差を調べる。

Uniform radial-grid tests of isolated hydrogenic 1s, 2s, 2p and 3d states; not a direct general many-electron Schrödinger solver.

Other names: シュレーディンガー, Schrödinger equation, electronic Hamiltonian

Comparison notes: Nuclear dynamics, relativity, spin–orbit coupling and external fields are outside this representative Hamiltonian. A small eigenpair residual does not establish domain or basis convergence.

核運動、相対論、スピン軌道相互作用、外場はこの代表式に含めません。固有値の残差が小さくても、領域・基底の誤差は残ります。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/quantum-chemistry/#schrodinger
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-chemistry/#schrodinger



- Reference: https://doi.org/10.1002/andp.19263840404 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.
- Reference: https://doi.org/10.1103/RevModPhys.23.69 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.

Scoped example: Uniform radial-grid tests of isolated hydrogenic 1s, 2s, 2p and 3d states; not a direct general many-electron Schrödinger solver.

[
  {
    "id": "hydrogenic-atoms",
    "section": "hydrogenic",
    "name": {
      "ja": "水素型原子の動径固有値問題",
      "en": "Hydrogenic radial eigenproblems"
    },
    "result_pointer": "/hydrogenic/refinement",
    "figure": "hydrogenic.png",
    "reading": {
      "ja": "https://hrkoyama.github.io/numerical-methods-atlas/ja/read/quantum-atoms/#hydrogenic",
      "en": "https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-atoms/#hydrogenic"
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

Next: Separate domain and resolution errors for oscillator and hydrogenic models.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/schrodinger/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
