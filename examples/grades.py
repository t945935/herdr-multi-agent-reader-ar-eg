"""عقد مشترك للفصول 2 و4 و5 و6؛ يستخدم ترتيب المنافسات المجاميع غير المقرّبة."""

from collections.abc import Mapping
from math import isfinite

SUBJECTS = frozenset({"اللغة العربية", "اللغة الإنجليزية", "الرياضيات"})


def validate_scores(scores):
    if not isinstance(scores, Mapping) or set(scores) != SUBJECTS:
        raise ValueError("يجب أن تتضمن الدرجات المواد الثلاث بالضبط: اللغة العربية واللغة الإنجليزية والرياضيات")
    for value in scores.values():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("يجب أن تكون الدرجات أرقامًا، ولا يجوز أن تكون من النوع bool")
        if not isfinite(value) or not 0 <= value <= 100:
            raise ValueError("يجب أن تكون الدرجات منتهية وضمن النطاق من 0 إلى 100")
    return scores


def calculate_total(scores):
    return sum(validate_scores(scores).values())


def calculate_average(scores):
    return calculate_total(scores) / 3


def get_grade(average):
    if isinstance(average, bool) or not isinstance(average, (int, float)):
        raise ValueError("يجب أن يكون المتوسط قيمة رقمية")
    if not isfinite(average) or not 0 <= average <= 100:
        raise ValueError("يجب أن يكون المتوسط ضمن النطاق من 0 إلى 100")
    return "ناجح" if average >= 60 else "راسب"


def rank_students(students):
    if not isinstance(students, list):
        raise ValueError("يجب أن تكون قائمة الطلاب قائمةً")
    rows = []
    for student in students:
        if not isinstance(student, Mapping):
            raise ValueError("يجب أن يكون كل طالب كائنًا")
        name = student.get("name")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("اسم الطالب مطلوب")
        total = calculate_total(student.get("scores"))
        average = total / 3
        rows.append({"name": name.strip(), "scores": dict(student["scores"]),
                     "total": total, "average": average, "grade": get_grade(average)})
    rows.sort(key=lambda row: row["total"], reverse=True)
    previous = None
    rank = 0
    for index, row in enumerate(rows, 1):
        if previous is None or row["total"] != previous:
            rank = index
        previous = row["total"]
        row["rank"] = rank
    return rows
