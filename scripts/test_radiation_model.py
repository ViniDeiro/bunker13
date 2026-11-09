"""Compile the production policy with sanitizers; does not launch or certify Unreal."""
from pathlib import Path
import json
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "logs").mkdir(exist_ok=True)
with tempfile.TemporaryDirectory(prefix="c13-radiation-") as tmp:
    binary = str(Path(tmp) / "radiation-test")
    cmd = [os.environ.get("CXX", "clang++"), "-std=c++17", "-Wall", "-Wextra", "-Werror",
           "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g",
           "-I", str(ROOT / "unreal/Condominio13/Source/Condominio13"),
           str(ROOT / "tests/radiation_model_test.cpp"), "-o", binary]
    build = subprocess.run(cmd, capture_output=True, text=True)
    run = subprocess.run([binary], capture_output=True, text=True) if build.returncode == 0 else None
    result = dict(passed=bool(run and run.returncode == 0), scope="engine-independent production policy only",
                  unreal_integration=False, build_exit=build.returncode,
                  output=build.stdout + build.stderr + (run.stdout + run.stderr if run else ""))
    (ROOT / "logs/radiation_model_result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["passed"] else 1)
