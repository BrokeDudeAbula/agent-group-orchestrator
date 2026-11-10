#!/usr/bin/env python3
"""把技能包运行时文件安装到宿主 skills 目录。

只复制 SKILL.md、workflows/、scripts/、references/ 和 assets/。
examples/、tests/、ROADMAP.html 以及仓库说明文件留在原仓库。
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_group_paths import skill_root  # noqa: E402


RUNTIME_ENTRIES = ("SKILL.md", "workflows", "scripts", "references", "assets")
LEFT_BEHIND = (
    "examples",
    "tests",
    "ROADMAP.html",
    "README.md",
    "AGENTS.md",
    "LICENSE",
    ".github",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="安装 agent-group 技能运行时文件，不复制示例、测试和路线图"
    )
    parser.add_argument(
        "--dest",
        required=True,
        help="宿主 skills 目录，或已经以 agent-group 结尾的目标目录",
    )
    parser.add_argument("--force", action="store_true", help="覆盖已有目标目录")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不复制")
    return parser.parse_args()


def resolve_destination(dest: Path) -> Path:
    dest = dest.expanduser().resolve()
    if dest.name != "agent-group":
        dest = dest / "agent-group"
    return dest


def left_behind(root: Path) -> list[str]:
    return [name for name in LEFT_BEHIND if (root / name).exists()]


def install_tree(root: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for name in RUNTIME_ENTRIES:
        src = root / name
        target = dest / name
        if not src.exists():
            raise SystemExit(f"技能包缺少运行时路径: {name}")
        if src.is_dir():
            shutil.copytree(
                src,
                target,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        else:
            shutil.copy2(src, target)


def assert_slim(dest: Path) -> None:
    for name in LEFT_BEHIND:
        if (dest / name).exists():
            raise SystemExit(f"安装结果不应包含: {name}")
    for name in RUNTIME_ENTRIES:
        if not (dest / name).exists():
            raise SystemExit(f"安装结果缺少: {name}")


def main() -> int:
    args = parse_args()
    root = skill_root()
    dest = resolve_destination(Path(args.dest))
    if dest == root or root in dest.parents:
        raise SystemExit(f"拒绝把技能安装到技能包仓库内部: {dest}")

    print(f"source: {root}")
    print(f"dest: {dest}")
    print("copy: " + ", ".join(RUNTIME_ENTRIES))
    skipped = left_behind(root)
    if skipped:
        print("leave behind: " + ", ".join(skipped))

    if dest.exists() and any(dest.iterdir()) and not args.force and not args.dry_run:
        raise SystemExit(f"目标目录已存在且非空，拒绝覆盖: {dest}。可加 --force")

    if args.dry_run:
        print("dry-run: 未复制文件")
        return 0

    dest.parent.mkdir(parents=True, exist_ok=True)
    install_tree(root, dest)
    assert_slim(dest)
    print(f"installed skill: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
