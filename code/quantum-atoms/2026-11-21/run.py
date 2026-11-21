"""Reproduce fixed inputs, convergence studies, failures and original figures."""
from pathlib import Path
import argparse,csv,json,math,platform
import numpy as np
import scipy
from atomic_radial import hydrogenic,helium

ROOT=Path(__file__).resolve().parent

def save_csv(path,columns):
    with path.open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(columns)
        writer.writerows(zip(*columns.values()))

def he_summary(result,**extra):
    keys=['model','energy','orbital_energy','kinetic_energy','nuclear_energy','hartree_energy','exchange_energy','correlation_energy','electron_count','orbital_residual','density_residual','energy_identity_error','converged','reason']
    return {**{k:result[k] for k in keys},'dr':result['grid'].dr,'r_max':result['grid'].r_max,'iterations':len(result['history']),**extra}

def calculate(inputs,reference,output):
    output.mkdir(parents=True,exist_ok=True);(output/'profiles').mkdir(exist_ok=True)
    h=inputs['hydrogenic'];he=inputs['helium'];hs=[];hprofiles={};hdomains=[]
    for Z in h['charges']:
        for n,l in h['states']:
            for dr in h['steps']:
                result=hydrogenic(Z,n,l,h['r_max'],dr)
                hs.append({k:result[k] for k in ['Z','n','l','energy','exact_energy','energy_error','norm','wavefunction_l2','eigen_residual']}|{'dr':dr,'r_max':h['r_max']})
                if dr==min(h['steps']):
                    key=f'z{Z}-n{n}-l{l}';hprofiles[key]=result
                    save_csv(output/'profiles'/('hydrogenic-'+key+'.csv'),{'r_bohr':result['grid'].r,'u':result['u'],'exact_u':result['exact_u'],'radial_probability':result['u']**2})
    for radius in h['domain_radii']:
        result=hydrogenic(r_max=radius,dr=h['domain_step'])
        hdomains.append({'r_max':radius,'dr':h['domain_step'],'energy':result['energy'],'energy_error':result['energy_error']})
    args={k:he[k] for k in ['mixing','max_iterations','density_tolerance','energy_tolerance','orbital_tolerance']}
    rows=[];profiles={};domains=[];restarts=[];comparison=[];failures=[]
    for model in he['models']:
        by_step=[]
        for dr in he['steps']:
            result=helium(model,he['r_max'],dr,**args)
            if not result['converged']:raise RuntimeError('Unexpected SCF failure')
            row=he_summary(result);rows.append(row);by_step.append(row)
            if dr==min(he['steps']):profiles[model]=result
        coarse,fine=by_step[-2:]
        assert math.isclose(coarse['dr'],2*fine['dr'])
        extrapolated=(4*fine['energy']-coarse['energy'])/3
        ref=reference['finest'][model]
        r=profiles[model]['grid'].r
        assert np.allclose(r,ref['r'],rtol=0,atol=1e-12)
        density_l1=float(np.sum(abs(profiles[model]['radial_density']-ref['radial_density']))*min(he['steps']))
        comparison.append({'model':model,'finest_energy':fine['energy'],'reference_energy':ref['energy'],
                           'finest_reference_difference':fine['energy']-ref['energy'],'richardson_h2_energy':extrapolated,
                           'extrapolated_reference_difference':extrapolated-ref['energy'],'radial_density_l1_difference':density_l1,
                           'note':'h^2 extrapolation is a consistency estimate, not a certified error bound. The Gaussian reference has its own basis/quadrature error.'})
        result=profiles[model]
        save_csv(output/'profiles'/('helium-'+model+'.csv'),{'r_bohr':r,'u':result['u'],'radial_number_density':result['radial_density'],
                 'hartree_potential':result['hartree'],'exchange_potential':result['exchange_potential'],'independent_radial_density':ref['radial_density']})
        for radius in he['domain_radii']:
            result=helium(model,radius,he['domain_step'],**args)
            if not result['converged']:raise RuntimeError('Domain study did not converge')
            domains.append(he_summary(result))
        result=helium(model,he['r_max'],he['domain_step'],**{**args,'mixing':he['alternative_mixing'],'initial_exponent':he['alternative_initial_exponent']})
        if not result['converged']:raise RuntimeError('Restart study did not converge')
        restarts.append({**he_summary(result),'history':result['history'],'mixing':result['mixing'],'initial_exponent':result['initial_exponent']})
        result=helium(model,he['r_max'],he['domain_step'],**{**args,'max_iterations':1})
        failures.append({**he_summary(result),'history':result['history']})
    checks={
        'hydrogenic_exact_energy_errors_reduce':all(g[-1]['energy_error']<g[0]['energy_error']/12 for Z in h['charges'] for n,l in h['states'] for g in [[x for x in hs if (x['Z'],x['n'],x['l'])==(Z,n,l)]]),
        'hydrogenic_normalization':all(abs(x['norm']-1)<1e-12 for x in hs),
        'hydrogenic_eigen_residual':all(x['eigen_residual']<1e-7 for x in hs),
        'helium_scf_converged':all(x['converged'] for x in rows+domains+restarts),
        'helium_electron_count':all(abs(x['electron_count']-2)<1e-12 for x in rows+domains+restarts),
        'helium_energy_identity':all(x['energy_identity_error']<1e-10 for x in rows),
        'independent_extrapolated_energies':all(abs(x['extrapolated_reference_difference'])<1e-8 for x in comparison),
        'independent_density_profiles':all(x['radial_density_l1_difference']<5e-5 for x in comparison),
        'expected_failures_reported':all(not x['converged'] and x['reason']=='max_iterations' for x in failures),
        'independent_basis_refinement':all(abs([x['energy'] for x in reference['cases'] if x['model']==m and x['quadrature_grid']==reference['finest'][m]['quadrature_grid']][-1]-[x['energy'] for x in reference['cases'] if x['model']==m and x['quadrature_grid']==reference['finest'][m]['quadrature_grid']][-2])<1e-8 for m in he['models'])}
    report={'schema_version':1,'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'inputs':inputs,
            'scope':'Hydrogenic radial bound states and isolated closed-shell 1s^2 helium. HF exact exchange is special to this two-electron orbital. LDA_X has zero correlation. Not molecular/periodic or a general HF/DFT solver.',
            'hydrogenic':{'refinement':hs,'domain_refinement':hdomains},'helium':{'refinement':rows,'domain_refinement':domains,'independent_comparison':comparison,'alternative_starts':restarts,
             'scf_histories':{m:r['history'] for m,r in profiles.items()},'expected_nonconvergence':failures},'checks':checks}
    (output/'results.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    if not all(checks.values()):raise RuntimeError('Numerical validation failed: '+str(checks))
    return report,hprofiles,profiles

def figures(output,report,hprofiles,profiles):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white','figure.facecolor':'white'})
    h=hprofiles['z1-n1-l0'];fig,ax=plt.subplots(figsize=(6.4,3.8),layout='constrained')
    mask=h['grid'].r<10
    ax.plot(h['grid'].r[mask],h['u'][mask]**2,label='Finite difference, h=0.01')
    ax.plot(h['grid'].r[mask],h['exact_u'][mask]**2,'--',label='Hydrogen 1s reference')
    ax.set(xlabel='r / bohr',ylabel='radial probability / bohr');ax.legend(fontsize=8);fig.savefig(output/'hydrogenic.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(6.4,3.8),layout='constrained')
    for m,r in profiles.items():
        mask=r['grid'].r<7;ax.plot(r['grid'].r[mask],r['radial_density'][mask],label='He HF' if m=='hf' else 'He LDA exchange only')
    ax.set(xlabel='r / bohr',ylabel='radial electron density / bohr');ax.legend(fontsize=8);fig.savefig(output/'helium.png',dpi=150);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for n,l in [(1,0),(2,0),(2,1),(3,2)]:
        rows=[x for x in report['hydrogenic']['refinement'] if (x['Z'],x['n'],x['l'])==(1,n,l)]
        axes[0].loglog([x['dr'] for x in rows],[x['energy_error'] for x in rows],'o-',label=f'H n={n}, l={l}')
    for m in ['hf','lda_x']:
        ref=next(x['reference_energy'] for x in report['helium']['independent_comparison'] if x['model']==m)
        rows=[x for x in report['helium']['refinement'] if x['model']==m]
        axes[1].loglog([x['dr'] for x in rows],[abs(x['energy']-ref) for x in rows],'o-',label='He '+m)
    for ax in axes:ax.set(xlabel='radial step / bohr',ylabel='energy difference / hartree');ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.savefig(output/'convergence.png',dpi=150);plt.close(fig)
    fig,ax=plt.subplots(figsize=(6.4,3.8),layout='constrained')
    for m,r in profiles.items():ax.semilogy([x['iteration'] for x in r['history']],[x['density_l1_residual'] for x in r['history']],label=m)
    ax.set(xlabel='SCF iteration',ylabel='input-output density L1 residual');ax.legend(fontsize=8);ax.grid(alpha=.2);fig.savefig(output/'scf.png',dpi=150);plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,default=ROOT/'inputs.json');p.add_argument('--reference',type=Path,default=ROOT/'reference-pyscf.json');p.add_argument('--output',type=Path,default=Path('output'));p.add_argument('--figures',action='store_true');a=p.parse_args()
    report,h,he=calculate(json.loads(a.input.read_text()),json.loads(a.reference.read_text()),a.output)
    if a.figures:figures(a.output,report,h,he)
    print(json.dumps({'checks':report['checks'],'helium':report['helium']['independent_comparison']},indent=2))
