# Self-consistent field iteration / SCF / 自己無撞着場反復（SCF）

Status: reading-only

Iterate densities or effective potentials and diagnose convergence or failure.

密度や有効ポテンシャルを反復し、収束と未収束を診断する。

Introductory bilingual reading, representative equations and primary references are available. No dedicated implementation or numerical verification result is provided yet. A small energy change alone is insufficient. Convergence also does not establish the lowest-energy stable electronic solution.

Other names: 自己無撞着場, self consistency, density mixing

Comparison notes: A small energy change alone is insufficient. Convergence also does not establish the lowest-energy stable electronic solution.

小さいエネルギー変化だけで収束を宣言しません。収束した解が最低エネルギーの安定な電子状態である保証も別に検査します。

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/quantum-chemistry/#scf
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-chemistry/#scf



- Reference: https://doi.org/10.1103/RevModPhys.23.69 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.
- Reference: https://doi.org/10.1016/0009-2614(80)80396-4 — Primary publication entry point for the quantum-chemistry overview. Bibliographic/introductory review only; full-paper equations and numerical results have not been reproduced.

Next: A baseline recording electron number, residuals and energy changes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/scf/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
