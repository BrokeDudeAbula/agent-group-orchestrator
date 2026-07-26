#!/usr/bin/env python3
"""后端中立的 agent_group 实例路径解析。"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


CLAUDE_INSTANCE = Path(".claude") / "agent_group"
CODEX_INSTANCE = Path(".codex") / "agent_group"
KNOWN_BACKENDS = ("auto", "codex", "claude-code")


def detect_backend(requested: str = "auto") -> str:
    """解析执行后端。

    优先级：
    1. 显式 requested（非 auto）
    2. 环境变量 AGENT_GROUP_BACKEND
    3. Claude Code 常见环境信号
    4. 默认 codex（保持历史兼容）
    """
    if requested and requested != "auto":
        backend = requested.strip().lower()
        if backend in {"claude", "claude-code-cli", "claudecode"}:
            return "claude-code"
        if backend not in {"codex", "claude-code"}:
            raise ValueError(f"未知 backend: {requested}")
        return backend

    env_backend = (os.environ.get("AGENT_GROUP_BACKEND") or "").strip().lower()
    if env_backend and env_backend != "auto":
        return detect_backend(env_backend)

    claude_signals = (
        os.environ.get("CLAUDECODE"),
        os.environ.get("CLAUDE_CODE_ENTRYPOINT"),
        os.environ.get("CLAUDE_CODE_SESSION"),
        os.environ.get("CLAUDE_PLUGIN_ROOT"),
    )
    if any(claude_signals):
        return "claude-code"

    return "codex"


def default_instance_relpath(backend: str = "auto") -> Path:
    resolved = detect_backend(backend)
    if resolved == "claude-code":
        return CLAUDE_INSTANCE
    return CODEX_INSTANCE


def existing_instances(root: Path) -> list[Path]:
    found: list[Path] = []
    for rel in (CLAUDE_INSTANCE, CODEX_INSTANCE):
        path = (root / rel).resolve()
        if path.is_dir():
            found.append(path)
    return found


def resolve_instance_path(
    *,
    root: Path | None = None,
    target: str | Path | None = None,
    backend: str = "auto",
) -> Path:
    """解析 agent_group 实例路径。

    规则：
    1. 显式 target 优先
    2. 若仅存在一个标准实例目录，使用该目录
    3. 若两个都存在，按 backend 偏好选择，并仍返回路径（调用方可自行提示）
    4. 若都不存在，按 backend 返回默认新建路径
    """
    base = (root or Path.cwd()).expanduser().resolve()
    if target is not None and str(target).strip():
        path = Path(target).expanduser()
        if not path.is_absolute():
            path = base / path
        return path.resolve()

    found = existing_instances(base)
    preferred = (base / default_instance_relpath(backend)).resolve()
    if len(found) == 1:
        return found[0]
    if len(found) == 2:
        return preferred if preferred in found else found[0]
    return preferred


def describe_resolution(
    *,
    root: Path | None = None,
    target: str | Path | None = None,
    backend: str = "auto",
) -> dict[str, object]:
    base = (root or Path.cwd()).expanduser().resolve()
    resolved_backend = detect_backend(backend)
    path = resolve_instance_path(root=base, target=target, backend=backend)
    found = existing_instances(base)
    return {
        "backend": resolved_backend,
        "path": str(path),
        "exists": path.is_dir(),
        "found_instances": [str(item) for item in found],
        "default_relpath": str(default_instance_relpath(resolved_backend)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="解析项目本地 agent_group 实例路径")
    parser.add_argument("--root", default=".", help="项目根目录，默认当前目录")
    parser.add_argument("--target", help="显式实例路径，提供时直接使用")
    parser.add_argument(
        "--backend",
        default="auto",
        choices=list(KNOWN_BACKENDS),
        help="执行后端：auto / codex / claude-code",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON 描述而不是纯路径",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    info = describe_resolution(root=Path(args.root), target=args.target, backend=args.backend)
    if args.json:
        import json

        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        # 目录契约要求：双标准实例并存且未显式指定路径时，应交由用户决策
        if not args.target and len(info["found_instances"]) > 1:
            print(
                "warning: 检测到多个 agent_group 实例，已按 backend 偏好选择；"
                "如需使用另一实例请显式传入 --target",
                file=sys.stderr,
            )
        print(info["path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
