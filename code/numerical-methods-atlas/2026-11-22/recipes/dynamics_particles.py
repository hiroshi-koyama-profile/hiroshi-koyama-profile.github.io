"""Fixed-input ODE, periodic-fluid and particle laboratories.

Only orchestration and independent analytic diagnostics live here. Numerical
steps are provided by the unchanged numart modules in this code edition.
No files are written; the common recipe runner handles publication formats.
"""
import numpy as np

from numart.hamiltonian import trajectory, energy, canonical_step
from numart.stiff import integrate, sdirk2_step
from numart.incompressible import taylor_green
from numart.particle_gravity import pm_acceleration, periodic_poisson


def _keys(parameters, expected):
    if not isinstance(parameters, dict) or set(parameters) != set(expected):
        raise ValueError('Parameters must contain exactly: '+', '.join(expected))


def _number(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value):
        raise ValueError(name+' must be a finite number')
    if positive and value <= 0:
        raise ValueError(name+' must be positive')
    return float(value)


def _integer(value, name, lower, upper):
    if isinstance(value, bool) or not isinstance(value, int) or not lower <= value <= upper:
        raise ValueError(name+' must be an integer in the supported range')
    return value


def _levels(values, name, lower, upper):
    if not isinstance(values, list) or len(values) != 3:
        raise ValueError(name+' requires three successive doubling levels')
    levels = [_integer(v, name, lower, upper) for v in values]
    if levels[1] != 2*levels[0] or levels[2] != 2*levels[1]:
        raise ValueError(name+' requires successive doubling')
    return levels


def _vector(value, name, size):
    if not isinstance(value, list) or len(value) != size:
        raise ValueError(name+' has the wrong dimension')
    return np.array([_number(v, name) for v in value])


def _orders(errors):
    errors = np.asarray(errors)
    if not np.all(np.isfinite(errors)) or np.any(errors <= 0):
        raise RuntimeError('Cannot estimate refinement order from nonpositive errors')
    return np.log2(errors[:-1]/errors[1:])


def _table(**columns):
    converted = {k: np.asarray(v).ravel().astype(float) for k, v in columns.items()}
    if len({len(v) for v in converted.values()}) != 1 or any(not np.all(np.isfinite(v)) for v in converted.values()):
        raise RuntimeError('Output table must have aligned finite columns')
    return {k: v.tolist() for k, v in converted.items()}


def _harmonic(p):
    _keys(p, ['system', 'method', 'initial', 'final_time', 'step_counts'])
    if p['system'] != 'harmonic' or p['method'] != 'verlet':
        raise ValueError('This recipe is the unit-mass, unit-frequency harmonic Verlet case')
    initial = _vector(p['initial'], 'initial', 2)
    if float(initial@initial) == 0:
        raise ValueError('A nonzero oscillator is required for relative diagnostics')
    final = _number(p['final_time'], 'final_time', positive=True)
    counts = _levels(p['step_counts'], 'step_counts', 10, 100000)
    if final/counts[0] >= 2:
        raise ValueError('Verlet oscillator stability requires h*omega < 2')
    errors = []; refinements = []
    for count in counts:
        times, states = trajectory(final/count, count, 'verlet', 'harmonic', initial)
        q = initial[0]*np.cos(times)+initial[1]*np.sin(times)
        momentum = -initial[0]*np.sin(times)+initial[1]*np.cos(times)
        error = np.hypot(states[:, 0]-q, states[:, 1]-momentum)
        errors.append(float(error[-1]))
        refinements.append({'steps': count, 'h': final/count, 'endpoint_error': errors[-1],
                            'maximum_state_error': float(error.max())})
    energies = energy(states, 'harmonic'); initial_energy = float(energies[0])
    reverse = states[-1].copy()
    for _ in range(counts[-1]):
        reverse = canonical_step(reverse, -final/counts[-1], 'verlet', 'harmonic')
    orders = _orders(errors)
    return {'metrics': {'final_state_error': errors[-1], 'max_state_error': float(error.max()),
                        'minimum_observed_order': float(orders.min()),
                        'max_relative_energy_deviation': float(np.max(abs(energies-initial_energy))/initial_energy),
                        'reversal_error': float(np.linalg.norm(reverse-initial)),
                        'final_time_error': float(abs(times[-1]-final))},
            'table': _table(time=times, q=states[:, 0], p=states[:, 1],
                            q_exact=q, p_exact=momentum, energy=energies,
                            energy_exact=np.full(len(times), initial_energy), state_error=error),
            'details': {'reference': 'q=q0*cos(t)+p0*sin(t); p=-q0*sin(t)+p0*cos(t), H=(q^2+p^2)/2',
                        'row_layout': 'One row per time of the finest trajectory, including t=0 and final_time.',
                        'refinement': refinements, 'observed_orders': orders.tolist(),
                        'scope': 'Symplectic/time-symmetric does not imply exact conservation of the original energy or absence of phase error.'}}


