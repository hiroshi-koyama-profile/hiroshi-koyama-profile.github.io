# Hartree–Fock / Hartree–Fock法

Status: reading-only

Study exchange-containing mean-field models and molecular SCF calculations.

交換を含む平均場と、基底を用いた分子のSCF計算を扱う。

Introductory bilingual reading, representative equations and primary references are available. No dedicated implementation or numerical verification result is provided yet. HF solutions need not be unique. SCF termination does not prove basis convergence, orbital stability or the desired electronic state. Bond dissociation can expose single-reference limitations.

Other names: HF, RHF, UHF, ROHF, ハートリー・フォック

Comparison notes: HF solutions need not be unique. SCF termination does not prove basis convergence, orbital stability or the desired electronic state. Bond dissociation can expose single-reference limitations.

HFの解は一般に一意とは限りません。SCFが停止しても基底収束・軌道安定性・正しい電子状態の確認が必要です。分子解離では単一参照の限界が現れます。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/quantum-chemistry/#hartree-fock
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-chemistry/#hartree-fock



- Reference: https://doi.org/10.1103/RevModPhys.23.69 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.

Next: Small-molecule minimal-basis inputs checked against an independent reference.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/hartree-fock/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
