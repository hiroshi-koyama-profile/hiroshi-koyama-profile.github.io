# LDA, GGA and hybrid functionals / LDA・GGA・hybrid汎関数

Status: educational-example

Separate exchange-correlation model choices from numerical errors.

交換相関近似を、数値誤差と物理近似の違いを保って整理する。

Only spin-unpolarized Dirac exchange energy and its functional derivative are verified; LDA correlation, GGA, meta-GGA and hybrids remain reading-only.

Other names: LDA, GGA, meta-GGA, hybrid, PBE, PBE0, SCAN, B3LYP, 交換相関汎関数

Comparison notes: Basis, grid and SCF convergence do not remove functional error. Assess self-interaction, charge transfer, strong correlation and dispersion for the chosen system and approximation.

基底・格子・SCFが収束しても汎関数の近似誤差は消えません。自己相互作用、電荷移動、強相関、分散の扱いは対象と近似に応じて評価します。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/quantum-chemistry/#xc-functionals
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-chemistry/#xc-functionals



- Reference: https://doi.org/10.1017/S0305004100016108 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.
- Reference: https://doi.org/10.1103/PhysRevLett.77.3865 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.
- Reference: https://doi.org/10.1103/PhysRevLett.115.036402 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.
- Reference: https://doi.org/10.1063/1.464913 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.
- Reference: https://doi.org/10.1063/1.478522 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.

Scoped example: Only spin-unpolarized Dirac exchange energy and its functional derivative are verified; LDA correlation, GGA, meta-GGA and hybrids remain reading-only.

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

Common execution records: [{"id": "helium-ground-state", "registry_url": "https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/examples.json", "guide": {"ja": "https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/?lang=ja#helium-ground-state-ja", "en": "https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/?lang=en#helium-ground-state-en"}}]

Next: Document functional, grid, basis and primary references.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/xc-functionals/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
