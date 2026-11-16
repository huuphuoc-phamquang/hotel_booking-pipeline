"""Fail CI nếu mutation score < --min. Đọc `mutmut junitxml` (mutmut 2.x): mỗi mutant là 1 testcase,
mutant sống sót là failure. Score = bị giết / tổng (timeout và suspicious tính là sống sót)."""
import argparse
import subprocess
import sys
import xml.etree.ElementTree as ET


def score(junit_xml: str) -> tuple[float, int]:
    suite = ET.fromstring(junit_xml)
    suite = suite if suite.tag == "testsuite" else suite.find("testsuite")
    total = int(suite.get("tests", 0))
    alive = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
    return (1.0 if total == 0 else (total - alive) / total), total


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=float, default=0.8)
    a = ap.parse_args()
    s, n = score(subprocess.run(["mutmut", "junitxml"], capture_output=True, text=True, check=True).stdout)
    print(f"mutation score {s:.1%} trên {n} mutant (ngưỡng {a.min:.0%})")
    sys.exit(0 if s >= a.min else 1)
