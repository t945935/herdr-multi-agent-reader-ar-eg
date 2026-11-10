"""الفصل الثامن: تحقّق من أدلة الادعاءات ومصادرها وأنشئ تقريرًا قابلًا للتدقيق."""

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


def validate(data):
    if not isinstance(data, dict) or not data.get("question"):
        raise ValueError("سؤال البحث مطلوب")
    sources = data.get("sources", [])
    if not isinstance(sources, list) or not sources:
        raise ValueError("المصادر مطلوبة")
    by_id = {}
    for source in sources:
        if not {"id", "url", "title", "accessed", "kind"} <= source.keys():
            raise ValueError("بيانات المصدر غير مكتملة")
        parsed = urlparse(source["url"])
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("يجب أن يستخدم رابط المصدر HTTP أو HTTPS")
        if source["id"] in by_id:
            raise ValueError("معرّف المصدر مكرر")
        by_id[source["id"]] = source
    claims = data.get("claims", [])
    if not claims:
        raise ValueError("الادعاءات مطلوبة")
    for claim in claims:
        if not claim.get("text") or claim.get("status") not in {"supported", "uncertain", "conflict"}:
            raise ValueError("الادعاء غير صالح")
        evidence = claim.get("evidence", [])
        if claim["status"] == "supported" and not evidence:
            raise ValueError("تتطلب الادعاءات المدعومة أدلة")
        for item in evidence:
            if item.get("source") not in by_id or not item.get("quote"):
                raise ValueError("يتطلب الدليل مصدرًا معروفًا واقتباسًا")
    return by_id


def render(data):
    sources = validate(data)
    lines = ["# " + data["question"], "", "## الاستنتاجات والأدلة", ""]
    for claim in data["claims"]:
        lines.extend([f"### {claim['text']}", "", "الحالة: " + claim["status"], ""])
        for evidence in claim.get("evidence", []):
            source = sources[evidence["source"]]
            lines.extend([f"> {evidence['quote']}", "", f"المصدر: [{source['title']}]({source['url']})", ""])
    lines.extend(["## قائمة المصادر", ""])
    for source in sources.values():
        lines.append(f"- {source['id']}: [{source['title']}]({source['url']}); {source['kind']}; تاريخ الاطلاع {source['accessed']}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = render(json.loads(args.input.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
    print(args.output)
