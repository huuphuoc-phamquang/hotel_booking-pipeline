"""Tóm tắt event log Spark (spark.eventLog.dir) cho rubric edai-1 dòng 11-12: thời gian app, và theo từng stage
số task, thời gian task max / trung vị (straggler = max ≫ trung vị), shuffle read, spill ra đĩa.
Chạy: python event_log_stats.py <file event log> [...]   (lấy file: mc cp <minio>/lake/spark-events/<app id> .)"""
import json
import statistics
import sys


def summarize(path: str) -> dict:
    app, stages, tasks = {}, {}, {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            ev = e["Event"]
            if ev == "SparkListenerApplicationStart":
                app["name"], app["start"] = e["App Name"], e["Timestamp"]
            elif ev == "SparkListenerApplicationEnd":
                app["end"] = e["Timestamp"]
            elif ev == "SparkListenerStageCompleted":
                s = e["Stage Info"]
                stages[s["Stage ID"]] = {"name": s["Stage Name"].split(" at ")[0], "tasks": s["Number of Tasks"],
                                         "ms": s.get("Completion Time", 0) - s.get("Submission Time", 0)}
            elif ev == "SparkListenerTaskEnd" and e.get("Task End Reason", {}).get("Reason") == "Success":
                m, i = e.get("Task Metrics") or {}, e["Task Info"]
                rd = m.get("Shuffle Read Metrics", {})
                tasks.setdefault(e["Stage ID"], []).append((
                    i["Finish Time"] - i["Launch Time"],
                    rd.get("Remote Bytes Read", 0) + rd.get("Local Bytes Read", 0),
                    m.get("Disk Bytes Spilled", 0)))
    out = {"app": app.get("name"), "seconds": round((app.get("end", 0) - app.get("start", 0)) / 1000), "stages": []}
    for sid in sorted(stages):
        t = tasks.get(sid, [])
        if not t:
            continue
        d = [x[0] for x in t]
        out["stages"].append({**stages[sid], "id": sid, "max_s": round(max(d) / 1000, 1),
                              "median_s": round(statistics.median(d) / 1000, 1),
                              "shuffle_read_gb": round(sum(x[1] for x in t) / 2**30, 1),
                              "spill_gb": round(sum(x[2] for x in t) / 2**30, 1)})
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        s = summarize(p)
        print(f"== {s['app']}  {s['seconds']} s")
        for st in s["stages"]:
            print(f"  stage {st['id']:>3} {st['name'][:28]:<28} tasks={st['tasks']:>5} {st['ms'] / 1000:>7.0f}s "
                  f"max={st['max_s']:>7}s median={st['median_s']:>6}s shuffle_read={st['shuffle_read_gb']:>6}GB "
                  f"spill={st['spill_gb']}GB")
