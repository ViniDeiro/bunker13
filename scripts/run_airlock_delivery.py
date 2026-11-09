"""Reproducible airlock checks, with version-specific evidence and isolated campaign slots."""
from pathlib import Path
import subprocess, os, json, shutil, hashlib, argparse
R = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(); p.add_argument('--resume', action='store_true'); a = p.parse_args()
app = R/'builds/Mac/Condominio13-Airlock.app'
exe = app/'Contents/MacOS/Condominio13'
digest = hashlib.sha256(exe.read_bytes()).hexdigest()
out = R/'logs/airlock_delivery_manifest.json'
prior = json.loads(out.read_text()) if out.exists() else {}
rows = prior.get('steps', {}) if a.resume and prior.get('executable_sha256') == digest else {}
archive = R/'logs/airlock_prior'; archive.mkdir(exist_ok=True)
for pattern in ('round_seed_*', 'round_load_*', 'round_walk_*', 'round_network_*', 'reconnect_*.log', 'reconnect_result.json'):
    for source in (R/'logs').glob(pattern):
        target = archive/source.name
        if source.is_file() and not target.exists(): shutil.copy2(source, target)
reconnect = R/'scripts/run_reconnect_test.py'
wrapper = "from pathlib import Path\np=Path(" + repr(str(reconnect)) + ")\nexec(compile(p.read_text().replace('builds/Mac/Condominio13-VerticalSlice.app','builds/Mac/Condominio13-Airlock.app'),str(p),'exec'),{'__file__':str(p),'__name__':'__main__'})"
cases = [
    ('network', ['python3', 'scripts/run_airlock_validation.py', '--lag'], 'airlock_package_network_result.json', {}),
    ('resume', ['python3', 'scripts/run_airlock_validation.py', '--load'], 'airlock_package_load_result.json', {}),
    ('legacy_seed', ['python3', 'scripts/run_round_validation.py', 'seed'], 'round_seed_result.json', {'C13_TEST_EXE': str(R/'builds/Mac/Condominio13-Infrastructure.app/Contents/MacOS/Condominio13')}),
    ('legacy_load', ['python3', 'scripts/run_round_validation.py', 'load'], 'round_load_result.json', {'C13_TEST_EXE': str(exe), 'C13_TEST_EXTRA': '-C13Expedition'}),
    ('walk', ['python3', 'scripts/run_round_validation.py', 'walk'], 'round_walk_result.json', {'C13_TEST_EXE': str(exe), 'C13_TEST_EXTRA': '-C13Expedition'}),
    ('legacy_round', ['python3', 'scripts/run_round_validation.py', 'network'], 'round_network_result.json', {'C13_TEST_EXE': str(exe)}),
    ('reconnect', ['python3', '-c', wrapper], 'reconnect_result.json', {}),
]
for name, command, result_name, extra in cases:
    if rows.get(name, {}).get('passed'): print(f'{name}: existing pass for identical executable', flush=True); continue
    env = dict(os.environ); env.pop('C13_TEST_EXTRA', None); env.update(extra)
    with (R/f'logs/airlock_delivery_{name}.log').open('w') as log:
        run = subprocess.run(command, cwd=R, env=env, stdout=log, stderr=subprocess.STDOUT)
    result_path = R/'logs'/result_name
    result = json.loads(result_path.read_text()) if result_path.exists() else {}
    shutil.copy2(result_path, R/f'logs/airlock_verified_{name}.json') if result_path.exists() else None
    rows[name] = dict(passed=run.returncode == 0 and result.get('passed', False), exit_code=run.returncode, result=f'logs/airlock_verified_{name}.json')
    manifest = dict(version='0.4.1', scope='Airlock only: first expedition remains incomplete', executable_sha256=digest, passed=len(rows) == len(cases) and all(row['passed'] for row in rows.values()), steps=rows)
    out.write_text(json.dumps(manifest, indent=2)); print(name, rows[name], flush=True)
    if not rows[name]['passed']: raise SystemExit(1)
