"""Educational isolated hydrogenic and closed-shell helium radial calculations.

Atomic units; reduced radial orbital u=r*R, integral |u|^2 dr=1.
Second-order central differences at interior points of [0,r_max], u(0)=u(r_max)=0.
Helium is restricted to two opposite-spin electrons in one spherical 1s orbital.
No correlation, relativistic effects, finite nuclear mass or general molecular HF.
"""
from dataclasses import dataclass
import math
import numpy as np
from scipy.linalg import eigh_tridiagonal
from scipy.special import eval_genlaguerre, gammaln

@dataclass(frozen=True)
class Grid:
    r: np.ndarray
    dr: float
    r_max: float


def radial_grid(r_max=16., dr=.01):
    if not np.isfinite([r_max, dr]).all() or dr <= 0 or r_max <= 0:
        raise ValueError('r_max and dr must be finite and positive')
    intervals=round(r_max/dr)
    if intervals < 16 or not math.isclose(intervals*dr,r_max,rel_tol=1e-12,abs_tol=1e-12):
        raise ValueError('r_max/dr must be an integer of at least 16')
    return Grid(np.arange(1,intervals,dtype=float)*dr,float(dr),float(r_max))


def kinetic(u, dr):
    result=u/dr**2
    result=result.copy()
    result[1:]-=.5*u[:-1]/dr**2
    result[:-1]-=.5*u[1:]/dr**2
    return result


def eigenstate(grid, potential, l=0, radial_index=0):
    if isinstance(l,bool) or int(l)!=l or l<0 or int(radial_index)!=radial_index or radial_index<0:
        raise ValueError('angular momentum and radial index must be nonnegative integers')
    l=int(l);radial_index=int(radial_index)
    v=np.asarray(potential,dtype=float)
    if v.shape!=grid.r.shape or not np.isfinite(v).all():raise ValueError('invalid radial potential')
    diagonal=1/grid.dr**2+v+l*(l+1)/(2*grid.r**2)
    off=np.full(len(v)-1,-.5/grid.dr**2)
    energy,vec=eigh_tridiagonal(diagonal,off,select='i',select_range=(radial_index,radial_index),check_finite=True)
    u=vec[:,0]/math.sqrt(grid.dr)
    if u[np.argmax(abs(u))]<0:u=-u
    residual=kinetic(u,grid.dr)+(v+l*(l+1)/(2*grid.r**2))*u-energy[0]*u
    return float(energy[0]),u,float(np.linalg.norm(residual)*math.sqrt(grid.dr))


def hydrogenic(Z=1., n=1, l=0, r_max=40., dr=.01):
    if isinstance(n,bool) or isinstance(l,bool) or not np.isfinite(Z) or Z<=0 or int(n)!=n or int(l)!=l or n<1 or l<0 or l>=n:
        raise ValueError('Z>0, n>=1 and 0<=l<n are required')
    grid=radial_grid(r_max,dr)
    energy,u,residual=eigenstate(grid,-Z/grid.r,l,n-l-1)
    rho=2*Z*grid.r/n
    scale=(2*Z/n)**1.5*math.exp(.5*(gammaln(n-l)-math.log(2*n)-gammaln(n+l+1)))
    exact_u=grid.r*scale*np.exp(-rho/2)*rho**l*eval_genlaguerre(n-l-1,2*l+1,rho)
    if np.dot(u,exact_u)<0:u=-u
    return {'grid':grid,'u':u,'exact_u':exact_u,'energy':energy,'exact_energy':-Z**2/(2*n**2),
            'energy_error':abs(energy+Z**2/(2*n**2)),'norm':float(np.dot(u,u)*dr),
            'wavefunction_l2':float(np.linalg.norm(u-exact_u)*math.sqrt(dr)),
            'eigen_residual':residual,'Z':float(Z),'n':int(n),'l':int(l)}


