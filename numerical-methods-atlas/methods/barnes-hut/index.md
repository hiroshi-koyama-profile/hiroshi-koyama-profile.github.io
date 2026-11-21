# Barnes–Hut octree / Barnes–Hut八分木

Status: educational-example

Approximate isolated particle gravity with an octree and cell moments; compare force error with the identical softened direct sum.

粒子を八分木にまとめ、遠方セルの質量モーメントで孤立重力を近似します。直接和と同じ軟化核で力誤差を比べられます。

Static force comparisons only. Target-wise approximation need not conserve pair momentum exactly; interaction counts are not timings. This is not an FMM or TreePM implementation.

- Reading (ja): https://hrkoyama.github.io/numerical-methods-atlas/ja/read/particle-gravity/
- Reading (en): https://hrkoyama.github.io/numerical-methods-atlas/en/read/particle-gravity/

- Code: https://hrkoyama.github.io/code/numerical-methods-atlas/2026-11-21/numart/particle_gravity.py

- Reference: https://doi.org/10.1038/324446a0 — Cited by the linked chapter; inspect its source-review notes before treating this as a method-specific derivation.

Runnable example:

{
  "input": "https://hrkoyama.github.io/code/numerical-methods-atlas/2026-11-21/examples/barnes-hut/input.json",
  "runner": "https://hrkoyama.github.io/code/numerical-methods-atlas/2026-11-21/examples/barnes-hut/run.py",
  "reference": "https://hrkoyama.github.io/code/numerical-methods-atlas/2026-11-21/examples/barnes-hut/reference/result.json",
  "forces": "https://hrkoyama.github.io/code/numerical-methods-atlas/2026-11-21/examples/barnes-hut/reference/forces.csv",
  "command": "python examples/barnes-hut/run.py --input examples/barnes-hut/input.json --output output-barnes-hut",
  "working_directory": "Extracted code edition directory"
}

Source: https://hrkoyama.github.io/numerical-methods-atlas/methods/barnes-hut/
Edition and terms: https://hrkoyama.github.io/numerical-methods-atlas/code-and-data/
