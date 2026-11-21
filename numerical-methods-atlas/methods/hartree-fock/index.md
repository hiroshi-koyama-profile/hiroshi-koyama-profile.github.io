# Hartree–Fock / Hartree–Fock法

Status: educational-example

Study exchange-containing mean-field models and molecular SCF calculations.

交換を含む平均場と、基底を用いた分子のSCF計算を扱う。

Only spherical helium with one doubly occupied 1s spatial orbital; the local HF exchange reduction is specific to this two-electron problem.

Other names: HF, RHF, UHF, ROHF, ハートリー・フォック

Comparison notes: HF solutions need not be unique. SCF termination does not prove basis convergence, orbital stability or the desired electronic state. Bond dissociation can expose single-reference limitations.

HFの解は一般に一意とは限りません。SCFが停止しても基底収束・軌道安定性・正しい電子状態の確認が必要です。分子解離では単一参照の限界が現れます。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/quantum-chemistry/#hartree-fock
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-chemistry/#hartree-fock



- Reference: https://doi.org/10.1103/RevModPhys.23.69 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.

Scoped example: Only spherical helium with one doubly occupied 1s spatial orbital; the local HF exchange reduction is specific to this two-electron problem.

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

Next: Small-molecule minimal-basis inputs checked against an independent reference.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/hartree-fock/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
