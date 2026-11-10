#!/usr/bin/env python3
"""أسند العمل إلى وكيل خامل بدأ تشغيله مسبقًا، وتحقق من سجل تنفيذ خاص بالمهمة."""
import argparse
import json
import os
import subprocess
import uuid
from pathlib import Path


def call(*args, timeout=310):
    done = subprocess.run(["herdr", *args], text=True, capture_output=True, timeout=timeout)
    if done.returncode:
        raise RuntimeError(done.stderr or done.stdout)
    return json.loads(done.stdout)["result"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("prompt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if os.environ.get("HERDR_ENV") != "1":
        raise SystemExit("شغّل الأداة داخل Herdr")
    agent = call("agent", "get", args.target)["agent"]
    if agent["agent_status"] not in {"idle", "done"}:
        raise SystemExit("يجب أن تكون حالة الوكيل idle أو done قبل بدء هذه المهمة")
    path = args.output.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit("اختر مسار سجل تنفيذ جديدًا؛ ولا تعِد استخدام مسار مهمة سابقة")
    task_id = uuid.uuid4().hex
    prompt = args.prompt.read_text() + (
        f"\n\ntask_id لهذه المهمة={task_id}\ncompletion_path={path}\n"
        'أنجز العمل الفعلي ثم اكتب JSON: {"task_id":"المعرّف أعلاه","status":"completed",'
        '"summary":"المخرجات والتحقق المحددان","artifacts":["مسارات الملفات الناتجة الفعلية"]}. '
        "إذا تعذّر إكمال المهمة، فاستخدم status=blocked واشرح السبب في summary. لا تبدأ وكلاء آخرين."
    )
    settled = call("agent", "prompt", args.target, prompt, "--wait", "--timeout", "300000")
    state = settled["agent"]["agent_status"]
    if state not in {"idle", "done"} or not path.is_file():
        raise SystemExit("استقر الوكيل دون سجل تنفيذ مقبول؛ افحص agent get/read")
    receipt = json.loads(path.read_text())
    if receipt.get("task_id") != task_id or receipt.get("status") != "completed" or not receipt.get("summary"):
        raise SystemExit("سجل التنفيذ لا يثبت قبول هذه المهمة")
    for artifact in receipt.get("artifacts", []):
        candidate = Path(artifact)
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        if not candidate.is_file():
            raise SystemExit(f"الملف الناتج غير موجود: {artifact}")
    print(json.dumps(receipt, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
