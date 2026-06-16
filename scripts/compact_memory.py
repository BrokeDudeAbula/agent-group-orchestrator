#!/usr/bin/env python3
"""归档 agent_group 的 current 工作记忆。"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


CURRENT_FILES = ["STATE.md", "epic.md", "acceptance.md", "tasks.csv", "tasks.meta.yml"]
TASK_COLUMNS = ["id", "title", "owner", "status", "risk", "depends_on", "inputs", "outputs", "notes"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="归档 current 状态和 worker 输出")
    parser.add_argument("--target", required=True, help="agent_group 目录")
    parser.add_argument("--archive-name", required=True, help="archive 子目录名")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不移动文件")
    parser.add_argument(
        "--no-reset-current",
        action="store_true",
        help="归档后不重建 current 热状态文件；默认会重建以保持实例可校验",
    )
    return parser.parse_args()


def plan_moves(root: Path, archive: Path) -> list[tuple[Path, Path]]:
    moves: list[tuple[Path, Path]] = []
    current = root / "current"
    for name in CURRENT_FILES:
        src = current / name
        if src.exists():
            moves.append((src, archive / name))

    outputs = current / "agent_outputs"
    if outputs.exists():
        for src in sorted(outputs.iterdir()):
            if src.name == ".gitkeep":
                continue
            moves.append((src, archive / "agent_outputs" / src.name))
    return moves


def reset_current(root: Path, archive_name: str) -> None:
    current = root / "current"
    current.mkdir(parents=True, exist_ok=True)
    outputs = current / "agent_outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    (outputs / ".gitkeep").touch(exist_ok=True)

    (current / "STATE.md").write_text(
        "\n".join(
            [
                "---",
                "ag_schema: v1",
                "doc_type: current_state",
                "authority: canonical",
                "lifecycle: hot",
                "---",
                "",
                "# Current State",
                "",
                "## Active Goal",
                "",
                "Unset.",
                "",
                "## Current Phase",
                "",
                f"Previous phase archived to `archive/{archive_name}/`; no active phase has been started.",
                "",
                "## Active Task",
                "",
                "None.",
                "",
                "## Blockers",
                "",
                "None.",
                "",
                "## Latest Evidence",
                "",
                f"- `archive/{archive_name}/`",
                "",
                "## Next Step",
                "",
                "Define the next goal, acceptance criteria, and active task list.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (current / "epic.md").write_text("# Current Epic\n\nUnset.\n", encoding="utf-8")
    (current / "acceptance.md").write_text("# Acceptance Criteria\n\nUnset.\n", encoding="utf-8")
    (current / "tasks.csv").write_text(",".join(TASK_COLUMNS) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.target).expanduser().resolve()
    archive = root / "archive" / args.archive_name
    moves = plan_moves(root, archive)

    if not moves:
        print("没有可归档文件")
        return 0

    print(f"archive target: {archive}")
    for src, dst in moves:
        print(f"{src} -> {dst}")

    if args.dry_run:
        print("dry-run: 未执行移动")
        if not args.no_reset_current:
            print("dry-run: 归档成功后将重建 current/STATE.md、current/epic.md、current/acceptance.md 和 current/tasks.csv")
        return 0

    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

    if not args.no_reset_current:
        reset_current(root, args.archive_name)
        print("current reset complete")
    else:
        (root / "current" / "agent_outputs").mkdir(parents=True, exist_ok=True)
        keep = root / "current" / "agent_outputs" / ".gitkeep"
        keep.touch(exist_ok=True)
    print("archive complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
