"""Optional independent Gaussian-basis HF and Libxc LDA-exchange reference.

Requires requirements-reference.txt. No atlas SCF, radial Hartree or XC functions
are imported. PySCF supplies Gaussian integrals/SCF and Libxc supplies LDA_X.
"""
from pathlib import Path
import argparse,json,platform
import numpy as np
import scipy
from pyscf import gto,scf,dft,lib
import pyscf

def calculate(config):
    lib.num_threads(1)
    cases=[];final={}
    for size in config['basis_sizes']:
        exponents=np.geomspace(*config['exponent_range'],size)
        mol=gto.M(atom='He 0 0 0',unit='Bohr',basis={'He':[[0,[float(a),1.]] for a in exponents]},spin=config['spin'],charge=config['charge'],verbose=0)
        for model in ['hf','lda_x']:
            grids=config['radial_angular_grids'] if model=='lda_x' else [None]
            for grid in grids:
                mf=scf.RHF(mol) if model=='hf' else dft.RKS(mol)
                if grid is not None:mf.xc=config['pyscf_xc'];mf.grids.atom_grid=tuple(grid);mf.grids.prune=None
                mf.conv_tol=config['scf_energy_tolerance'];mf.conv_tol_grad=1e-9;mf.max_cycle=200
                energy=float(mf.kernel())
                if not mf.converged:raise RuntimeError('Independent reference did not converge')
                dm=mf.make_rdm1();s=mol.intor('int1e_ovlp')
                profile=config['density_profile'];r=np.arange(1,round(profile['r_max']/profile['dr']))*profile['dr'];coords=np.column_stack([r,np.zeros_like(r),np.zeros_like(r)])
                rho=dft.numint.eval_rho(mol,dft.numint.eval_ao(mol,coords),dm,xctype='LDA')
                result={'model':model,'basis_size':size,'exponents':exponents.tolist(),'quadrature_grid':grid,'energy':energy,
                        'converged':bool(mf.converged),'electron_count_overlap':float(np.einsum('ij,ji',dm,s)),
                        'overlap_minimum_eigenvalue':float(np.linalg.eigvalsh(s).min())}
                cases.append(result)
                final[model]={**result,'r':r.tolist(),'radial_density':(4*np.pi*r*r*rho).tolist()}
                print(size,model,grid,energy,flush=True)
    return {'scope':'Independent uncontracted even-tempered s-Gaussian PySCF calculation of closed-shell helium; HF and spin-unpolarized exchange-only LDA. Finite-basis/quadrature references, not exact correlated helium.',
            'environment':{'python':platform.python_version(),'pyscf':pyscf.__version__,'numpy':np.__version__,'scipy':scipy.__version__,'libxc':dft.libxc.libxc_version()},
            'inputs':config,'cases':cases,'finest':final}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',default='inputs.json');p.add_argument('--output',default='reference-pyscf.json');a=p.parse_args()
    config=json.loads(Path(a.input).read_text())['independent_reference']
    Path(a.output).write_text(json.dumps(calculate(config),indent=2,allow_nan=False)+'\n')
