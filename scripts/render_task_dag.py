#!/usr/bin/env python3
"""从 tasks.csv 生成简单 Mermaid DAG。"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="渲染 tasks.csv 为 Mermaid")
    parser.add_argument("tasks_csv", help="tasks.csv 路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path = Path(args.tasks_csv)
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    print("flowchart TD")
    for row in rows:
        task_id = (row.get("id") or row.get("task_id") or "").strip()
        title = (row.get("title") or row.get("task") or task_id).strip()
        status = (row.get("status") or "").strip()
        if not task_id:
            continue
        label = f"{task_id}<br/>{title}<br/>{status}"
        print(f'  {task_id.replace("-", "_")}["{label}"]')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