def _stiff(p):
    _keys(p, ['method', 'rate', 'initial', 'final_time', 'step_counts', 'decay_rate', 'decay_step'])
    if p['method'] != 'sdirk2':
        raise ValueError('This fixed-step recipe uses the released L-stable SDIRK2')
    rate = _number(p['rate'], 'rate', positive=True)
    initial = _number(p['initial'], 'initial')
    final = _number(p['final_time'], 'final_time', positive=True)
    counts = _levels(p['step_counts'], 'step_counts', 10, 20000)
    decay_rate = _number(p['decay_rate'], 'decay_rate', positive=True)
    decay_step = _number(p['decay_step'], 'decay_step', positive=True)
    f = lambda t, y: -rate*(y-np.cos(t))-np.sin(t)
    jac = lambda t, y: -rate*np.eye(len(y))
    errors = []; refinements = []
    for count in counts:
        # Round the requested upper bound upward to avoid an accidental extra
        # step from ceil(T/dt), while the integrator still uses exactly T/count.
        times, states = integrate(f, jac, [initial], final,
                                 np.nextafter(final/count, np.inf), 'sdirk2')
        if len(times) != count+1:
            raise RuntimeError('Fixed-step count does not match the input')
        exact = np.cos(times)+(initial-1)*np.exp(-rate*times)
        error = abs(states[:, 0]-exact)
        errors.append(float(error.max()))
        refinements.append({'steps': count, 'h': final/count,
                            'rate_times_h': rate*final/count, 'maximum_error': errors[-1]})
    orders = _orders(errors)
    decay = sdirk2_step(lambda t,y: -decay_rate*y,
                       lambda t,y: -decay_rate*np.eye(1), 0., np.ones(1), decay_step)
    decay_exact = float(np.exp(-decay_rate*decay_step))
    return {'metrics': {'maximum_error': errors[-1], 'minimum_observed_order': float(orders.min()),
                        'final_error': float(error[-1]), 'final_time_error': float(abs(times[-1]-final)),
                        'maximum_state_magnitude': float(np.max(abs(states))),
                        'stiff_decay_error': float(abs(decay[0]-decay_exact))},
            'table': _table(time=times, y=states[:, 0], y_exact=exact, absolute_error=error),
            'details': {'equation': "y'=-rate*(y-cos(t))-sin(t)",
                        'reference': 'y(t)=cos(t)+(y(0)-1)*exp(-rate*t)',
                        'row_layout': 'One row per time of the finest fixed-step trajectory.',
                        'refinement': refinements, 'observed_orders': orders.tolist(),
                        'decay_reference': {'equation': "y'=-decay_rate*y; y(0)=1", 'time': decay_step,
                                            'computed': float(decay[0]), 'exact': decay_exact},
                        'scope': 'Classical order two is not assumed for unresolved stiff transients or coarse rate*h; fixed-step Newton tolerances are those of the released solver.'}}


