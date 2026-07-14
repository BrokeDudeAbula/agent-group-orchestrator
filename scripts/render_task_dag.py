#!/usr/bin/env python3
"""从 tasks.csv 生成 Mermaid 任务 DAG。"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def node_id(task_id: str) -> str:
    return task_id.replace("-", "_").replace(".", "_")


def escape_label(text: str) -> str:
    return text.replace('"', "'")


def parse_depends(raw: str) -> list[str]:
    deps: list[str] = []
    for chunk in raw.replace(",", ";").split(";"):
        dep = chunk.strip()
        if dep:
            deps.append(dep)
    return deps


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
        label = escape_label(f"{task_id}<br/>{title}<br/>{status}")
        print(f'  {node_id(task_id)}["{label}"]')

    for row in rows:
        task_id = (row.get("id") or row.get("task_id") or "").strip()
        if not task_id:
            continue
        for dep in parse_depends(row.get("depends_on") or ""):
            print(f"  {node_id(dep)} --> {node_id(task_id)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
