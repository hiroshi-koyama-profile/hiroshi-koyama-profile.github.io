#!/usr/bin/env python3
"""Fetch public code/input/reference artifacts and execute the curated examples.

No dependencies are installed. Use an existing Python environment that satisfies
both releases. --registry may be the local source catalog before first publication;
all scientific artifacts are still downloaded from their public HTTPS URLs.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import importlib.util
import io
import json
import os
import platform
import stat
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('execution_registry', HERE / 'build-atlas-execution-examples.py')
registry_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry_module)
REGISTRY_URL = registry_module.ORIGIN + registry_module.ROUTE
sha = registry_module.digest


def checked_download(url, expected=None, limit=20_000_000):
    path = registry_module.public_path(url)
    if not (str(path).startswith('code/') or url == REGISTRY_URL):
        raise ValueError('Only the public registry and immutable code artifacts may be downloaded')
    request = urllib.request.Request(url, headers={'User-Agent':'Atlas-example-verification/1.0'})
    with urllib.request.urlopen(request, timeout=60) as response:
        registry_module.public_path(response.geturl())
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError('Artifact exceeds download budget')
    if expected is not None and sha(data) != expected:
        raise ValueError('Downloaded artifact SHA-256 mismatch')
    return data


def safe_extract(data, manifest, release, destination):
    """Extract exactly the verified edition, rejecting traversal, links and bombs."""
    prefix = release['archive_directory'] + '/'
    allowed = {prefix + str(registry_module.safe_path(p)) for p in manifest['files']}
    allowed.add(prefix + 'source-manifest.json')
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        if len(infos) != len(allowed) or {x.filename for x in infos} != allowed:
            raise ValueError('Archive entries do not match the source manifest')
        if sum(x.file_size for x in infos) > 50_000_000:
            raise ValueError('Archive exceeds expanded-size budget')
        for entry in infos:
            registry_module.safe_path(entry.filename)
            if stat.S_IFMT(entry.external_attr >> 16) == stat.S_IFLNK:
                raise ValueError('Symbolic links are not permitted in code archives')
            payload = archive.read(entry)
            relative = entry.filename[len(prefix):]
            expected = release['manifest_sha256'] if relative == 'source-manifest.json' else manifest['files'][relative]
            if sha(payload) != expected:
                raise ValueError('Archived file SHA-256 mismatch')
            target = destination / entry.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
    return destination / release['archive_directory']


def check_case(example, output):
    result_file = next(x['generated_path'] for x in example['outputs'] if x['id'] == 'results')
    try:
        document = json.loads((output / result_file).read_bytes())
    except (OSError, ValueError):
        return {'passed':False, 'checks':[], 'expected_failures':[], 'error':'missing_or_invalid_result_json'}
    checks = [registry_module.evaluate_check(document, c) for c in example['checks']]
    failures = [registry_module.evaluate_check(document, c) for c in example.get('expected_failures', [])]
    for artifact in example['outputs']:
        path = output / artifact['generated_path']
        good = path.is_file() and path.stat().st_size > 0
        if artifact['format'] == 'csv' and good:
            # A populated numerical table must contain header and data rows.
            with path.open() as handle:
                good = bool(handle.readline().strip() and handle.readline().strip())
        check = {'id':'output-' + artifact['id'], 'passed':good, 'generated_path':artifact['generated_path'], 'comparison':'nonempty_artifact'}
        if path.is_file():
            check.update(sha256=sha(path.read_bytes()), bytes=path.stat().st_size)
        checks.append(check)
    return {'passed':all(x['passed'] for x in checks + failures), 'checks':checks, 'expected_failures':failures}


def run_registry(registry, python, timeout=300):
    registry_module.validate_registry(registry)
    groups = {}
    for x in registry['examples']:
        groups.setdefault(x['execution_group'], []).append(x)
    receipts = []; examples = []
    with tempfile.TemporaryDirectory(prefix='atlas-public-verification-') as temporary:
        temporary = Path(temporary)
        env = {k:v for k,v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME'}}
        env.update(PYTHONDONTWRITEBYTECODE='1', MPLCONFIGDIR=str(temporary / 'plot-cache'))
        versions = subprocess.run([python, '-c', 'import json,platform,importlib.metadata as m;print(json.dumps({"python":platform.python_version(),"numpy":m.version("numpy"),"scipy":m.version("scipy"),"matplotlib":m.version("matplotlib")}))'], text=True, capture_output=True, env=env, timeout=30)
        if versions.returncode:
            raise ValueError('Selected Python must already contain NumPy, SciPy and Matplotlib; no installation was attempted')
        environment = {**json.loads(versions.stdout), 'operating_system':platform.system(), 'machine':platform.machine()}
        for group, cases in groups.items():
            first = cases[0]; release = first['release']
            manifest_bytes = checked_download(release['manifest'], release['manifest_sha256'])
            manifest = json.loads(manifest_bytes)
            if manifest['edition'] != release['version']:
                raise ValueError('Downloaded source edition mismatch')
            archive_bytes = checked_download(release['download'], release['sha256'])
            packaged_verification = json.loads(checked_download(release['verification']))
            if packaged_verification['archive_sha256'] != release['sha256'] or packaged_verification['failures'] or packaged_verification['errors']:
                raise ValueError('Existing release verification is incompatible')
            folder = safe_extract(archive_bytes, manifest, release, temporary / group)
            downloaded = []
            seen = set()
            for case in cases:
                assets = [case['inputs'], *case['outputs'], *[x for x in case['references'] if 'sha256' in x]]
                for artifact in assets:
                    if artifact['url'] in seen:
                        continue
                    seen.add(artifact['url'])
                    if manifest['files'].get(artifact['path']) != artifact['sha256']:
                        raise ValueError('Artifact is not covered by the verified source manifest')
                    payload = checked_download(artifact['url'], artifact['sha256'])
                    if payload != (folder / artifact['path']).read_bytes():
                        raise ValueError('Standalone artifact differs from archived copy')
                    downloaded.append({'url':artifact['url'], 'sha256':artifact['sha256'], 'bytes':len(payload)})
            output = temporary / ('output-' + group)
            argv = [python if i == 0 else str(output) if arg == '{output}' else arg for i, arg in enumerate(first['commands']['run_argv'])]
            started = time.monotonic(); timed_out = False
            try:
                completed = subprocess.run(argv, cwd=folder, env=env, text=True, capture_output=True, timeout=timeout)
                exit_code = completed.returncode
            except subprocess.TimeoutExpired:
                exit_code = None; timed_out = True
            duration = round(time.monotonic() - started, 6)
            execution = {'group':group, 'completed':exit_code == 0, 'exit_code':exit_code, 'timed_out':timed_out, 'duration_seconds':duration, 'shared_runner_cases':[x['id'] for x in cases], 'command':first['commands']['run']}
            receipts.append({'family':release['family'], 'version':release['version'], 'download':release['download'], 'sha256':release['sha256'], 'archive_bytes':len(archive_bytes), 'manifest':release['manifest'], 'manifest_sha256':release['manifest_sha256'], 'archived_files_verified':len(manifest['files']), 'downloaded_artifacts':downloaded, 'execution':execution})
            for case in cases:
                validation = check_case(case, output)
                residuals = {c['id']:c['maximum_residual'] for c in validation['checks'] if 'maximum_residual' in c}
                examples.append({'id':case['id'], 'problem_id':case['problem_id'], 'execution':execution, 'validation':validation, 'residuals':residuals, 'passed':execution['completed'] and validation['passed']})
    return environment, receipts, examples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', default=REGISTRY_URL, help='Public registry URL or local registry/catalog path before first publication')
    parser.add_argument('--python', default=sys.executable, help='Existing Python with both code editions’ dependencies')
    parser.add_argument('--output', type=Path, required=True, help='Report JSON to write; never modifies a code edition')
    parser.add_argument('--timeout', type=int, default=300, help='Maximum seconds per shared runner')
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    if args.registry.startswith('https://'):
        raw = checked_download(args.registry)
        registry = json.loads(raw)
        if registry.get('url') != REGISTRY_URL or 'catalog_source' not in registry:
            raise ValueError('Remote registry is missing canonical metadata')
        source_mode = 'public-registry'
    else:
        raw_catalog = Path(args.registry).read_bytes()
        data = json.loads(raw_catalog)
        if 'catalog_source' in data:
            registry = data
            raw = raw_catalog
            source_mode = 'local-public-registry-before-publication'
        else:
            registry = registry_module.build_registry(data, source_bytes=raw_catalog)
            raw = registry_module.encode(registry)
            source_mode = 'local-catalog-before-publication'
    environment, releases, examples = run_registry(registry, args.python, args.timeout)
    report = {'schema_version':1, 'verified_on':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'registry_url':REGISTRY_URL, 'registry_sha256':sha(raw), 'registry_source_mode':source_mode, 'verification_tool':{'verifier_url':registry_module.ORIGIN + '/scripts/verify-atlas-execution-examples.py', 'verifier_sha256':sha(Path(__file__).read_bytes()), 'registry_builder_url':registry_module.ORIGIN + '/scripts/build-atlas-execution-examples.py', 'registry_builder_sha256':sha((HERE / 'build-atlas-execution-examples.py').read_bytes())}, 'environment':environment, 'scope':f'Only the {len(examples)} curated execution recipes were rerun from the public files. Atomic cases share one runner. This is separate from packaged pytest checks, independent PySCF reference regeneration, all 60 atlas problems, or a general solver certification.', 'releases':releases, 'examples':examples, 'unique_runner_executions':len(releases), 'passed':all(x['passed'] for x in examples)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(registry_module.encode(report))
    print(json.dumps({'examples':len(examples), 'unique_runner_executions':len(releases), 'passed':report['passed']}))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