def _periodic(p):
    _keys(p, ['positions', 'masses', 'mesh_size', 'length', 'gravity', 'periodic_shift',
              'single_position', 'single_mass', 'density_background', 'density_amplitude', 'density_mode'])
    n = _integer(p['mesh_size'], 'mesh_size', 4, 96)
    length = _number(p['length'], 'length', positive=True)
    gravity = _number(p['gravity'], 'gravity', positive=True)
    if gravity != 1:
        raise ValueError('The released pm_acceleration uses G=1')
    if not isinstance(p['positions'], list) or not 2 <= len(p['positions']) <= 10000:
        raise ValueError('Require an explicit nonempty particle cloud with at least two particles')
    positions = np.array([_vector(x, 'position', 3) for x in p['positions']])
    masses = _vector(p['masses'], 'masses', len(positions))
    if np.any(masses <= 0):
        raise ValueError('Particle masses must be positive')
    shift = _vector(p['periodic_shift'], 'periodic_shift', 3)
    if not np.all(shift == np.rint(shift)):
        raise ValueError('periodic_shift counts integer box lengths')
    single = _vector(p['single_position'], 'single_position', 3)
    single_mass = _number(p['single_mass'], 'single_mass', positive=True)
    background = _number(p['density_background'], 'density_background', positive=True)
    amplitude = _number(p['density_amplitude'], 'density_amplitude', positive=True)
    mode = _integer(p['density_mode'], 'density_mode', 1, (n-1)//2)
    if amplitude >= background:
        raise ValueError('The manufactured positive density requires amplitude < background')
    acceleration, rho, potential = pm_acceleration(positions, masses, n, length)
    wrapped, wrapped_rho, _ = pm_acceleration(positions+shift*length, masses, n, length)
    self_acceleration, _, _ = pm_acceleration(single[None, :], [single_mass], n, length)
    force = masses[:, None]*acceleration
    force_scale = float(np.sum(np.linalg.norm(force, axis=1)))
    if force_scale <= 0:
        raise ValueError('Nonzero internal forces are required for the normalized diagnostic')
    x = np.arange(n)*length/n; wave = 2*np.pi*mode/length
    density = np.broadcast_to(background+amplitude*np.cos(wave*x)[:, None, None], (n,n,n))
    phi, field = periodic_poisson(density, length, gravity)
    phi_exact = np.broadcast_to(-4*np.pi*gravity*amplitude/wave**2*np.cos(wave*x)[:, None, None], (n,n,n))
    field_exact = np.zeros_like(field)
    field_exact[0] = -4*np.pi*gravity*amplitude/wave*np.sin(wave*x)[:, None, None]
    total_mass = float(masses.sum()); deposited = float(rho.sum()*(length/n)**3)
    return {'metrics': {'mass_relative_error': float(abs(deposited-total_mass)/total_mass),
                        'internal_net_force_norm': float(np.linalg.norm(force.sum(axis=0))),
                        'internal_net_force_relative': float(np.linalg.norm(force.sum(axis=0))/force_scale),
                        'single_particle_self_acceleration': float(np.linalg.norm(self_acceleration)),
                        'periodic_shift_acceleration_max_error': float(np.max(abs(wrapped-acceleration))),
                        'periodic_shift_density_relative_error': float(np.max(abs(wrapped_rho-rho))/np.max(abs(rho))),
                        'potential_mean_absolute': float(abs(potential.mean())),
                        'manufactured_potential_max_error': float(np.max(abs(phi-phi_exact))),
                        'manufactured_acceleration_max_error': float(np.max(abs(field-field_exact))),
                        'particle_count': len(masses), 'total_mass': total_mass, 'deposited_mass': deposited},
            'table': _table(particle=np.arange(len(masses)), x=positions[:,0], y=positions[:,1], z=positions[:,2], mass=masses,
                            ax=acceleration[:,0], ay=acceleration[:,1], az=acceleration[:,2],
                            fx=force[:,0], fy=force[:,1], fz=force[:,2]),
            'details': {'row_layout': 'One row per supplied particle; force=m*acceleration. Coordinates are the supplied positions, periodically wrapped internally.',
                        'field_reference': 'rho=rho0+A*cos(k*x); phi=-4*pi*G*A*cos(k*x)/k^2; ax=-4*pi*G*A*sin(k*x)/k; ay=az=0.',
                        'boundary': 'Periodic box; subtract mean density and set phi_hat(0)=0. Matched CIC deposition/interpolation.',
                        'scope': 'The analytic mesh field is a separate manufactured-density test. Mass/net-force/self-force checks do not establish particle-force accuracy against a periodic pair sum. No isolated direct-sum comparison or particle time integration.'}}


def _taylor(p):
    _keys(p, ['grid_sizes', 'final_time', 'viscosity', 'cfl', 'time_refinement_factor'])
    levels = _levels(p['grid_sizes'], 'grid_sizes', 8, 128)
    final = _number(p['final_time'], 'final_time', positive=True)
    viscosity = _number(p['viscosity'], 'viscosity', positive=True)
    cfl = _number(p['cfl'], 'cfl', positive=True)
    factor = _integer(p['time_refinement_factor'], 'time_refinement_factor', 2, 4)
    if cfl > .4:
        raise ValueError('The released explicit MAC solver requires cfl <= 0.4')
    errors = []; refinement = []
    for n in levels:
        result = taylor_green(n, final, viscosity, cfl)
        errors.append(float(result['error']))
        refinement.append({'n': n, 'h': float(result['h']), 'velocity_rms_error': errors[-1],
                           'steps': len(result['history'])-1,
                           'maximum_divergence': float(np.max(result['history'][:,2]))})
    # Keep the spatial mesh fixed: this is a time-sensitivity diagnostic, not
    # an independently exact reference or a pure spatial-error measurement.
    half = taylor_green(levels[-1], final, viscosity, cfl/factor)
    time_change = float(np.sqrt(np.mean((result['u']-half['u'])**2+(result['v']-half['v'])**2)))
    n = levels[-1]; h = result['h']; t = result['time']
    face = np.arange(n)*h; center = face+h/2
    xu,yu = np.meshgrid(face, center, indexing='ij')
    xv,yv = np.meshgrid(center, face, indexing='ij')
    xp,yp = np.meshgrid(center, center, indexing='ij')
    # Continuum expressions, evaluated independently of the solver's exact_*.
    exact_u = np.sin(xu)*np.cos(yu)*np.exp(-2*viscosity*t)
    exact_v = -np.cos(xv)*np.sin(yv)*np.exp(-2*viscosity*t)
    exact_pressure = .25*(np.cos(2*xp)+np.cos(2*yp))*np.exp(-4*viscosity*t)
    u,v = result['u'],result['v']; history = result['history']
    exact_energy = .25*np.exp(-4*viscosity*t)
    orders = _orders(errors)
    return {'metrics': {'velocity_rms_error': float(np.sqrt(np.mean((u-exact_u)**2+(v-exact_v)**2))),
                        'minimum_observed_order': float(orders.min()),
                        'maximum_divergence': float(np.max(history[:,2])),
                        'pressure_mean_absolute': float(abs(result['pressure'].mean())),
                        'pressure_rms_error': float(np.sqrt(np.mean((result['pressure']-exact_pressure)**2))),
                        'relative_final_energy_error': float(abs(history[-1,1]-exact_energy)/exact_energy),
                        'maximum_energy_increase': float(max(0., np.max(np.diff(history[:,1])))),
                        'time_refinement_change': time_change,
                        'time_change_to_combined_error_ratio': time_change/errors[-1],
                        'final_time_error': float(abs(t-final))},
            'table': _table(i=np.repeat(np.arange(n),n), j=np.tile(np.arange(n),n),
                            x_u=xu, y_u=yu, u=u, u_exact=exact_u,
                            x_v=xv, y_v=yv, v=v, v_exact=exact_v,
                            x_pressure=xp, y_pressure=yp, pressure=result['pressure'], pressure_exact=exact_pressure),
            'details': {'row_layout': 'One row per (i,j), C order. MAC u, v and pressure have separate coordinate columns and are not collocated.',
                        'reference': 'u=sin(x)*cos(y)*exp(-2*nu*t); v=-cos(x)*sin(y)*exp(-2*nu*t); p=(cos(2*x)+cos(2*y))*exp(-4*nu*t)/4, mean(p)=0.',
                        'refinement': refinement, 'observed_orders': orders.tolist(),
                        'energy_history': {'time': history[:,0].tolist(), 'kinetic_energy_mean': history[:,1].tolist()},
                        'time_refinement': {'factor': factor, 'steps': len(half['history'])-1, 'velocity_change_rms': time_change},
                        'scope': 'Uniform refinement changes space and stable time step together. Fixed-grid CFL reduction estimates temporal sensitivity; it is not an exact temporal-error bound. Unit density; periodic [0,2*pi)^2.'}}


def run(problem_id, parameters):
    """Calculate one of four fixed-model recipes without writing files."""
    handlers = {'harmonic-oscillator': _harmonic, 'stiff-cosine': _stiff,
                'periodic-particles': _periodic, 'taylor-green': _taylor}
    if not isinstance(problem_id, str) or problem_id not in handlers:
        raise ValueError('Unknown dynamics/particle recipe')
    return handlers[problem_id](parameters)
