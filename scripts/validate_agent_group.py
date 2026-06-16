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
    "archive",
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
STRICT_TASK_COLUMNS_WITH_DEPS = [
    "id",
    "title",
    "owner",
    "status",
    "risk",
    "depends_on",
    "inputs",
    "outputs",
    "notes",
]
STRICT_STATE_HEADINGS = [
    "# Current State",
    "## Active Goal",
    "## Current Phase",
    "## Active Task",
    "## Blockers",
    "## Latest Evidence",
    "## Next Step",
]
STRICT_OUTPUT_HEADINGS = [
    "## Task ID",
    "## Worker Name",
    "## Scope",
    "## Inputs Read",
    "## Commands Run",
    "## Conclusion",
    "## Artifacts",
    "## Risks or Blockers",
    "## Recommended Next Step",
]


def parse_depends(raw: str) -> list[str]:
    deps: list[str] = []
    for chunk in raw.replace(",", ";").split(";"):
        dep = chunk.strip()
        if dep:
            deps.append(dep)
    return deps


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
        if strict and reader.fieldnames not in (STRICT_TASK_COLUMNS, STRICT_TASK_COLUMNS_WITH_DEPS):
            errors.append(
                f"{path}: strict 模式要求列为 {','.join(STRICT_TASK_COLUMNS)} "
                f"或 {','.join(STRICT_TASK_COLUMNS_WITH_DEPS)}，实际为 {','.join(reader.fieldnames)}"
            )
        rows = list(reader)

        seen_ids: set[str] = set()
        task_ids: set[str] = set()
        for row_num, row in enumerate(rows, start=2):
            task_id = (row.get("id") or "").strip()
            if strict and not task_id:
                errors.append(f"{path}:{row_num}: 缺少 id")
            if task_id:
                if task_id in seen_ids:
                    errors.append(f"{path}:{row_num}: 重复 id: {task_id}")
                seen_ids.add(task_id)
                task_ids.add(task_id)
            status = (row.get("status") or "").strip()
            if status and status not in VALID_STATUSES:
                errors.append(f"{path}:{row_num}: 非法 status: {status}")
            if strict:
                risk = (row.get("risk") or "").strip()
                if risk and risk not in VALID_RISKS:
                    errors.append(f"{path}:{row_num}: 非法 risk: {risk}")
        if strict and "depends_on" in (reader.fieldnames or []):
            for row_num, row in enumerate(rows, start=2):
                task_id = (row.get("id") or "").strip()
                for dep in parse_depends(row.get("depends_on") or ""):
                    if dep == task_id:
                        errors.append(f"{path}:{row_num}: depends_on 不能引用自身: {dep}")
                    elif dep not in task_ids:
                        errors.append(f"{path}:{row_num}: depends_on 引用未知任务: {dep}")
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


def validate_agent_outputs(root: Path, *, strict: bool) -> list[str]:
    if not strict:
        return []
    output_dir = root / "current" / "agent_outputs"
    if not output_dir.exists():
        return []

    errors: list[str] = []
    for path in sorted(output_dir.iterdir()):
        if path.name == ".gitkeep":
            continue
        if path.is_dir():
            errors.append(f"{path}: worker 输出应为 Markdown 文件，不应是目录")
            continue
        if path.suffix != ".md":
            errors.append(f"{path}: worker 输出文件应使用 .md 后缀")
            continue

        stem = path.stem
        if "_" not in stem:
            errors.append(f"{path}: 文件名应为 <task_id>_<worker>.md")
        else:
            task_id, worker = stem.rsplit("_", 1)
            if not task_id or not worker:
                errors.append(f"{path}: 文件名应包含 task_id 和 worker")

        text = path.read_text(encoding="utf-8")
        for heading in STRICT_OUTPUT_HEADINGS:
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
    errors.extend(validate_agent_outputs(root, strict=args.strict))

    if errors:
        print("agent_group validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"agent_group validation passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
