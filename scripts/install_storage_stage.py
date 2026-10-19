"""Install the blue bottle, presentation variants and usable storage in order."""
from pathlib import Path
import runpy
ROOT=Path(__file__).resolve().parents[1]
for script in ('install_item_kit.py','install_first_person_hands.py','install_storage.py'):
    runpy.run_path(str(ROOT/'scripts'/script))
