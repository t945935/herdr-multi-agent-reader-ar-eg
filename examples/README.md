# حزمة التطبيقات العملية للقراء

شغّل جميع الأوامر من جذر المشروع بعد فك ضغط الحزمة؛ واستورد الوحدات باستخدام `examples.*`.

موجّها العمل في تمرين الدرجات هما `examples/prompts/grades-developer.md` و`examples/prompts/grades-qa.md`؛ أما `examples/prompts/qa.md` فيخصّ الموقع. أسند المهام في نسخة تدريبية خاصة بك للحفاظ على النسخة المرجعية.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q tests
.venv/bin/python -m examples.pipeline
```

| الفصل | نقطة البدء | محور القبول |
| --- | --- | --- |
| 1 | `examples/calculator.py` | العمليات الأربع، والقسمة على صفر، وأنواع البيانات |
| 2 | `examples/grades.py` | حدود الدرجات، والمواد الناقصة، وترتيب التعادل التنافسي |
| 3 | `scripts/probe_herdr.py --live` | تشغيل أمر في جزء صدفة جديد وقراءته وانتظاره وتنظيفه |
| 4 | `scripts/team.py` | الإسناد المرحلي، ومعرّفات المهام الفريدة، وقبول الملفات الناتجة |
| 5 | `examples/prompts/reviewer-a.md` و`examples/prompts/reviewer-b.md` | مراجعتان مستقلتان وقرار المدير |
| 6 | `examples/handoff.py` | وجود الملف، ونطاق المشروع، وSHA-256 |
| 7 | `examples/task_manager/` | الإنشاء والقراءة والتحديث والحذف، والتحقق، والصفحات الثابتة، والاستمرار بعد إعادة التشغيل |
| 8 | `examples/research.py` | الادعاءات والمصادر والاقتباسات وحالات عدم اليقين |
| 9 | `examples/pipeline.py` | رموز الخروج، والمهل الزمنية، وقبول المخرجات، والتوقف عند الفشل |
| 10 | `examples/queue.py` | إزالة التكرار، ومهل الامتلاك، والاستعادة، والرسائل المتعذّرة، والتزامن |

## تشغيل الموقع

```bash
.venv/bin/python -m uvicorn examples.task_manager.main:app --host 0.0.0.0 --port 8000
```

في WSL، افتح `http://localhost:8000/` في متصفح Windows. تُحفظ بيانات العرض الافتراضية في `examples/data/tasks.db`؛ أما الاختبارات الآلية فتستخدم مجلدًا مؤقتًا ولا تمس هذا الملف.

مثال طابور العمل الخلفي محدود التنفيذ ويعالج بيانات حسابية بحتة؛ فلا يستدعي نموذجًا مدفوعًا. أما الإسناد الفعلي إلى النماذج فينفّذه `scripts/team.py` صراحةً؛ ثبّت واجهة CLI المطلوبة وسجّل الدخول إليها أولًا.
