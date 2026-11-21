# Hydrogenic atoms and helium: reproducible radial examples

Edition: 2026-11-21. Python 3.10 or later; measured with Python 3.12.14.
This is a small educational implementation, with fixed inputs and explicit limits.
It is not a molecular/periodic or general many-electron HF/DFT package.

## Run

Extract the archive into a new directory and change into that directory.
Use your own Python environment, then:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest -q
python run.py --input inputs.json --output output --figures
```

`run.py` uses the included, previously computed independent reference and requires
no network, API key, ChatGPT or Codex. Without `--figures`, NumPy and SciPy suffice.
The output contains `results.json`, complete finest-grid profiles as CSV, and,
with plotting enabled, four PNGs. An unconverged SCF calculation is explicitly
reported, not relabeled as a valid ground-state result.

To rerun the independent Gaussian-basis reference:

```sh
python -m pip install -r requirements-reference.txt
python reference_pyscf.py --input inputs.json --output new-reference.json
python run.py --reference new-reference.json --output independently-checked --figures
```

The reference script imports no `atomic_radial` or atlas SCF/Hartree/XC function.
It uses PySCF 2.11.0 and Libxc's `LDA_X,` (exchange only), with all exponents,
basis sizes, quadrature grids, spin, charge and stopping parameters in the input.
The optional OpenMP warning on systems without OpenMP does not affect the physics;
no timing or parallel performance claim is made.

## Equations and conventions

Atomic units: hbar=m_e=e=4*pi*epsilon_0=1. Energies are in hartree and radii in bohr.
Nuclei are pointlike, fixed and infinitely heavy. No relativistic or finite-mass
correction is included. At interior radial nodes the reduced orbital u=r*R obeys
u(0)=u(r_max)=0, integral |u|^2 dr=1. Second-order central differences give the
symmetric tridiagonal kinetic matrix; angular momentum adds l(l+1)/(2*r^2).

The one-electron potential is -Z/r. Exact energies are -Z^2/(2*n^2); analytic
Laguerre radial orbitals also provide a shape reference. The input covers H and
He+ with 1s, 2s, 2p and 3d states. These state/charge/resolution variants are one
hydrogenic test-problem family in the atlas inventory. Domain studies keep the
radial spacing fixed, separating finite-box and mesh errors.

Helium is a closed-shell 1s^2 singlet with Z=2, two opposite-spin electrons and
one common real s orbital. There is only one nucleus, so E_NN=0. Write
p(r)=4*pi*r^2*n(r)=2*u(r)^2, integral p dr=2, with n a positive number density.
The positive Hartree potential is integral p(s)/max(r,s) ds and
E_H=(1/2)*integral p*v_H dr. Cumulative quadrature counts the diagonal sample once.

For this **specific two-electron, single-orbital HF case**, exchange cancels half
the Hartree term: v_eff=-2/r+v_H/2 and E_x=-E_H/2. This local reduction is not a
general local representation of the HF exchange operator.

For spin-unpolarized exchange-only LDA,
v_x=-(3*n/pi)^(1/3) and E_x=(3/4)*integral p*v_x dr. The potential and energy are
functional derivatives of the same discrete density expression. Correlation is
zero. This is not LDA+VWN, PBE, a hybrid, or exact correlated helium.

Total energy is T_s+V_nuc+E_H+E_x. The reported orbital energy is a Rayleigh
quotient in the field rebuilt from the output density. Both its residual and
the input-output density L1 residual are checked. SCF stops only when density,
energy-change and orbital-residual criteria all pass. Electron number is imposed
by normalization and checked; this does not independently establish model accuracy.

The independent reference uses variational even-tempered s-Gaussian bases of
24, 32 and 40 functions. The LDA reference also refines radial/angular quadrature.
It is a finite-basis/quadrature reference, not an exact answer. Compare raw
finite-difference results separately from an h^2 Richardson extrapolation.
The extrapolation is a consistency estimate, not a certified error bound.

## Scope of checks

Analytic energies and shapes; charge scaling; orthogonality; domain and grid
refinement; a dense eigensolver cross-check; the analytic Hartree field and its
Coulomb energy for exponential densities; XC functional differentiation;
self-consistency; energy accounting; alternative starts/mixing; explicit
nonconvergence; independently computed HF/LDA_X energies and radial densities.
No finite test suite proves a generally correct electronic-structure solver.
In particular, small SCF residuals do not remove discretization or physical
approximation errors. HF and LDA_X energies are not exact correlated He energies.

## Sources and terms

- Hohenberg & Kohn (1964), https://doi.org/10.1103/PhysRev.136.B864
- Kohn & Sham (1965), https://doi.org/10.1103/PhysRev.140.A1133
- Dirac (1930), https://doi.org/10.1017/S0305004100016108
- PySCF DFT conventions: https://pyscf.org/user/dft.html
- PySCF SCF documentation: https://pyscf.org/user/scf.html
- SciPy tridiagonal eigensolver: https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.linalg.eigh_tridiagonal.html

Original Python code is MIT under LICENSE. Dependencies retain their own licenses
and are not bundled. Text, figures and numerical data use the site's separate
terms at https://hrkoyama.github.io/rights/ and https://hrkoyama.github.io/using/.
No third-party paper or private repository history is included.
