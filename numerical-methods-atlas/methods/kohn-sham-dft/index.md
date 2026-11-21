# Kohn–Sham density functional theory / DFT / Kohn–Sham密度汎関数法

Status: educational-example

Connect density, effective potential, exchange-correlation approximations and SCF.

密度・有効ポテンシャル・交換相関近似とSCFをつなぐ。

Spin-unpolarized exchange-only Dirac LDA for spherical helium; correlation, GGA, hybrids, molecules, periodic systems and excitations are not implemented.

Other names: DFT, 密度汎関数法, 密度汎関数理論, コーン・シャム, density functional theory

Comparison notes: Distinguish exact-functional theory from calculations with approximate functionals. KS eigenvalues are not generally excitation energies; ground-state DFT alone does not guarantee excited-state accuracy.

正確な汎関数の理論と、近似汎関数による実計算を分けます。KS固有値を一般に励起エネルギーと同一視せず、基底状態DFTだけで励起状態まで保証しません。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/quantum-chemistry/#kohn-sham-dft
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-chemistry/#kohn-sham-dft



- Reference: https://doi.org/10.1103/PhysRev.136.B864 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.
- Reference: https://doi.org/10.1103/PhysRev.140.A1133 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.

Scoped example: Spin-unpolarized exchange-only Dirac LDA for spherical helium; correlation, GGA, hybrids, molecules, periodic systems and excitations are not implemented.

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

Next: A small reproducible case with a specified exchange-correlation model.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/kohn-sham-dft/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
