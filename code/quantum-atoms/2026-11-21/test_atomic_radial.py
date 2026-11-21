"""Numerical checks using analytic identities and an independently run reference."""
from pathlib import Path
import json
import numpy as np
import pytest
from atomic_radial import radial_grid,kinetic,eigenstate,hydrogenic,hartree_potential,lda_exchange,helium

@pytest.mark.parametrize('Z,n,l',[(1,1,0),(2,1,0),(1,2,0),(1,2,1),(1,3,2)])
def test_hydrogenic_refinement_and_normalization(Z,n,l):
    coarse=hydrogenic(Z,n,l,60,.04);fine=hydrogenic(Z,n,l,60,.02)
    assert 3.8<coarse['energy_error']/fine['energy_error']<4.2
    assert abs(fine['norm']-1)<1e-12
    assert fine['eigen_residual']<1e-7
    assert fine['wavefunction_l2']<3e-4

def test_coulomb_charge_scaling_and_orthogonality():
    h=hydrogenic(1,1,0,32,.02);ion=hydrogenic(2,1,0,16,.01)
    assert abs(ion['energy']-4*h['energy'])<1e-9
    excited=hydrogenic(1,2,0,32,.02)
    assert abs(np.dot(h['u'],excited['u'])*.02)<1e-10

def test_finite_domain_is_separate_from_grid_error():
    energies=[hydrogenic(r_max=r,dr=.01)['energy'] for r in [4,8,16,32]]
    assert energies[0]-energies[1]>1e-3
    assert abs(energies[-1]-energies[-2])<1e-8
    assert abs(energies[-1]+.5)>1e-6  # a large box alone does not remove mesh error

def test_tridiagonal_solver_against_independent_dense_diagonalization():
    g=radial_grid(8,.1);v=-1/g.r;e,u,_=eigenstate(g,v)
    a=np.diag(1/g.dr**2+v)+np.diag(np.full(len(v)-1,-.5/g.dr**2),1)+np.diag(np.full(len(v)-1,-.5/g.dr**2),-1)
    assert abs(e-np.linalg.eigvalsh(a)[0])<1e-10

def test_hartree_analytic_exponential_density_and_single_counted_diagonal():
    g=radial_grid(16,.005);r=g.r;Z=1.5
    p=8*Z**3*r*r*np.exp(-2*Z*r)
    v=hartree_potential(g,p)
    exact=2*(1/r-np.exp(-2*Z*r)*(1/r+Z))
    assert np.max(abs(v-exact))<1e-4
    assert abs(.5*np.dot(p,v)*g.dr-5*Z/4)<1e-4
    assert abs(r[-1]*v[-1]-np.sum(p)*g.dr)<1e-12

def test_lda_exchange_is_functional_derivative_of_the_same_energy():
    g=radial_grid(12,.01);r=g.r;p=8*r*r*np.exp(-2*r)
    delta=np.where(r<4,p*np.sin(r),0);eps=1e-5
    vx,ex=lda_exchange(g,p)
    derivative=(lda_exchange(g,p+eps*delta)[1]-lda_exchange(g,p-eps*delta)[1])/(2*eps)
    assert abs(derivative-np.dot(vx,delta)*g.dr)<1e-9
    assert abs(ex-.75*np.dot(p,vx)*g.dr)<1e-12

@pytest.mark.parametrize('model',['hf','lda_x'])
def test_helium_scf_and_independent_reference(model):
    coarse=helium(model,dr=.01);fine=helium(model,dr=.005)
    ref=json.loads((Path(__file__).parent/'reference-pyscf.json').read_text())['finest'][model]
    assert coarse['converged'] and fine['converged']
    assert fine['orbital_residual']<1e-7 and fine['density_residual']<1e-9
    assert abs(fine['electron_count']-2)<1e-12
    assert fine['energy_identity_error']<1e-10
    assert abs((4*fine['energy']-coarse['energy'])/3-ref['energy'])<1e-7
    assert coarse['energy']-ref['energy']>3.9*(fine['energy']-ref['energy'])
    if model=='hf':assert abs(fine['exchange_energy']+.5*fine['hartree_energy'])<1e-12
    assert fine['correlation_energy']==0

@pytest.mark.parametrize('model',['hf','lda_x'])
def test_alternative_start_and_explicit_nonconvergence(model):
    baseline=helium(model,dr=.01)
    alternate=helium(model,dr=.01,mixing=.7,initial_exponent=1.)
    assert alternate['converged'] and abs(baseline['energy']-alternate['energy'])<1e-9
    failed=helium(model,dr=.01,max_iterations=1)
    assert not failed['converged'] and failed['reason']=='max_iterations'
    assert np.isfinite(failed['energy'])

@pytest.mark.parametrize('settings',[{'mixing':0},{'mixing':1.1},{'max_iterations':0},{'density_tolerance':-1},{'model':'vwn'}])
def test_unsupported_inputs_are_not_silently_reinterpreted(settings):
    with pytest.raises(ValueError):helium(**settings)

@pytest.mark.parametrize('rmax,dr',[(0,.1),(4,0),(4,float('nan')),(4,.3)])
def test_invalid_grids(rmax,dr):
    with pytest.raises(ValueError):radial_grid(rmax,dr)