def hartree_potential(grid, radial_number_density):
    """p(r)=4*pi*r^2*n(r), positive number density, integral p dr = N.

    Evaluate int p(s)/max(r,s) ds by cumulative trapezoidal sums. Endpoints
    p(0)=p(r_max)=0; the diagonal sample is counted once, not twice.
    """
    p=np.asarray(radial_number_density,dtype=float)
    if p.shape!=grid.r.shape or not np.isfinite(p).all() or np.any(p<0):raise ValueError('invalid density')
    enclosed=np.cumsum(p)*grid.dr
    outer=np.cumsum((p/grid.r)[::-1])[::-1]*grid.dr
    return enclosed/grid.r+outer-grid.dr*p/grid.r


def lda_exchange(grid, p):
    n=p/(4*np.pi*grid.r**2)
    vx=-np.cbrt(3*n/np.pi)
    ex=float(.75*np.dot(p,vx)*grid.dr)
    return vx,ex


def helium(model='lda_x', r_max=16., dr=.01, mixing=.35, max_iterations=300,
           density_tolerance=1e-9, energy_tolerance=1e-10, orbital_tolerance=1e-7,
           initial_exponent=1.6875):
    if model not in ['hf','lda_x']:raise ValueError('model must be hf or lda_x')
    values=[mixing,density_tolerance,energy_tolerance,orbital_tolerance,initial_exponent]
    if not np.isfinite(values).all() or not 0<mixing<=1 or min(values[1:])<=0:raise ValueError('invalid SCF parameters')
    if isinstance(max_iterations,bool) or int(max_iterations)!=max_iterations or max_iterations<1:raise ValueError('invalid iteration limit')
    max_iterations=int(max_iterations)
    grid=radial_grid(r_max,dr);r=grid.r
    u=2*initial_exponent**1.5*r*np.exp(-initial_exponent*r);u/=math.sqrt(np.dot(u,u)*dr)
    p=2*u*u;history=[];previous=None;converged=False
    for step in range(1,max_iterations+1):
        vh_in=hartree_potential(grid,p)
        v_extra=.5*vh_in if model=='hf' else vh_in+lda_exchange(grid,p)[0]
        _,u,_=eigenstate(grid,-2/r+v_extra)
        out=2*u*u;vh=hartree_potential(grid,out)
        kinetic_energy=float(2*np.dot(u,kinetic(u,dr))*dr)
        nuclear_energy=float(np.dot(out,-2/r)*dr)
        eh=float(.5*np.dot(out,vh)*dr)
        if model=='hf':vx=-.5*vh;ex=-.5*eh
        else:vx,ex=lda_exchange(grid,out)
        energy=kinetic_energy+nuclear_energy+eh+ex
        action=kinetic(u,dr)+(-2/r+vh+vx)*u
        orbital_energy=float(np.dot(u,action)*dr)
        orbital_residual=float(np.linalg.norm(action-orbital_energy*u)*math.sqrt(dr))
        density_residual=float(np.sum(abs(out-p))*dr)
        change=None if previous is None else abs(energy-previous)
        history.append({'iteration':step,'energy':energy,'energy_change':change,'density_l1_residual':density_residual,
                        'orbital_residual':orbital_residual,'electron_count':float(np.sum(out)*dr)})
        if change is not None and density_residual<density_tolerance and change<energy_tolerance and orbital_residual<orbital_tolerance:
            converged=True;break
        p=(1-mixing)*p+mixing*out;previous=energy
    identity=2*orbital_energy-.5*eh if model=='hf' else 2*orbital_energy-eh-ex/3
    return {'grid':grid,'u':u,'radial_density':out,'hartree':vh,'exchange_potential':vx,'model':model,
            'energy':energy,'orbital_energy':orbital_energy,'kinetic_energy':kinetic_energy,'nuclear_energy':nuclear_energy,
            'hartree_energy':eh,'exchange_energy':ex,'correlation_energy':0.,'electron_count':float(np.sum(out)*dr),
            'orbital_residual':orbital_residual,'density_residual':density_residual,'energy_identity_error':abs(energy-identity),
            'history':history,'converged':converged,'reason':'density_energy_and_orbital_residual' if converged else 'max_iterations',
            'mixing':mixing,'initial_exponent':initial_exponent}
