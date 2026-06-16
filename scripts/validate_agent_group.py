#!/usr/bin/env python3
"""校验 agent_group 实例结构。"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


REQUIRED_DIRS = [
    "rules",
    "memory",
    "current",
    "current/agent_outputs",
    "agents",
]

REQUIRED_FILES = [
    "rules/BOOTSTRAP.md",
    "rules/WORKER_REGISTRY.md",
    "rules/ROUTING_POLICY.md",
    "rules/MEMORY_SYNC_SOP.md",
    "memory/TASK_LEDGER.md",
    "memory/PROGRESS_LEDGER.md",
    "memory/DECISIONS.md",
    "memory/RISKS.md",
    "memory/PROJECT_FACTS.md",
    "current/STATE.md",
    "current/epic.md",
    "current/acceptance.md",
    "current/tasks.csv",
]

VALID_STATUSES = {"todo", "in_progress", "blocked", "review", "done", "dropped"}
VALID_RISKS = {"R0", "R1", "R2", "R3", "R4"}
STRICT_TASK_COLUMNS = ["id", "title", "owner", "status", "risk", "inputs", "outputs", "notes"]
STRICT_STATE_HEADINGS = [
    "# Current State",
    "## Active Goal",
    "## Current Phase",
    "## Active Task",
    "## Blockers",
    "## Latest Evidence",
    "## Next Step",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验 agent_group 实例")
    parser.add_argument("--strict", action="store_true", help="启用记忆文档形态严格校验")
    parser.add_argument("target", help="agent_group 目录")
    return parser.parse_args()


def validate_tasks_csv(path: Path, *, strict: bool) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return errors

    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            errors.append(f"{path}: 缺少 CSV header")
            return errors
        if "status" not in reader.fieldnames:
            errors.append(f"{path}: 缺少 status 列")
            return errors
        if strict and reader.fieldnames != STRICT_TASK_COLUMNS:
            errors.append(
                f"{path}: strict 模式要求列为 {','.join(STRICT_TASK_COLUMNS)}，实际为 {','.join(reader.fieldnames)}"
            )
        for row_num, row in enumerate(reader, start=2):
            status = (row.get("status") or "").strip()
            if status and status not in VALID_STATUSES:
                errors.append(f"{path}:{row_num}: 非法 status: {status}")
            if strict:
                risk = (row.get("risk") or "").strip()
                if risk and risk not in VALID_RISKS:
                    errors.append(f"{path}:{row_num}: 非法 risk: {risk}")
    return errors


def validate_state_md(path: Path, *, strict: bool) -> list[str]:
    if not strict or not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for heading in STRICT_STATE_HEADINGS:
        if heading not in text:
            errors.append(f"{path}: strict 模式缺少 heading: {heading}")
    return errors


def main() -> int:
    args = parse_args()
    root = Path(args.target).expanduser().resolve()
    errors: list[str] = []

    if not root.exists():
        errors.append(f"目标不存在: {root}")
    elif not root.is_dir():
        errors.append(f"目标不是目录: {root}")

    for item in REQUIRED_DIRS:
        path = root / item
        if not path.is_dir():
            errors.append(f"缺少目录: {item}")

    for item in REQUIRED_FILES:
        path = root / item
        if not path.is_file():
            errors.append(f"缺少文件: {item}")

    errors.extend(validate_tasks_csv(root / "current" / "tasks.csv", strict=args.strict))
    errors.extend(validate_state_md(root / "current" / "STATE.md", strict=args.strict))

    if errors:
        print("agent_group validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"agent_group validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
