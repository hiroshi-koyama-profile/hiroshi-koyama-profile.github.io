"""Four input-driven wave recipes using unchanged released numart solvers.

Exact transport/Riemann references and high-resolution numerical references
are deliberately different. Nothing in this module writes a file.
"""
import numpy as np
from numart.advection import difference_step
from numart.benchmarks import Problem
from numart.equations import Euler
from numart.solvers import solve
from numart.reconstruction import solve_euler
from numart.riemann import exact_euler
from numart.mhd_tests import solve_1d
from numart.hlld import conserved as mhd_conserved, primitive as mhd_primitive, physical_flux


def _keys(parameters, required):
    if not isinstance(parameters, dict) or set(parameters) != set(required.split()):
        raise ValueError('Parameters must specify exactly: '+required)


def _number(value, name, lower=None, upper=None, strict=False):
    if isinstance(value, bool) or not isinstance(value, (int, float, np.integer, np.floating)) or not np.isfinite(value):
        raise ValueError(name+' must be a finite real number')
    value = float(value)
    if ((lower is not None and (value <= lower if strict else value < lower))
            or (upper is not None and value > upper)):
        raise ValueError(name+' is outside the recipe range')
    return value


def _integer(value, name, lower, upper):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or not lower <= value <= upper:
        raise ValueError(name+' must be an integer in the recipe range')
    return int(value)


def _grids(p, reference=False):
    coarse = _integer(p['coarse_n'], 'coarse_n', 16, 512)
    fine = _integer(p['fine_n'], 'fine_n', 32, 1024)
    if fine != 2*coarse:
        raise ValueError('fine_n must be twice coarse_n')
    if not reference:
        return coarse, fine
    ref = _integer(p['reference_n'], 'reference_n', 64, 2048)
    if ref < 2*fine or ref % fine:
        raise ValueError('reference_n must be an integer multiple of fine_n, at least twice as large')
    return coarse, fine, ref


def _fixed(p, definitions):
    # These named historical cases are wrappers, not new general solvers.
    for key, value in definitions.items():
        try:
            equal = np.array_equal(np.asarray(p[key]), np.asarray(value))
            if np.asarray(value).dtype.kind in 'fiu':
                equal = equal and not any(isinstance(v, (bool, np.bool_)) for v in np.asarray(p[key], dtype=object).ravel())
        except (TypeError, ValueError):
            equal = False
        if not equal:
            raise ValueError(key+' differs from this named benchmark; use the recorded definition')


def _balance(initial, final, domain, time, left_flux, right_flux):
    dx = (domain[1]-domain[0])/len(final)
    start = dx*np.sum(initial, axis=0)
    finish = dx*np.sum(final, axis=0)
    transported = time*(left_flux-right_flux)
    residual = finish-start-transported
    scale = np.maximum(1., np.maximum(abs(start), np.maximum(abs(finish), abs(transported))))
    return residual, float(np.max(abs(residual)/scale))


def _ratio(coarse_error, fine_error):
    if coarse_error <= np.finfo(float).tiny:
        raise ValueError('Refinement diagnostic is undefined for zero coarse error')
    return float(fine_error/coarse_error)


