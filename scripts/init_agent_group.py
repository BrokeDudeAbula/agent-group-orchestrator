#!/usr/bin/env python3
"""初始化项目本地 agent_group 实例。"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PLUGIN_ROOT / "assets" / "templates" / "instance"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="初始化 .codex/agent_group 实例")
    parser.add_argument("--target", required=True, help="目标 agent_group 目录")
    parser.add_argument("--project-name", default="example", help="项目名称")
    parser.add_argument("--force", action="store_true", help="允许覆盖已有目录")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = Path(args.target).expanduser().resolve()

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

    config = target / "config.yml"
    if not config.exists():
        config.write_text(
            "\n".join(
                [
                    f"project_name: {args.project_name}",
                    "default_mode: auto-orchestrate",
                    "task_id_prefix: AUTO",
                    "worker_output_dir: current/agent_outputs",
                    "archive_dir: archive",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    print(f"initialized agent group: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
