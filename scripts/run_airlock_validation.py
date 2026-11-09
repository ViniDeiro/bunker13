"""Physical airlock validation in isolated Round test slots; never a user campaign."""
from pathlib import Path
import argparse, os, subprocess, time, json, re, shutil
R = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--editor', action='store_true')
p.add_argument('--load', action='store_true')
p.add_argument('--lag', action='store_true')
p.add_argument('--headless', action='store_true')
a = p.parse_args()
exe = os.environ.get('C13_TEST_EXE', str(R/'builds/Mac/Condominio13-Airlock.app/Contents/MacOS/Condominio13'))
base = [exe] if not a.editor else ['/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor-Cmd', str(R/'unreal/Condominio13/Condominio13.uproject')]
os.environ['DEVELOPER_DIR'] = '/Applications/Xcode.app/Contents/Developer'
os.environ['TOOLCHAINS'] = 'com.apple.dt.toolchain.Metal.32023.883'
kind = ('editor_' if a.editor else 'package_') + ('load' if a.load else 'network')
started = time.time(); processes = []; files = []; logs = {}
roles = ['host'] if a.load else ['host', 'client']
try:
    for i, role in enumerate(roles):
        out = (R/f'logs/airlock_{kind}_{role}.log').open('w'); files.append(out)
        url = '/Game/Bunker/Lvl_CollectionRound?listen' if i == 0 else '127.0.0.1:7796'
        cmd = base + [url, '-game', '-C13Round', '-C13RoundTest', '-C13Expedition', '-C13AirlockTest', '-port=7796', '-windowed', '-ResX=960', '-ResY=540', '-ForceRes', '-stdout', '-FullStdOutLogOutput']
        cmd += ['-C13AirlockLoad'] if a.load else ['-C13RoundReset']
        if i: cmd += [f'-C13RoundProfile={i}']
        if a.headless: cmd += ['-nullrhi', '-nosound', '-unattended']
        if a.lag: cmd += ['-PktLag=80', '-PktLoss=2']
        processes.append(subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT))
        if i == 0 and not a.load: time.sleep(3)
    deadline = time.time() + 240
    while any(proc.poll() is None for proc in processes) and time.time() < deadline:
        if any(proc.poll() not in (None, 0) for proc in processes): break
        time.sleep(.5)
finally:
    for proc in processes:
        if proc.poll() is None:
            proc.terminate()
            try: proc.wait(timeout=8)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=5)
    for out in files: out.close()
for role in roles: logs[role] = (R/f'logs/airlock_{kind}_{role}.log').read_text(errors='replace')
host = logs['host']
checks = {'exit_clean': all(x.returncode == 0 for x in processes), 'checkpoint_valid': 'C13_SAVE_REJECT' not in host, 'inner_found': 'C13_AIRLOCK_MISSING_INNER' not in host}
if a.load:
    checks['resumed_doors_and_reset_cycle'] = 'C13_AIRLOCK_CHECK step=14 pass=1' in host
    checks['infrastructure_restored'] = 'C13_INFRA_RESTORED legacy=0' in host
else:
    for step in (10, 11, 12, 13, 15, 16): checks[f'physical_step_{step}'] = f'C13_AIRLOCK_CHECK step={step} pass=1' in host
    checks['initial_collection_and_closure'] = 'C13_ROUND_STARTED duration=35' in host and 'C13_ROUND_SHELTER' in host
    checks['powered_cycle'] = 'C13_AIRLOCK_CYCLE target=2 manual=0 seconds=5.0' in host
    checks['manual_cycles'] = all(f'C13_AIRLOCK_CYCLE target={target} manual=1 seconds=12.0' in host for target in (1, 2))
    checks['concurrent_cycle_rejected'] = 'C13_AIRLOCK_REJECT other_cycle' in host
    checks['other_leaf_blocked'] = 'C13_AIRLOCK_REJECT other_open' in host
    checks['outside_recovery'] = 'C13_ROUND_RECOVERY_OPEN' in host
    checks['remote_observed_open_outer_closed_inner'] = 'C13_AIRLOCK_CHECK step=10 pass=1' in host and 'C13_AIRLOCK_REPLICA outer=1 inner=0' in logs['client']
    checks['power_loss_fallback'] = 'C13_AIRLOCK_MANUAL_FALLBACK' in host
    checks['legacy_outside_closes_inner'] = 'C13_AIRLOCK_RECOVERY_CLOSE_REQUEST' in host
    checks['saved'] = 'C13_SAVE_COMMIT' in host
if a.lag: checks['packet_emulation'] = all('PktLag set to 80' in text and 'PktLoss set to 2' in text for text in logs.values())
fps = [dict(role=m[1], samples=int(m[2]), fps=float(m[3]), p95_ms=float(m[4])) for text in logs.values() for m in re.finditer(r'C13_AIRLOCK_FPS role=(\w+) samples=(\d+) fps=([\d.]+) p95_ms=([\d.]+)', text)]
snap = R/'unreal/Condominio13/Saved/Screenshots/MacEditor' if a.editor else Path.home()/'Library/Containers/com.YourCompany.Condominio13/Data/Library/Application Support/Epic/Condominio13/Saved/Screenshots/Mac'
for image in snap.glob('airlock_*.png'):
    if image.stat().st_mtime >= started: shutil.copy2(image, R/'screenshots'/image.name)
result = dict(passed=all(checks.values()), checks=checks, exit_codes=[x.returncode for x in processes], fps=fps, runtime='UnrealEditor -game' if a.editor else 'packaged Mac', rendered_instances=0 if a.headless else len(roles), limits=['Local automated game input, not human playtest or internet.', 'Initial collection and closure execute normally; later fixtures position characters and set power for isolated checks. Movement across leaves uses CharacterMovement.', 'This validates the airlock, not a complete resource expedition.'])
(R/f'logs/airlock_{kind}_result.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
raise SystemExit(0 if result['passed'] else 1)