def _advection(p):
    _keys(p, 'coarse_n fine_n domain mean amplitude mode speed final_time cfl method')
    coarse, fine = _grids(p)
    domain = np.asarray(p['domain'], dtype=float)
    if domain.shape != (2,) or not np.isfinite(domain).all() or domain[1] <= domain[0]:
        raise ValueError('domain must contain two increasing finite endpoints')
    mean = _number(p['mean'], 'mean')
    amplitude = _number(p['amplitude'], 'amplitude', 0., strict=True)
    mode = _integer(p['mode'], 'mode', 1, coarse//8)
    speed = _number(p['speed'], 'speed')
    time = _number(p['final_time'], 'final_time', 0., 10., strict=True)
    cfl = _number(p['cfl'], 'cfl', 0., 1., strict=True)
    if speed == 0 or p['method'] != 'upwind':
        raise ValueError('This refinement recipe requires nonzero speed and method upwind')
    length = domain[1]-domain[0]
    def initial(x):
        return mean+amplitude*np.sin(2*np.pi*mode*(x-domain[0])/length)
    results = []
    for n in (coarse, fine):
        dx = length/n
        x = domain[0]+(np.arange(n)+.5)*dx
        start = initial(x)
        steps = int(np.ceil(time*abs(speed)/(cfl*dx)))
        if steps > 100000:
            raise ValueError('Requested advection step count exceeds recipe limit')
        dt = time/steps
        q = start.copy()
        for _ in range(steps):
            q = difference_step(q, speed*dt/dx, 'upwind')
        exact = initial(x-speed*time)
        error = float(np.mean(abs(q-exact)))
        results.append((x, start, q, exact, error, steps, speed*dt/dx))
    x, start, q, exact, fine_error, steps, courant = results[1]
    max_excess = max(0., float(q.max()-start.max()), float(start.min()-q.min()))
    return {
        'metrics': {'density_l1_error_coarse': results[0][4], 'density_l1_error_fine': fine_error,
                    'fine_to_coarse_error_ratio': _ratio(results[0][4], fine_error),
                    'mean_conservation_error': float(abs(q.mean()-start.mean())),
                    'maximum_principle_excess': max_excess, 'courant_abs': float(abs(courant)),
                    'steps_fine': steps, 'final_time': time},
        'table': {'x': x.tolist(), 'initial': start.tolist(), 'computed': q.tolist(),
                  'exact_pde': exact.tolist(), 'absolute_error': abs(q-exact).tolist()},
        'details': {'reference_kind': 'analytic translated periodic sine, not the discrete amplification factor',
                    'row_layout': 'one row per fine-grid cell-center sample at final_time',
                    'scheme': 'first-order upwind plus forward Euler; fixed step chosen at or below input CFL',
                    'refinement': 'L1 sample error versus the continuous PDE solution; no fitted formal-order claim'}}


def _euler_problem(case, p):
    eq = Euler(p['gamma'])
    left = np.asarray(p['left'], dtype=float)
    domain = tuple(p['domain'])
    if case == 'sod':
        right = np.asarray(p['right'], dtype=float)
        def initial(x):
            return eq.conserved(np.where((x < p['discontinuity'])[..., None], left, right))
        def reference(x, time):
            return eq.conserved(exact_euler((x-p['discontinuity'])/time, left, right, p['gamma']))
    else:
        def initial(x):
            rho = p['ambient_density']+p['density_amplitude']*np.sin(p['angular_wavenumber']*x)
            w = np.stack((rho, np.full_like(x, p['ambient_velocity']), np.full_like(x, p['ambient_pressure'])), axis=-1)
            return eq.conserved(np.where((x < p['discontinuity'])[..., None], left, w))
        reference = None
    return Problem(case, eq, domain, p['final_time'], p['boundary'], initial, reference)


def _euler(case, p):
    common = 'coarse_n fine_n domain discontinuity gamma left final_time cfl boundary method'
    if case == 'sod':
        _keys(p, common+' right riemann')
        ns = _grids(p)
        _fixed(p, {'domain':[0.,1.], 'discontinuity':.5, 'gamma':1.4,
                   'left':[1.,0.,1.], 'right':[.125,0.,.1],
                   'boundary':'outflow', 'method':'godunov', 'riemann':'hllc'})
        _number(p['final_time'], 'final_time', 0., .2, strict=True)
    else:
        _keys(p, common+' reference_n ambient_density density_amplitude angular_wavenumber ambient_velocity ambient_pressure basis epsilon')
        ns = _grids(p, True)
        _fixed(p, {'domain':[-5.,5.], 'discontinuity':-4., 'gamma':1.4,
                   'left':[3.857143,2.629369,10.33333], 'ambient_density':1., 'density_amplitude':.2,
                   'angular_wavenumber':5., 'ambient_velocity':0., 'ambient_pressure':1.,
                   'boundary':'fixed', 'method':'weno-z', 'basis':'characteristic'})
        _number(p['final_time'], 'final_time', 0., 1.8, strict=True)
        _number(p['epsilon'], 'epsilon', 0., strict=True)
        if any(abs((p['discontinuity']-p['domain'][0])*n/10-round((p['discontinuity']-p['domain'][0])*n/10)) > 1e-12 for n in ns):
            raise ValueError('Choose Shu–Osher grids with the initial discontinuity on a cell face (multiples of 10)')
    _number(p['cfl'], 'cfl', 0., .5, strict=True)
    problem = _euler_problem(case, p)
    results = []
    for n in ns:
        if case == 'sod':
            result = solve(problem, n=n, method=p['method'], riemann=p['riemann'], cfl=p['cfl'])
        else:
            result = solve_euler(problem, n=n, method=p['method'], basis=p['basis'], cfl=p['cfl'], epsilon=p['epsilon'])
        results.append(result)
    fine = results[1]
    if case == 'sod':
        reference = [problem.reference(result.x, result.time) for result in results[:2]]
    else:
        ref = results[2]
        reference = [np.column_stack([np.interp(result.x, ref.x, ref.q[:,j]) for j in range(3)]) for result in results[:2]]
    errors = [float(np.mean(abs(result.q[:,0]-qref[:,0]))) for result,qref in zip(results, reference)]
    w = problem.equation.primitive(fine.q)
    wr = problem.equation.primitive(reference[1])
    initial = problem.initial(fine.x)
    endpoints = problem.initial(np.asarray(p['domain'], dtype=float))
    flux = problem.equation.flux(endpoints)
    residual, defect = _balance(initial, fine.q, p['domain'], fine.time, flux[0], flux[1])
    metrics = {'density_l1_error_coarse': errors[0], 'density_l1_error_fine': errors[1],
               'fine_to_coarse_error_ratio': _ratio(*errors), 'minimum_density': float(w[:,0].min()),
               'minimum_pressure': float(w[:,2].min()), 'physical_boundary_balance_relative_defect': defect,
               'mass_balance_absolute_defect': float(abs(residual[0])),
               'momentum_balance_absolute_defect': float(abs(residual[1])),
               'energy_balance_absolute_defect': float(abs(residual[2])),
               'steps_fine': fine.steps, 'final_time_error': float(abs(fine.time-p['final_time']))}
    if case == 'shu-osher':
        metrics.update(reference_n=ns[2], rejected_steps=sum(result.rejected_steps for result in results))
    return {'metrics': metrics,
            'table': {'x': fine.x.tolist(), 'density': w[:,0].tolist(), 'velocity': w[:,1].tolist(),
                      'pressure': w[:,2].tolist(), 'reference_density': wr[:,0].tolist(),
                      'reference_velocity': wr[:,1].tolist(), 'reference_pressure': wr[:,2].tolist(),
                      'density_absolute_error': abs(w[:,0]-wr[:,0]).tolist()},
            'details': {'reference_kind': ('analytic self-similar Euler Riemann solution; pressure evaluated by bracketed numerical root in numart.riemann, not an independent codebase' if case == 'sod' else 'same-method higher-resolution numerical reference, linearly interpolated in conserved variables to the two sample grids; not exact and not an independent solver'),
                        'row_layout': 'one fine-grid location per row; reference at the identical final time and location',
                        'representation': 'sampled cell values with piecewise-constant FV update' if case == 'sod' else 'pointwise finite-difference values, not finite-volume cell averages',
                        'conservation': 'integral(final)-integral(initial)-T*(physical left flux-physical right flux); FD fixed ghosts can leave boundary discretization error' if case == 'shu-osher' else 'integral(final)-integral(initial)-T*(physical left flux-physical right flux); uniform far fields remain outside the wave fan',
                        'refinement': 'coarse and fine L1 sample errors against the stated reference; ratio is empirical, not a proof of formal order'}}


def _brio(p):
    _keys(p, 'coarse_n fine_n reference_n domain discontinuity gamma left right final_time cfl solver limiter boundary mu0')
    ns = _grids(p, True)
    _fixed(p, {'domain':[0.,1.], 'discontinuity':.5, 'gamma':2., 'mu0':1.,
               'left':[1.,0.,0.,0.,1.,.75,1.,0.], 'right':[.125,0.,0.,0.,.1,.75,-1.,0.],
               'solver':'hlld', 'limiter':'mc', 'boundary':'edge-extrapolation'})
    _number(p['final_time'], 'final_time', 0., .1, strict=True)
    _number(p['cfl'], 'cfl', 0., .4, strict=True)
    if any(n % 2 for n in ns):
        raise ValueError('Brio–Wu grids must align the initial jump with a cell face')
    results = [solve_1d('brio-wu', n=n, final_time=p['final_time'], solver=p['solver'], limiter=p['limiter'], cfl=p['cfl']) for n in ns]
    ref = results[2]
    references = [ref.q.reshape(n, ns[2]//n, 8).mean(axis=1) for n in ns[:2]]
    errors = [float(np.mean(abs(result.q[:,0]-qref[:,0]))) for result,qref in zip(results, references)]
    fine = results[1]
    w, wr = mhd_primitive(fine.q, p['gamma']), mhd_primitive(references[1], p['gamma'])
    x = (np.arange(ns[1])+.5)/ns[1]
    initial = mhd_conserved(np.where((x < .5)[:,None], p['left'], p['right']), p['gamma'])
    flux = physical_flux(np.asarray([p['left'],p['right']]), p['gamma'])
    residual, defect = _balance(initial, fine.q, p['domain'], fine.time, flux[0], flux[1])
    table = {'x': x.tolist()}
    for j, label in enumerate(['density','velocity_x','velocity_y','velocity_z','pressure','magnetic_x','magnetic_y','magnetic_z']):
        table[label] = w[:,j].tolist()
        table['reference_'+label] = wr[:,j].tolist()
    return {'metrics': {'density_l1_error_coarse': errors[0], 'density_l1_error_fine': errors[1],
                        'fine_to_coarse_error_ratio': _ratio(*errors),
                        'minimum_density': float(w[:,0].min()), 'minimum_pressure': float(w[:,4].min()),
                        'longitudinal_field_max_error': float(abs(w[:,5]-p['left'][5]).max()),
                        'physical_boundary_balance_relative_defect': defect,
                        'mass_balance_absolute_defect': float(abs(residual[0])),
                        'energy_balance_absolute_defect': float(abs(residual[4])),
                        'hlle_fallback_faces': sum(result.stats['hlle_fallback_faces'] for result in results),
                        'retried_steps': sum(result.stats['retried_steps'] for result in results),
                        'steps_fine': fine.steps, 'reference_n': ns[2],
                        'final_time_error': float(abs(fine.time-p['final_time']))},
            'table': table,
            'details': {'reference_kind': 'same HLLD/MC/SSPRK2 solver on a higher-resolution grid; conservative block restriction to each tested grid; not exact or an independent solver',
                        'row_layout': 'one fine cell per row; reference conserved cell averages are block-averaged before conversion to primitive variables',
                        'conservation': 'all eight integral balances subtract T*(physical left flux-physical right flux); nonzero momentum changes are expected',
                        'scheme': 'unchanged numart.mhd_tests.solve_1d, HLLD with counted HLLE fallback, MC primitive reconstruction and SSPRK2',
                        'refinement': 'empirical L1 density disagreement with the restricted numerical reference, not a formal convergence-rate or MHD uniqueness claim'}}


def run(problem_id, parameters):
    """Return finite metrics and a column-oriented numeric table; no file IO."""
    if problem_id == 'advection-sine':
        result = _advection(parameters)
    elif problem_id in ('sod','shu-osher'):
        result = _euler(problem_id, parameters)
    elif problem_id == 'brio-wu':
        result = _brio(parameters)
    else:
        raise ValueError('Unknown waves recipe: '+str(problem_id))
    if not all(isinstance(v, (bool,int,float)) and np.isfinite(v) for v in result['metrics'].values()):
        raise RuntimeError('Nonfinite or non-scalar recipe metric')
    lengths = {len(column) for column in result['table'].values()}
    if len(lengths) != 1 or not all(np.isfinite(column).all() for column in result['table'].values()):
        raise RuntimeError('Invalid numeric recipe table')
    return result
