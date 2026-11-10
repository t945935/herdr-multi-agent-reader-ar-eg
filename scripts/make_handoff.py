#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent.parent
path = root / "examples/grades.py"
record = {
    "task_id": "grade-api-v1", "from": "developer", "to": "qa",
    "completed": "أُعدّ عقد الدرجات والتنفيذ المرجعي", "next": "شغّل اختبارات الانحدار للترتيب والتحقق من المدخلات",
    "artifacts": [{"path": "examples/grades.py", "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}],
}
out = root / "reports/handoff.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
print(out)
