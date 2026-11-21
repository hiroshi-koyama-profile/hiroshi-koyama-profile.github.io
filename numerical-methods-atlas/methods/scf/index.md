# Self-consistent field iteration / SCF / 自己無撞着場反復（SCF）

Status: educational-example

Find a fixed point whose effective-field solution reproduces its input density. The released helium example uses simple linear density mixing and requires density, energy-change and rebuilt orbital-residual criteria together.

密度から作った有効場の解が元の密度と一致する固定点を求める。公開He例は単純な線形密度混合を使い、密度差・エネルギー変化・再構成した軌道残差をすべて判定する。

Energy change alone is insufficient. Electron number staying at two is an imposed consistency check, not independent physical validation. Agreement from alternative starts does not prove uniqueness, orbital stability or a global energy minimum. The Pulay reference is context for an unimplemented acceleration method, not the source of the simple density-mixing implementation.

Other names: 自己無撞着場, self consistency, density mixing

Comparison notes: A small energy change alone is insufficient. Convergence also does not establish the lowest-energy stable electronic solution.

小さいエネルギー変化だけで収束を宣言しません。収束した解が最低エネルギーの安定な電子状態である保証も別に検査します。


## 条件と確認範囲 (ja)

problem: 指定した電子密度依存ハミルトニアンと密度の自己整合固定点を求め、未収束を識別する。

variant: 単純線形密度混合。密度L1差・エネルギー変化・出力密度で再構成した軌道残差のAND条件、履歴保存、反復上限による明示的未収束。

use_when:
- 小さなHeモデルで混合率・初期値・停止基準を比較する。
- 正常終了と数値収束を区別し、反復上限1回の意図的な未収束を扱う。

avoid_when:
- 金属・難収束系や汎用分子SCFで、この混合率と公差が常に適切とみなす。
- 反復が停止した事実だけで安定性・最低エネルギー・物理精度を保証する。

assumptions [specified]:
- 固定点写像は公開する球対称He 1s²のHFまたは交換のみLDA動径モデルであり、汎用の分子・周期系SCF実装ではない。
- 入力・出力の動径電子数密度をp_next=(1−α)p_in+αp_out（0<α≤1）で混合。公開基本値α=0.35、別の初期値では0.7も用いる。
- 各固有値問題でuを規格化しp_out=2|u|²とするため、電子数の規格化は反復内で課している。
- 密度の入出力L1差<10⁻⁹電子数、|エネルギー変化|<10⁻¹⁰hartree、出力密度で再構成した軌道残差<10⁻⁷hartreeをすべて要求。最大300反復。
- アトラス側の反復にDIIS・Anderson・Newton加速は未採用。独立PySCF参照は独自のソルバーを使いうる。
heliumの密度更新式、停止の3条件と反復上限を確認。

units [specified]:
混合率αと反復回数は無次元。pはbohr⁻¹、∫|p_out−p_in|drは電子数、エネルギー変化と規格化した軌道残差はhartree。公開公差はこの規格化とモデルに対する値。
混合率の無次元性と残差ごとの単位・規格化を明記。

boundary_conditions [not-applicable]:
SCF混合そのものに空間境界条件はない。与えたHe固定点写像が縮約軌道u(0)=u(r_max)=0と、原点で有限・遠方N/rの孤立Hartree場を規定する。HF・KS・Hartree項目を参照。
混合アルゴリズム自体には境界がなく、Heの固定点写像が空間境界を与える。

limitations [specified]:
エネルギー変化だけで収束を宣言しない。電子数が2に保たれることは実装の整合性検査であり、独立な物理検証ではない。異なる初期値での一致も解の一意性・軌道安定性・大域的最低エネルギーを証明しない。Pulay文献は未採用の加速法の文脈用で、単純密度混合の実装出典ではない。
DIIS未実装、正規化と独立検証の差、収束と安定性の差を明記。

