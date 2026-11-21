"""Four fixed elliptic/approximation recipes around released numart kernels.

No files are written here. Analytic solutions, residual stencils and validation
quadrature are evaluated separately from the solver paths being exercised.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss

from numart import basis, fem, linear, poisson_comparison
from numart.krylov import CSR, newton


def _keys(parameters, required):
    if not isinstance(parameters, dict) or set(parameters) != set(required):
        raise ValueError('Parameters must contain exactly: '+', '.join(required))


def _integer(value, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError('Integer outside the supported recipe range')
    return value


def _number(value, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value) or not low <= value <= high:
        raise ValueError('Finite numeric parameter outside the supported recipe range')
    return float(value)


def _levels(values, low, high, interior=True):
    if not isinstance(values, list) or len(values) < 2:
        raise ValueError('At least two refinement levels are required')
    levels = [_integer(n, low, high) for n in values]
    offset = 1 if interior else 0
    if any(b+offset != 2*(a+offset) for a, b in zip(levels, levels[1:])):
        raise ValueError('Refinement must halve the mesh spacing at each level')
    return levels


def _domain(parameters, expected):
    values = parameters['domain']
    if not isinstance(values, list) or len(values) != len(expected):
        raise ValueError('Invalid domain declaration')
    if [_number(x, -10., 10.) for x in values] != expected:
        raise ValueError('This recipe uses the declared fixed reference domain')


def _orders(errors):
    errors = np.asarray(errors, dtype=float)
    if not np.isfinite(errors).all() or np.any(errors <= 0):
        raise RuntimeError('Refinement errors must be finite and positive')
    return np.log2(errors[:-1]/errors[1:]).tolist()


def _table(**columns):
    return {name: np.asarray(values, dtype=float).ravel().tolist()
            for name, values in columns.items()}


def _poisson_1d(p):
    _keys(p, ['interior_nodes', 'domain', 'boundary_values', 'forcing', 'solver'])
    _domain(p, [0., 1.])
    if p['boundary_values'] != [0., 0.] or p['forcing'] != 'pi^2*sin(pi*x)' or p['solver'] != 'thomas':
        raise ValueError('Unsupported 1D Poisson model or solver')
    levels = _levels(p['interior_nodes'], 3, 4095)
    errors, residuals, rows = [], [], []
    for n in levels:
        x, u = linear.poisson_1d(n)
        exact = np.sin(np.pi*x)
        h = 1/(n+1)
        padded = np.r_[0., u, 0.]
        forcing = np.pi**2*np.sin(np.pi*x)
        residual = (2*u-padded[:-2]-padded[2:])/h**2-forcing
        errors.append(float(np.max(abs(u-exact))))
        residuals.append(float(np.linalg.norm(residual)/np.linalg.norm(forcing)))
        rows.append({'interior_nodes': n, 'h': h, 'linf_error': errors[-1],
                     'true_relative_residual': residuals[-1]})
    grid = np.r_[0., x, 1.]
    solution = np.r_[0., u, 0.]
    reference = np.sin(np.pi*grid)
    return {'metrics': {'finest_linf_error': errors[-1],
                        'minimum_observed_order': min(_orders(errors)),
                        'maximum_true_relative_residual': max(residuals),
                        'boundary_maximum_absolute_value': float(max(abs(solution[0]), abs(solution[-1])))},
            'table': _table(x=grid, solution=solution, reference=reference,
                            absolute_error=abs(solution-reference)),
            'details': {'equation': '-u_xx=pi^2*sin(pi*x)',
                        'reference_type': 'analytic continuous solution sin(pi*x)',
                        'refinement': rows, 'observed_orders': _orders(errors),
                        'table_layout': 'Finest mesh, including both Dirichlet boundary nodes; every row shares x.'}}


def _sine_reference(points):
    return np.sin(np.pi*points[:, 0])*np.sin(np.pi*points[:, 1])


def _fem_errors(result, quadrature_order):
    """Independent element-interior L2 and H1-seminorm evaluation.

    A Duffy parameterization different from numart.fem.triangle_quadrature is
    used, with direct affine gradients rather than the solver's inverse basis.
    """
    z, w = leggauss(quadrature_order)
    z, w = (z+1)/2, w/2
    r, s = np.meshgrid(z, z, indexing='ij')
    xi, eta = r.ravel(), ((1-r)*s).ravel()
    barycentric = np.column_stack((1-xi-eta, xi, eta))
    reference_weights = (np.outer(w, w)*(1-r)).ravel()
    reference_gradients = np.array([[-1., -1.], [1., 0.], [0., 1.]])
    l2_squared, h1_squared = 0., 0.
    for cell in result.cells:
        vertices = result.points[cell]
        jacobian = np.column_stack((vertices[1]-vertices[0], vertices[2]-vertices[0]))
        weights = reference_weights*abs(np.linalg.det(jacobian))
        points = vertices[0]+np.column_stack((xi, eta))@jacobian.T
        exact_gradient = np.pi*np.column_stack((
            np.cos(np.pi*points[:, 0])*np.sin(np.pi*points[:, 1]),
            np.sin(np.pi*points[:, 0])*np.cos(np.pi*points[:, 1])))
        value_error = barycentric@result.u[cell]-_sine_reference(points)
        gradient_error = result.u[cell]@(reference_gradients@np.linalg.inv(jacobian))-exact_gradient
        l2_squared += float(weights@value_error**2)
        h1_squared += float(weights@np.sum(gradient_error**2, axis=1))
    return float(np.sqrt(l2_squared)), float(np.sqrt(h1_squared))


def _poisson_2d(p):
    _keys(p, ['interior_nodes', 'fem_subdivisions', 'domain', 'boundary_value',
              'forcing', 'finite_difference_solvers', 'relative_tolerance',
              'max_steps', 'fem_error_quadrature_order'])
    _domain(p, [0., 1., 0., 1.])
    if p['boundary_value'] != 0. or p['forcing'] != '2*pi^2*sin(pi*x)*sin(pi*y)' or p['finite_difference_solvers'] != ['cg', 'multigrid']:
        raise ValueError('Unsupported 2D Poisson model or solver comparison')
    levels = _levels(p['interior_nodes'], 3, 127)
    if any((n+1)&n for n in levels):
        raise ValueError('Multigrid needs n=2^k-1 interior nodes')
    fem_levels = _levels(p['fem_subdivisions'], 2, 64, interior=False)
    tolerance = _number(p['relative_tolerance'], 1e-14, 1e-3)
    max_steps = _integer(p['max_steps'], 1, 10000)
    quadrature = _integer(p['fem_error_quadrature_order'], 4, 16)
    errors = {'cg': [], 'multigrid': []}
    residuals, differences, finite_difference_rows = [], [], []
    csv_rows = []
    for n in levels:
        h = 1/(n+1)
        grid = np.arange(1, n+1)*h
        x, y = np.meshgrid(grid, grid, indexing='ij')
        exact = np.sin(np.pi*x)*np.sin(np.pi*y)
        forcing = 2*np.pi**2*exact
        solutions = {}
        for code, method in enumerate(p['finite_difference_solvers']):
            result = poisson_comparison.solve(forcing, method=method,
                tolerance=tolerance, max_steps=max_steps)
            if not result.converged:
                raise RuntimeError(method+' did not meet its solver tolerance')
            q = result.q
            padded = np.pad(q, 1)
            actual = (4*q-padded[:-2, 1:-1]-padded[2:, 1:-1]
                      -padded[1:-1, :-2]-padded[1:-1, 2:])/h**2-forcing
            residual = float(np.linalg.norm(actual)/np.linalg.norm(forcing))
            errors[method].append(float(np.max(abs(q-exact))))
            residuals.append(residual)
            finite_difference_rows.append({'method': method, 'interior_nodes': n,
                'linf_error': errors[method][-1], 'true_relative_residual': residual,
                'iterations_or_cycles': int(result.steps)})
            solutions[method] = q
            if n == levels[-1]:
                full_grid = np.linspace(0., 1., n+2)
                xx, yy = np.meshgrid(full_grid, full_grid, indexing='ij')
                values = np.pad(q, 1)
                reference = np.sin(np.pi*xx)*np.sin(np.pi*yy)
                csv_rows.extend(zip(np.full(xx.size, code), np.full(xx.size, n),
                    xx.ravel(), yy.ravel(), values.ravel(), reference.ravel(),
                    abs(values-reference).ravel()))
        differences.append(float(np.max(abs(solutions['cg']-solutions['multigrid']))))
    fem_l2, fem_h1, fem_residuals, fem_boundaries, fem_rows = [], [], [], [], []
    for n in fem_levels:
        result = fem.poisson_2d(n)
        l2, h1 = _fem_errors(result, quadrature)
        boundary = np.any((result.points == 0.) | (result.points == 1.), axis=1)
        residual = result.stiffness.matvec(result.u)-result.rhs
        true_residual = float(np.linalg.norm(residual[~boundary])/np.linalg.norm(result.rhs[~boundary]))
        fem_l2.append(l2); fem_h1.append(h1); fem_residuals.append(true_residual)
        fem_boundaries.append(float(np.max(abs(result.u[boundary]))))
        fem_rows.append({'subdivisions_per_axis': n, 'l2_error': l2,
            'h1_seminorm_error': h1, 'interior_true_relative_residual': true_residual})
        if n == fem_levels[-1]:
            exact = _sine_reference(result.points)
            csv_rows.extend(zip(np.full(len(exact), 2), np.full(len(exact), n),
                result.points[:, 0], result.points[:, 1], result.u, exact, abs(result.u-exact)))
    columns = np.asarray(csv_rows).T
    return {'metrics': {'fd_finest_cg_linf_error': errors['cg'][-1],
        'fd_finest_multigrid_linf_error': errors['multigrid'][-1],
        'fd_minimum_observed_order': min(min(_orders(e)) for e in errors.values()),
        'fd_maximum_true_relative_residual': max(residuals),
        'fd_maximum_cg_multigrid_difference': max(differences),
        'fem_finest_l2_error': fem_l2[-1], 'fem_finest_h1_seminorm_error': fem_h1[-1],
        'fem_minimum_l2_order': min(_orders(fem_l2)),
        'fem_minimum_h1_seminorm_order': min(_orders(fem_h1)),
        'fem_maximum_interior_true_relative_residual': max(fem_residuals),
        'fem_boundary_maximum_absolute_value': max(fem_boundaries)},
        'table': _table(method_code=columns[0], resolution=columns[1], x=columns[2],
            y=columns[3], solution=columns[4], reference=columns[5], absolute_error=columns[6]),
        'details': {'analytic_solution': 'sin(pi*x)*sin(pi*y)',
            'finite_difference_refinement': finite_difference_rows, 'fem_refinement': fem_rows,
            'fem_l2_orders': _orders(fem_l2), 'fem_h1_seminorm_orders': _orders(fem_h1),
            'fem_error_definition': 'L2 integrates the value error; H1 seminorm integrates the gradient error inside each triangle. These are not nodal norms.',
            'table_layout': 'Finest meshes only. method_code 0=CG, 1=multigrid, 2=P1 FEM. resolution is interior nodes per axis for FD and cells per axis before triangle splitting for FEM. Reference is evaluated at each row coordinate, including boundary nodes.',
            'scope': 'The sine source is one discrete eigenmode, so rapid CG termination is not a general performance benchmark. FEM and FD use different meshes; their continuous-error norms are reported separately.'}}


def _bratu(p):
    _keys(p, ['interior_nodes', 'domain', 'boundary_values', 'beta', 'branch',
              'initial_guess', 'nonlinear_tolerance', 'max_iterations', 'linear_solver'])
    _domain(p, [0., 1.])
    beta = _number(p['beta'], 1e-3, 2.39)
    if p['branch'] != 'lower' or beta*np.tanh(beta/2) >= 2 or p['boundary_values'] != [0., 0.] or p['initial_guess'] != 0. or p['linear_solver'] != 'gmres':
        raise ValueError('This recipe selects the lower branch with a zero initial guess and Newton–GMRES')
    levels = _levels(p['interior_nodes'], 3, 1023)
    tolerance = _number(p['nonlinear_tolerance'], 1e-13, 1e-3)
    max_iterations = _integer(p['max_iterations'], 1, 100)
    lam = 2*beta**2/np.cosh(beta/2)**2
    errors, residuals, rows = [], [], []
    for n in levels:
        h = 1/(n+1)
        x = np.arange(1, n+1)*h
        def residual(q):
            padded = np.r_[0., q, 0.]
            return (2*q-padded[:-2]-padded[2:])/h**2-lam*np.exp(q)
        def jacobian(q):
            indices = np.arange(n)
            return CSR.from_coo(np.r_[indices, indices[:-1], indices[1:]],
                np.r_[indices, indices[1:], indices[:-1]],
                np.r_[2/h**2-lam*np.exp(q), np.full(2*(n-1), -1/h**2)], (n, n))
        result = newton(residual, jacobian, np.zeros(n), tolerance=tolerance,
                        maxiter=max_iterations, linear_solver='gmres')
        if not result.converged:
            raise RuntimeError('Bratu Newton solve failed: '+result.reason)
        exact = 2*(np.log(np.cosh(beta/2))-np.log(np.cosh(beta*(x-.5))))
        # Recompute with an independently expressed second-difference stencil.
        actual = -(np.diff(np.r_[0., result.x, 0.], n=2))/h**2-lam*np.exp(result.x)
        errors.append(float(np.max(abs(result.x-exact))))
        residuals.append(float(np.linalg.norm(actual)))
        rows.append({'interior_nodes': n, 'linf_error': errors[-1],
            'independent_residual_l2': residuals[-1],
            'newton_iterations': len(result.step_lengths),
            'minimum_step_length': float(np.min(result.step_lengths))})
    grid = np.r_[0., x, 1.]
    solution = np.r_[0., result.x, 0.]
    reference = 2*(np.log(np.cosh(beta/2))-np.log(np.cosh(beta*(grid-.5))))
    return {'metrics': {'all_converged': True, 'lambda': float(lam),
        'finest_linf_error': errors[-1], 'minimum_observed_order': min(_orders(errors)),
        'maximum_independent_residual_l2': max(residuals),
        'boundary_maximum_absolute_value': float(max(abs(solution[0]), abs(solution[-1])))},
        'table': _table(x=grid, solution=solution, reference=reference,
            absolute_error=abs(solution-reference)),
        'details': {'equation': '-u_xx=lambda*exp(u)',
            'analytic_solution': 'u(x)=2*log(cosh(beta/2)/cosh(beta*(x-1/2))); lambda=2*beta^2/cosh(beta/2)^2',
            'branch_selection': 'beta*tanh(beta/2)<2 parameterizes the small/lower solution branch; the nonlinear solve starts at zero. No upper-branch continuation is attempted.',
            'refinement': rows, 'observed_orders': _orders(errors),
            'table_layout': 'Finest mesh with both boundary nodes; analytic and computed values share x.'}}


def _legendre_recurrence(x, degree):
    values = np.ones((len(x), degree+1))
    if degree:
        values[:, 1] = x
    for k in range(1, degree):
        values[:, k+1] = ((2*k+1)*x*values[:, k]-k*values[:, k-1])/(k+1)
    return values


def _projection(p):
    _keys(p, ['domain', 'function', 'degrees', 'projection_quadrature_order',
              'reference_quadrature_orders', 'interpolation_nodes', 'evaluation_points'])
    _domain(p, [-1., 1.])
    if p['function'] != 'exp(x)' or p['interpolation_nodes'] != 'gll':
        raise ValueError('This smooth-function recipe uses exp(x) and GLL interpolation')
    if not isinstance(p['degrees'], list) or len(p['degrees']) < 2:
        raise ValueError('At least two polynomial degrees required')
    degrees = [_integer(k, 1, 12) for k in p['degrees']]
    if degrees != sorted(set(degrees)):
        raise ValueError('Degrees must be distinct and increasing')
    order = _integer(p['projection_quadrature_order'], max(degrees)+1, 128)
    reference_orders = p['reference_quadrature_orders']
    if not isinstance(reference_orders, list) or len(reference_orders) != 2:
        raise ValueError('Two independent reference quadrature orders required')
    first = _integer(reference_orders[0], order+1, 256)
    second = _integer(reference_orders[1], first+1, 512)
    evaluation_points = _integer(p['evaluation_points'], 3, 10001)
    evaluation_grid = np.linspace(-1., 1., evaluation_points)
    validation = [leggauss(first), leggauss(second)]
    l2_errors, nodal_errors, coefficients_errors, defects, quadrature_agreement = [], [], [], [], []
    rows, csv_rows = [], []
    for degree in degrees:
        coefficients = basis.project_legendre(np.exp, degree, quadrature_order=order)
        nodes, _ = basis.lobatto(degree)
        l2_by_rule, nodal_by_rule, c_reference = [], [], []
        for x, w in validation:
            # Separate recurrence and quadrature orders from project_legendre.
            polynomials = _legendre_recurrence(x, degree)
            exact = np.exp(x)
            c_reference.append((polynomials.T@(w*exact))*(2*np.arange(degree+1)+1)/2)
            approximation = polynomials@coefficients
            interpolant = basis.lagrange(x, nodes)@np.exp(nodes)
            l2_by_rule.append(float(np.sqrt(w@(approximation-exact)**2)))
            nodal_by_rule.append(float(np.sqrt(w@(interpolant-exact)**2)))
            defects.append(float(np.max(abs(polynomials.T@(w*(approximation-exact))))))
        error = l2_by_rule[-1]
        l2_errors.append(error); nodal_errors.append(nodal_by_rule[-1])
        coefficients_errors.append(float(np.max(abs(coefficients-c_reference[-1]))))
        quadrature_agreement.append(float(max(abs(np.asarray(l2_by_rule)-l2_by_rule[-1]).max(),
                                             abs(np.asarray(nodal_by_rule)-nodal_by_rule[-1]).max())))
        rows.append({'degree': degree, 'projection_l2_error': error,
            'gll_interpolation_l2_error': nodal_errors[-1],
            'independent_coefficient_maximum_difference': coefficients_errors[-1]})
        approximation = np.einsum('ij,j->i', basis.legendre(evaluation_grid, degree), coefficients)
        interpolant = np.einsum('ij,j->i', basis.lagrange(evaluation_grid, nodes), np.exp(nodes))
        exact = np.exp(evaluation_grid)
        csv_rows.extend(zip(np.full(evaluation_points, degree), evaluation_grid,
            approximation, interpolant, exact, abs(approximation-exact), abs(interpolant-exact)))
    columns = np.asarray(csv_rows).T
    return {'metrics': {'finest_projection_l2_error': l2_errors[-1],
        'finest_gll_interpolation_l2_error': nodal_errors[-1],
        'minimum_projection_error_reduction': float(np.min(np.asarray(l2_errors[:-1])/l2_errors[1:])),
        'minimum_interpolation_error_reduction': float(np.min(np.asarray(nodal_errors[:-1])/nodal_errors[1:])),
        'maximum_independent_coefficient_difference': max(coefficients_errors),
        'maximum_projection_orthogonality_defect': max(defects),
        'maximum_reference_quadrature_disagreement': max(quadrature_agreement)},
        'table': _table(degree=columns[0], x=columns[1], projection=columns[2],
            gll_interpolation=columns[3], reference=columns[4],
            projection_absolute_error=columns[5], interpolation_absolute_error=columns[6]),
        'details': {'reference_type': 'Analytic exp(x) values; L2 norms and independent modal coefficients use higher-order Gauss quadrature, not an exact integral claim.',
            'degree_refinement': rows,
            'independence': 'Projection uses released project_legendre at the input order. Reference coefficients and orthogonality use a separately coded three-term Legendre recurrence with two higher quadrature orders. No comparison merely repeats the projection quadrature.',
            'table_layout': 'Each degree contributes evaluation_points rows on the same inclusive [-1,1] grid. Projection, GLL interpolation and exp(x) align at each row coordinate.',
            'scope': 'Smooth-function p refinement only; no discontinuity or general spectral-element PDE validation.'}}


def run(problem_id, parameters):
    functions = {'poisson-1d-dirichlet': _poisson_1d, 'poisson-2d-sine': _poisson_2d,
                 'bratu': _bratu, 'smooth-function-projection': _projection}
    if problem_id not in functions:
        raise ValueError('Unknown elliptic/basis recipe: '+str(problem_id))
    return functions[problem_id](parameters)
