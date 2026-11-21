# Numerical Methods Atlas code edition 2026 11 22

Public source, tests and the small stored dataset required by the tests.
This source-only edition contains no original Git history, private manuscripts,
source-paper PDFs, credentials, movie archive or production simulation code.

## Run

With Python 3.9 or later, create and activate a virtual environment, then run
these commands from this directory. Python 3.12 is used for the release check.

```sh
python -m pip install -r requirements.txt
python -m pytest -q
python -m numart.cli --help
```

For a quick, bounded gravity check:

```sh
python -m pytest -q tests/test_particle_gravity.py
```

Use the corresponding chapter to read assumptions, boundaries, units and
verification limits: https://hrkoyama.github.io/numerical-methods-atlas/ .
The Barnes–Hut tests use isolated softened gravity; the FFT PM tests use periodic
boundaries. Neither is a PME/SPME or a coupled TreePM implementation.
Tests and educational examples do not establish production suitability or
reproduction of every result in the cited literature.

## Fixed-input representative recipes

This edition adds twelve fixed-input adapters around the unchanged educational
Numart implementations from edition 2026-11-21. The earlier edition stays public.
The existing Barnes–Hut and quantum-atoms recipes retain their original editions.

Run one JSON input from the edition directory into a new, empty output directory:

```sh
python run_recipe.py --input recipes/advection-sine.json --output output-advection
```

Available inputs: advection-sine, sod, shu-osher, poisson-1d-dirichlet,
poisson-2d-sine, bratu, harmonic-oscillator, stiff-cosine,
smooth-function-projection, periodic-particles, taylor-green, brio-wu.
The complete problem, grids/time steps, model conventions and acceptance
conditions are recorded in each JSON file. A changed input is a new experiment,
not a reproduction of the packaged reference. These are existing atlas problems,
not twelve additions to the atlas-wide count of sixty independent problems.

Each run produces `result.json` (input SHA-256, actual parameters, numerical
metrics, per-criterion decisions and a pass/fail status) and `solution.csv`
(computed fields and references on the documented grid). Exit 0 means the
specified acceptance tests passed; exit 1 means numerical acceptance failed;
exit 2 means an invalid input, computation error or unsafe output location.
The CLI refuses to overwrite a nonempty output directory. Inspect `details`
for table layout, reference provenance and case-specific restrictions.

`reference/<problem-id>/` holds outputs actually generated from the shipped
input. Analytic references, high-resolution comparisons using the same solver,
conservation and residual tests have different meanings. In particular,
Shu–Osher and Brio–Wu refinement comparisons are empirical numerical references,
not exact solutions or independent solver implementations. The PM example is
periodic gravity, not isolated direct gravity or PME/SPME.

Normal site refreshes read these stored outputs; they do not rerun simulations.
New packaged source and independent-extraction verification are identified by
`source-manifest.json` and `verification.json`. The public execution registry
also records a later run using only publicly downloaded artifacts.

## Version and citation

source-manifest.json identifies every packaged file by SHA-256 and records the
reviewed source revision. Retain that edition, input settings and original
method references when citing a computation. Release verification is published
separately, so packaging does not imply that a particular test was executed.

## Rights

Original implementation code is MIT within LICENSE and LICENSING.md. Stored
datasets, explanatory prose and generated outputs have separate terms; the
code license does not relicense them. External dependencies are installed
separately and keep their own licenses. No third-party paper is bundled.
Usage and citation: https://hrkoyama.github.io/using/ .

## Fixed input gravity example

The stored input contains explicit coordinates and masses for 192 particles.
From this directory run:

```sh
python examples/barnes-hut/run.py --input examples/barnes-hut/input.json --output output-barnes-hut
```

The output contains result.json with source/input hashes and checks, and
forces.csv with tree and direct accelerations. examples/barnes-hut/reference/
contains the reference output. These are static isolated softened-force
comparisons, with G=1; they are not periodic gravity or orbit integrations.
