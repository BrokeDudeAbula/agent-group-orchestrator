#!/usr/bin/env python3
"""初始化项目本地 agent_group 实例。"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PLUGIN_ROOT / "assets" / "templates" / "instance"
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from agent_group_paths import (  # noqa: E402
    KNOWN_BACKENDS,
    default_instance_relpath,
    detect_backend,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="初始化项目本地 agent_group 实例（支持 .claude/agent_group 与 .codex/agent_group）"
    )
    parser.add_argument(
        "--target",
        help="目标 agent_group 目录；省略时按 --backend 选择默认路径",
    )
    parser.add_argument(
        "--backend",
        default="auto",
        choices=list(KNOWN_BACKENDS),
        help="执行后端：auto / codex / claude-code；影响默认路径与 config.yml",
    )
    parser.add_argument("--project-name", default="example", help="项目名称")
    parser.add_argument("--force", action="store_true", help="允许覆盖已有目录")
    parser.add_argument(
        "--root",
        default=".",
        help="解析默认路径时使用的项目根目录，默认当前目录",
    )
    return parser.parse_args()


def write_config(target: Path, *, project_name: str, backend: str) -> None:
    config = target / "config.yml"
    config.write_text(
        "\n".join(
            [
                f"project_name: {project_name}",
                "default_mode: auto-orchestrate",
                f"execution_backend: {backend}",
                "task_id_prefix: AUTO",
                "worker_output_dir: current/agent_outputs",
                "archive_dir: archive",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    backend = detect_backend(args.backend)
    root = Path(args.root).expanduser().resolve()

    # 初始化时：显式 target 优先；否则始终按 backend 默认路径创建，
    # 不要复用另一个后端已有的实例目录。
    if args.target:
        target = Path(args.target).expanduser()
        if not target.is_absolute():
            target = root / target
        target = target.resolve()
    else:
        target = (root / default_instance_relpath(backend)).resolve()

    if target.exists() and any(target.iterdir()) and not args.force:
        raise SystemExit(f"目标目录已存在且非空，拒绝覆盖: {target}")

    if target.exists() and args.force:
        shutil.rmtree(target)

    shutil.copytree(TEMPLATE_ROOT, target)
    domain_agents = target / "agents-domain"
    if domain_agents.exists():
        shutil.rmtree(domain_agents)
    (target / "archive").mkdir(exist_ok=True)
    (target / "current" / "agent_outputs").mkdir(parents=True, exist_ok=True)
    write_config(target, project_name=args.project_name, backend=backend)

    print(f"initialized agent group: {target}")
    print(f"execution backend: {backend}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
