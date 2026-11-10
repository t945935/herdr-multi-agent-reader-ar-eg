"""الفصل السادس: تحقّق من سجل تسليم صريح، لا من ادعاء وكيل في نص وصفي."""

import argparse
import hashlib
import json
from pathlib import Path


def validate(record, root):
    required = {"task_id", "from", "to", "completed", "next", "artifacts"}
    if not isinstance(record, dict) or not required <= record.keys():
        raise ValueError("حقول سجل التسليم ناقصة")
    if any(not isinstance(record[key], str) or not record[key].strip()
           for key in ["task_id", "from", "to", "completed", "next"]):
        raise ValueError("يجب ألا تكون حقول النص في سجل التسليم فارغة")
    if not isinstance(record["artifacts"], list) or not record["artifacts"]:
        raise ValueError("يجب أن يتضمن سجل التسليم ملفات ناتجة")
    root = Path(root).resolve()
    for artifact in record["artifacts"]:
        if not isinstance(artifact, dict) or set(artifact) != {"path", "sha256"}:
            raise ValueError("يتطلب الملف الناتج مسارًا وقيمة sha256")
        path = (root / artifact["path"]).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("يجب أن يشير مسار الملف الناتج إلى ملف داخل المشروع")
        if hashlib.sha256(path.read_bytes()).hexdigest() != artifact["sha256"]:
            raise ValueError("قيمة تجزئة الملف الناتج غير مطابقة")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    validate(json.loads(args.record.read_text()), args.root)
    print("تم قبول سجل التسليم")