Review: 既存公開版の実装・検査・保存結果を読んだ点検であり、この点検では再実行していません。heliumの入力密度混合・3条件の収束判定、初期値比較とmax_iterationsの検査、保存反復履歴・意図的未収束を確認。

Not checked:
- 新規再実行、DIIS・Anderson・Newton法や周期金属系の収束挙動は検証していない。
- 固定点の全解・軌道安定性を網羅する解析はない。

Evidence:
- helium: linear input-density mixing; joint stopping conditions; reason/max_iterations: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/atomic_radial.py
- test_alternative_start_and_explicit_nonconvergence; test_helium_scf_and_independent_reference: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/test_atomic_radial.py
- helium mixing, alternative start, three tolerances and iteration limit: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/inputs.json
- helium.scf_histories; helium.alternative_starts; helium.expected_nonconvergence: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/results/results.json

References:
- [formulation / primary-research] Kohn, W. and Sham, L. J. (1965). Self-Consistent Equations Including Exchange and Correlation Effects. — https://doi.org/10.1103/PhysRev.140.A1133
  密度依存有効場の自己無撞着方程式の文脈。公開混合率・停止公差の出典ではない。
  abstract-and-metadata (2026-11-22); Publisher Abstract and bibliographic record; full paper not read; https://journals.aps.org/pr/abstract/10.1103/PhysRev.140.A1133
- [context / primary-research] Roothaan, C. C. J. (1951). New Developments in Molecular Orbital Theory. — https://doi.org/10.1103/RevModPhys.23.69
  分子軌道SCFの書誌的な入口。公開する動径He反復そのものではない。
  metadata (2026-11-22); Publisher bibliographic record; abstract/full paper not available in retrieved view; https://journals.aps.org/rmp/abstract/10.1103/RevModPhys.23.69
- [context / primary-research] Pulay, P. (1980). Convergence acceleration of iterative sequences. The case of SCF iteration. — https://doi.org/10.1016/0009-2614(80)80396-4
  DIIS系の収束加速との比較用。公開Heソルバーでは採用していない。
  abstract-and-metadata (2026-11-22); Publisher-indexed abstract and bibliographic record; subsequent direct open returned HTTP 403; full paper not read; https://www.sciencedirect.com/science/article/pii/0009261480803964

## Conditions and review scope (en)

problem: Find a self-consistent fixed point of a specified density-dependent Hamiltonian and identify failure.

variant: Simple linear density mixing; joint density-L1, energy-change and output-density-rebuilt orbital-residual criteria, saved histories and explicit iteration-limit failure.

use_when:
- Compare mixing rates, starts and stopping criteria in a small helium model.
- Distinguish process completion from convergence, including an intentional one-iteration failure.

avoid_when:
- Assuming the same mixing and tolerances are generally suitable for metals, difficult systems or molecular SCF.
- Using iteration termination alone to establish stability, minimum energy or physical accuracy.

assumptions [specified]:
- The fixed-point map is the released spherical He 1s² HF or exchange-only LDA radial model, not a general molecular or periodic SCF implementation.
- Mix input and output radial number densities: p_next=(1-alpha)p_in+alpha p_out, 0<alpha<=1; released baseline alpha=0.35 and an alternative start uses 0.7.
- Each eigenproblem normalizes u and sets p_out=2|u|^2, so the electron-number normalization is imposed within the iteration.
- Convergence requires input/output density L1<1e-9 electrons, |energy change|<1e-10 hartree, and the output-density-rebuilt orbital residual<1e-7 hartree; maximum 300 iterations.
- The atlas iteration implements no DIIS, Anderson or Newton acceleration. An independent PySCF reference may use its own solver algorithms.
Inspected helium's density update, three stopping criteria and iteration cap.

units [specified]:
Mixing alpha and iteration number are dimensionless. Radial p is in bohr^(-1), integral |p_out-p_in| dr is electron number, and energy changes/normalized orbital residuals are in hartree. Published tolerances belong to this normalization and model.
Specified dimensionless mixing and normalization/units of each residual.

