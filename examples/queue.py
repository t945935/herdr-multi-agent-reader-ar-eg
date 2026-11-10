"""الفصل العاشر: مهلات امتلاك SQLite وإعادات محاولة محدودة وإنهاء محمي بالملكية.

التنفيذ مرة واحدة على الأقل، لا ضمان للآثار الجانبية الخارجية مرة واحدة بالضبط.
المعالج التوضيحي بحت؛ وعلى المستدعين توفير قابلية التكرار الآمن لكتاباتهم الخارجية.
"""

import argparse
import json
import sqlite3
import time
import uuid
from contextlib import closing
from pathlib import Path


class Queue:
    def __init__(self, path):
        self.path = str(path)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as conn, conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS jobs (
              id TEXT PRIMARY KEY, payload TEXT NOT NULL,
              state TEXT NOT NULL DEFAULT 'pending', attempts INTEGER NOT NULL DEFAULT 0,
              max_attempts INTEGER NOT NULL, owner TEXT, lease_until REAL,
              result TEXT, error TEXT)""")

    def connect(self):
        conn = sqlite3.connect(self.path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def enqueue(self, job_id, payload, max_attempts=3):
        if not job_id or not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts < 1:
            raise ValueError("تتطلب المهمة معرّفًا وحدًا موجبًا لعدد المحاولات")
        encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        with closing(self.connect()) as conn, conn:
            conn.execute("BEGIN IMMEDIATE")
            existing = conn.execute("SELECT payload FROM jobs WHERE id=?", (job_id,)).fetchone()
            if existing and existing[0] != encoded:
                raise ValueError("لا يجوز لمفتاح قابلية التكرار الآمن أن يعرّف حمولة مختلفة")
            conn.execute("INSERT OR IGNORE INTO jobs(id,payload,max_attempts) VALUES(?,?,?)",
                         (job_id, encoded, max_attempts))

    def claim(self, lease_seconds=30, now=None):
        if lease_seconds <= 0:
            raise ValueError("يجب أن تكون مهلة الامتلاك موجبة")
        now = time.time() if now is None else now
        owner = uuid.uuid4().hex
        with closing(self.connect()) as conn, conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("""UPDATE jobs SET state='dead', owner=NULL, error='انتهت محاولات مهلة الامتلاك'
              WHERE state='running' AND lease_until<=? AND attempts>=max_attempts""", (now,))
            row = conn.execute("""SELECT * FROM jobs WHERE
              (state='pending' OR (state='running' AND lease_until<=?))
              AND attempts<max_attempts ORDER BY rowid LIMIT 1""", (now,)).fetchone()
            if not row:
                return None
            conn.execute("""UPDATE jobs SET state='running', owner=?, lease_until=?,
              attempts=attempts+1 WHERE id=?""", (owner, now + lease_seconds, row["id"]))
            return {"id": row["id"], "payload": json.loads(row["payload"]), "owner": owner}

    def heartbeat(self, job, lease_seconds=30, now=None):
        now = time.time() if now is None else now
        if lease_seconds <= 0:
            raise ValueError("يجب أن تكون مهلة الامتلاك موجبة")
        with closing(self.connect()) as conn, conn:
            cursor = conn.execute("""UPDATE jobs SET lease_until=? WHERE id=? AND owner=?
              AND state='running' AND lease_until>?""", (now + lease_seconds, job["id"], job["owner"], now))
            return cursor.rowcount == 1

    def finish(self, job, result=None, error=None, now=None):
        now = time.time() if now is None else now
        with closing(self.connect()) as conn, conn:
            if error is None:
                cursor = conn.execute("""UPDATE jobs SET state='done',result=?,owner=NULL,lease_until=NULL
                  WHERE id=? AND owner=? AND state='running' AND lease_until>?""",
                  (json.dumps(result, ensure_ascii=False), job["id"], job["owner"], now))
            else:
                cursor = conn.execute("""UPDATE jobs SET state=CASE WHEN attempts>=max_attempts
                  THEN 'dead' ELSE 'pending' END,error=?,owner=NULL,lease_until=NULL
                  WHERE id=? AND owner=? AND state='running' AND lease_until>?""",
                  (str(error), job["id"], job["owner"], now))
            return cursor.rowcount == 1

    def jobs(self):
        with closing(self.connect()) as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM jobs ORDER BY rowid")]


def work_once(queue):
    job = queue.claim()
    if job is None:
        return False
    try:
        # يحافظ المعالج البحت والمحدود على قابلية إعادة المثال دون مفتاح API.
        result = {"sum": sum(job["payload"]["numbers"])}
        if not queue.finish(job, result=result):
            raise RuntimeError("فُقدت ملكية مهلة الامتلاك قبل الإكمال")
    except (KeyError, TypeError, ValueError) as exc:
        queue.finish(job, error=str(exc))
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["enqueue", "once", "serve", "status"])
    parser.add_argument("--db", type=Path, default=Path("reports/jobs.db"))
    parser.add_argument("--id", default="sum-demo")
    parser.add_argument("--max-jobs", type=int, default=20)
    args = parser.parse_args()
    queue = Queue(args.db)
    if args.action == "enqueue":
        queue.enqueue(args.id, {"numbers": [10, 20, 30]})
    elif args.action == "once":
        work_once(queue)
    elif args.action == "serve":
        try:
            for _ in range(args.max_jobs):
                if not work_once(queue):
                    break
        except KeyboardInterrupt:
            pass
    print(json.dumps(queue.jobs(), ensure_ascii=False, indent=2))
