#!/usr/bin/env python3
"""Build a checked common execution registry; never modify immutable code editions."""
from pathlib import Path, PurePosixPath
import argparse
import copy
import hashlib
import json
import math
import re
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://hrkoyama.github.io'
ROUTE = '/numerical-methods-atlas/code-and-data/examples.json'
CATALOG = ROOT / 'catalog/atlas-execution-examples.json'
CHECK_TYPES = {'equals', 'maximum', 'absolute_maximum', 'abs_difference', 'all_true'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(data):
    return (json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def safe_path(value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('Invalid relative artifact path')
    path = PurePosixPath(value)
    if path.is_absolute() or any(x in ('', '.', '..') for x in value.split('/')):
        raise ValueError('Unsafe relative artifact path')
    return path


def public_path(url):
    parsed = urlparse(url)
    if parsed.scheme != 'https' or parsed.netloc != 'hrkoyama.github.io' or parsed.query or parsed.fragment:
        raise ValueError('Artifacts must use canonical public HTTPS URLs')
    return safe_path(unquote(parsed.path).lstrip('/'))


def hash_field(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('Invalid SHA-256 value')


def validate_registry(data):
    if type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        raise ValueError('Unsupported execution-registry schema version')
    rows = data.get('examples')
    if not isinstance(rows, list) or not rows:
        raise ValueError('An execution registry requires examples')
    ids = [x['id'] for x in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate execution-example ID')
    for x in rows:
        if not re.fullmatch('[a-z0-9-]+', x['id']):
            raise ValueError('Invalid example ID')
        for key in ['name', 'scope', 'assumptions', 'units', 'boundaries']:
            if not all(isinstance(x.get(key, {}).get(l), str) and x[key][l] for l in ['ja', 'en']):
                raise ValueError('Missing bilingual field: ' + key)
        if not x.get('problem_id') or not x.get('method_ids'):
            raise ValueError('Problem and method links are required')
        release = x['release']
        public_path(release['download']); public_path(release['manifest']); public_path(release['verification'])
        hash_field(release['sha256']); hash_field(release['manifest_sha256'])
        safe_path(release['archive_directory'])
        for asset in [x['inputs'], *x['outputs'], *[r for r in x['references'] if 'sha256' in r]]:
            public_path(asset['url']); safe_path(asset['path']); hash_field(asset['sha256'])
            if 'generated_path' in asset:
                safe_path(asset['generated_path'])
        if not any(y['id'] == 'results' and y['format'] == 'json' for y in x['outputs']):
            raise ValueError('A JSON result output is required')
        for key in ['install', 'run', 'tests']:
            if not isinstance(x['commands'][key], str) or not x['commands'][key]:
                raise ValueError('Display commands must be nonempty strings')
        argv = x['commands']['run_argv']
        if not argv or argv[0] != 'python' or argv.count('{output}') != 1:
            raise ValueError('Runner must use the selected Python and an explicit output directory')
        for url in x['dependencies'].values():
            public_path(url)
        if not x.get('checks'):
            raise ValueError('Numerical checks are required')
        for c in [*x['checks'], *x.get('expected_failures', [])]:
            if c['comparison'] not in CHECK_TYPES or not c['pointer'].startswith('/'):
                raise ValueError('Unsupported check contract')
            if c['comparison'] in {'maximum', 'absolute_maximum', 'abs_difference'}:
                t = c.get('tolerance')
                if isinstance(t, bool) or not isinstance(t, (int, float)) or not math.isfinite(t) or t < 0:
                    raise ValueError('A finite nonnegative tolerance is required')
        if set(x['shared_runner_cases']) - set(ids):
            raise ValueError('Unknown shared-runner case')
    for group in {x['execution_group'] for x in rows}:
        cases = [x for x in rows if x['execution_group'] == group]
        first = cases[0]
        for x in cases:
            if set(x['shared_runner_cases']) != {y['id'] for y in cases}:
                raise ValueError('Shared-runner membership is inconsistent')
            for key in ['release', 'inputs', 'commands']:
                if x[key] != first[key]:
                    raise ValueError('A shared runner must have identical code, input and command')
    return data


def pointer(document, path):
    value = document
    for part in path.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def evaluate_check(document, spec):
    result = {k: copy.deepcopy(v) for k, v in spec.items() if k != 'description'}
    try:
        value = pointer(document, spec['pointer'])
        if 'where' in spec:
            if not isinstance(value, list):
                raise ValueError('Selector target must be an array')
            value = [x for x in value if all(x.get(k) == v for k, v in spec['where'].items())]
            if not value:
                raise ValueError('Selector matched no result')
        if 'field' in spec:
            if not isinstance(value, list) or not value:
                raise ValueError('A result array is required')
            value = [x[spec['field']] for x in value]
        result['observed'] = value
        values = value if isinstance(value, list) else [value]
        if not values:
            raise ValueError('Empty result cannot pass')
        mode = spec['comparison']
        if mode == 'all_true':
            flags = list(value.values()) if isinstance(value, dict) else values
            passed = bool(flags) and all(v is True for v in flags)
        elif mode == 'equals':
            expected = spec['expected']
            passed = all(v == expected and (type(v) is bool if type(expected) is bool else type(v) is not bool) for v in values)
        else:
            if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
                raise ValueError('Numerical check needs finite numbers')
            if mode == 'abs_difference':
                errors = [abs(v - spec['expected']) for v in values]
            elif mode == 'absolute_maximum':
                errors = [abs(v) for v in values]
            else:
                if any(v < 0 for v in values):
                    raise ValueError('Error/residual metric must be nonnegative')
                errors = values
            result['maximum_residual'] = max(errors)
            passed = all(v <= spec['tolerance'] for v in errors)
        result['passed'] = bool(passed)
    except (KeyError, IndexError, TypeError, ValueError, OverflowError):
        result.update(passed=False, error='missing_or_incompatible_result_field')
    return result


def build_registry(data, root=ROOT, source_bytes=None):
    validate_registry(data)
    result = copy.deepcopy(data)
    source_bytes = encode(data) if source_bytes is None else source_bytes
    result.update(url=ORIGIN + ROUTE, catalog_source={'url':ORIGIN + '/catalog/atlas-execution-examples.json', 'sha256':digest(source_bytes)})
    for x in result['examples']:
        r = x['release']
        manifest_bytes = (root / public_path(r['manifest'])).read_bytes()
        if digest(manifest_bytes) != r['manifest_sha256'] or digest((root / public_path(r['download'])).read_bytes()) != r['sha256']:
            raise ValueError('Release digest mismatch: ' + x['id'])
        manifest = json.loads(manifest_bytes)
        if manifest['edition'] != r['version']:
            raise ValueError('Release edition mismatch')
        release_base = (root / public_path(r['manifest'])).parent
        for path, expected in manifest['files'].items():
            if digest((release_base / safe_path(path)).read_bytes()) != expected:
                raise ValueError('Source manifest mismatch: ' + path)
        verification = json.loads((root / public_path(r['verification'])).read_bytes())
        if verification['archive_sha256'] != r['sha256'] or verification['failures'] or verification['errors']:
            raise ValueError('Packaged verification does not match the release')
        for asset in [x['inputs'], *x['outputs'], *[a for a in x['references'] if 'sha256' in a]]:
            if manifest['files'].get(asset['path']) != asset['sha256'] or digest((root / public_path(asset['url'])).read_bytes()) != asset['sha256']:
                raise ValueError('Input/output receipt mismatch')
        for url in x['dependencies'].values():
            file = (root / public_path(url)).relative_to(release_base).as_posix()
            if file not in manifest['files']:
                raise ValueError('Dependency instructions are outside the verified release')
        raw = next(a for a in x['outputs'] if a['id'] == 'results')
        document = json.loads((root / public_path(raw['url'])).read_bytes())
        if not all(evaluate_check(document, c)['passed'] for c in [*x['checks'], *x.get('expected_failures', [])]):
            raise ValueError('The saved reference does not satisfy the advertised checks: ' + x['id'])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, default=CATALOG)
    parser.add_argument('--output', type=Path, default=ROOT / ROUTE.lstrip('/'))
    args = parser.parse_args()
    raw = args.catalog.read_bytes()
    registry = build_registry(json.loads(raw), source_bytes=raw)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encode(registry))
    print('Built common execution registry:', len(registry['examples']), 'existing problem families.')


if __name__ == '__main__':
    main()
