"""Collect audit evidence from stdout; the sandboxed Mac app may not write workspace files."""
from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[1]
source=root/(sys.argv[1] if len(sys.argv)>1 else 'logs/door_capsule_packaged.log')
text=source.read_text(errors='replace')
reports=[line.split('C13_CAPSULE_REPORT ',1)[1] for line in text.splitlines() if 'C13_CAPSULE_REPORT ' in line]
if not reports:raise SystemExit('No runtime capsule report found')
report=json.loads(reports[-1])
report['source_log']=str(source.relative_to(root))
(root/'logs/door_capsule_packaged_result.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='entries'},indent=2))
raise SystemExit(0 if report['passed'] and report['pawn_guard_passed'] else 1)