boundary_conditions [not-applicable]:
SCF mixing itself imposes no spatial boundary condition. The supplied helium fixed-point map uses reduced-orbital u(0)=u(r_max)=0 and an isolated finite-origin, N/r Hartree field; see the HF/KS/Hartree records.
Mixing has no intrinsic spatial boundary; the helium fixed-point map supplies it.

limitations [specified]:
Energy change alone is insufficient. Electron number staying at two is an imposed consistency check, not independent physical validation. Agreement from alternative starts does not prove uniqueness, orbital stability or a global energy minimum. The Pulay reference is context for an unimplemented acceleration method, not the source of the simple density-mixing implementation.
Distinguished absent DIIS, imposed normalization versus independent checks, and convergence versus stability.

Review: This inspection reads the released implementation, tests and saved results; it does not rerun the calculation. Inspected helium's input-density mixing and joint stopping test, alternative-start/max_iterations tests, saved histories and intentional nonconvergence.

Not checked:
- No new run or verification of DIIS/Anderson/Newton methods or periodic-metal convergence.
- No exhaustive stationary-solution or orbital-stability analysis.

Evidence:
- helium: linear input-density mixing; joint stopping conditions; reason/max_iterations: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/atomic_radial.py
- test_alternative_start_and_explicit_nonconvergence; test_helium_scf_and_independent_reference: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/test_atomic_radial.py
- helium mixing, alternative start, three tolerances and iteration limit: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/inputs.json
- helium.scf_histories; helium.alternative_starts; helium.expected_nonconvergence: https://hrkoyama.github.io/code/quantum-atoms/2026-11-21/results/results.json

References:
- [formulation / primary-research] Kohn, W. and Sham, L. J. (1965). Self-Consistent Equations Including Exchange and Correlation Effects. — https://doi.org/10.1103/PhysRev.140.A1133
  Self-consistent density-dependent equations; not the source of the released mixing parameter or stopping tolerances.
  abstract-and-metadata (2026-11-22); Publisher Abstract and bibliographic record; full paper not read; https://journals.aps.org/pr/abstract/10.1103/PhysRev.140.A1133
- [context / primary-research] Roothaan, C. C. J. (1951). New Developments in Molecular Orbital Theory. — https://doi.org/10.1103/RevModPhys.23.69
  Bibliographic entry point for molecular-orbital SCF, not the released radial helium iteration.
  metadata (2026-11-22); Publisher bibliographic record; abstract/full paper not available in retrieved view; https://journals.aps.org/rmp/abstract/10.1103/RevModPhys.23.69
- [context / primary-research] Pulay, P. (1980). Convergence acceleration of iterative sequences. The case of SCF iteration. — https://doi.org/10.1016/0009-2614(80)80396-4
  Context for DIIS-type convergence acceleration; not adopted by the released helium solver.
  abstract-and-metadata (2026-11-22); Publisher-indexed abstract and bibliographic record; subsequent direct open returned HTTP 403; full paper not read; https://www.sciencedirect.com/science/article/pii/0009261480803964


- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/quantum-chemistry/#scf
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/quantum-chemistry/#scf



- Reference: https://doi.org/10.1103/PhysRev.140.A1133 — Self-consistent density-dependent equations; not the source of the released mixing parameter or stopping tolerances.
- Reference: https://doi.org/10.1103/RevModPhys.23.69 — Bibliographic entry point for molecular-orbital SCF, not the released radial helium iteration.
- Reference: https://doi.org/10.1016/0009-2614(80)80396-4 — Context for DIIS-type convergence acceleration; not adopted by the released helium solver.

Scoped example: Helium linear density mixing with density/energy/orbital-residual checks, alternative starts/mixing and explicit failure; no DIIS.

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

Next: A baseline recording electron number, residuals and energy changes.

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/scf/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
