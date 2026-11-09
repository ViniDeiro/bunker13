"""Portable Mac build/editor entry point. Does not download Unreal or modify saves."""
from pathlib import Path
import argparse
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("action", choices=["build-editor", "edit-expedition"])
parser.add_argument("--engine", required=True, type=Path, help="Unreal installation root containing Engine/")
parser.add_argument("--jobs", type=int, default=3)
args = parser.parse_args()
project = ROOT / "unreal/Condominio13/Condominio13.uproject"
engine = args.engine.expanduser().resolve() / "Engine"
if not project.is_file() or not engine.is_dir():
    parser.error("Project or Engine directory missing. Supply the Unreal installation root.")
if not 1 <= args.jobs <= 16:
    parser.error("--jobs must be between 1 and 16")
if args.action == "build-editor":
    command = [str(engine / "Build/BatchFiles/Mac/Build.sh"), "Condominio13Editor", "Mac", "Development",
               f"-Project={project}", "-WaitMutex", f"-MaxParallelActions={args.jobs}"]
else:
    command = [str(engine / "Binaries/Mac/UnrealEditor"), str(project), "/Game/Bunker/Lvl_CollectionRound",
               "-C13Round", "-C13Expedition"]
if not Path(command[0]).is_file():
    parser.error("Required Unreal executable not found. This entry point supports macOS only.")
raise SystemExit(subprocess.call(command, cwd=ROOT, env=dict(os.environ)))
