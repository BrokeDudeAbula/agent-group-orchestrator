#!/usr/bin/env python3
"""后端中立的 agent_group 实例路径解析。"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


NEUTRAL_INSTANCE = Path(".agent_group")
CLAUDE_INSTANCE = Path(".claude") / "agent_group"
CODEX_INSTANCE = Path(".codex") / "agent_group"
STANDARD_INSTANCES = (NEUTRAL_INSTANCE, CLAUDE_INSTANCE, CODEX_INSTANCE)

CANONICAL_BACKENDS = ("neutral", "codex", "claude-code")
KNOWN_BACKENDS = ("auto", *CANONICAL_BACKENDS)
BACKEND_ALIASES = {
    "claude": "claude-code",
    "claude-code-cli": "claude-code",
    "claudecode": "claude-code",
    "host": "neutral",
    "cursor": "neutral",
    "opencode": "neutral",
    "grok": "neutral",
    "grok-build": "neutral",
}

# CLAUDE_PLUGIN_ROOT 只表示当前宿主可能是 Claude Code，不用于定位技能包文件。
CLAUDE_HOST_SIGNALS = (
    "CLAUDECODE",
    "CLAUDE_CODE_ENTRYPOINT",
    "CLAUDE_CODE_SESSION",
    "CLAUDE_PLUGIN_ROOT",
)
CODEX_HOST_SIGNALS = (
    "CODEX_THREAD_ID",
    "CODEX_CI",
    "CODEX_SANDBOX",
)


def skill_root() -> Path:
    """返回技能包根目录。

    由本文件位置解析（scripts/ 的上一级）。不读取 CLAUDE_PLUGIN_ROOT。
    """
    return Path(__file__).resolve().parents[1]


def canonical_backend(name: str) -> str:
    backend = name.strip().lower()
    backend = BACKEND_ALIASES.get(backend, backend)
    if backend not in CANONICAL_BACKENDS:
        raise ValueError(f"未知 backend: {name}")
    return backend


def _signal_present(names: tuple[str, ...]) -> bool:
    return any((os.environ.get(name) or "").strip() for name in names)


def detect_backend(requested: str = "auto") -> str:
    """解析执行后端。

    优先级：
    1. 显式 requested（非 auto）
    2. 环境变量 AGENT_GROUP_BACKEND
    3. Claude Code 环境信号（含可选的 CLAUDE_PLUGIN_ROOT）
    4. Codex 环境信号
    5. 默认 neutral（宿主中立的 .agent_group）
    """
    if requested and requested != "auto":
        return canonical_backend(requested)

    env_backend = (os.environ.get("AGENT_GROUP_BACKEND") or "").strip().lower()
    if env_backend and env_backend != "auto":
        return detect_backend(env_backend)

    if _signal_present(CLAUDE_HOST_SIGNALS):
        return "claude-code"
    if _signal_present(CODEX_HOST_SIGNALS):
        return "codex"
    return "neutral"


def default_instance_relpath(backend: str = "auto") -> Path:
    resolved = detect_backend(backend)
    if resolved == "claude-code":
        return CLAUDE_INSTANCE
    if resolved == "codex":
        return CODEX_INSTANCE
    return NEUTRAL_INSTANCE


def existing_instances(root: Path) -> list[Path]:
    found: list[Path] = []
    for rel in STANDARD_INSTANCES:
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
    3. 若多个标准实例并存，按 backend 偏好选择；偏好目录不存在时取发现顺序中的第一个
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
    if len(found) > 1:
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
        help="执行后端：auto / neutral / codex / claude-code",
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
        # 目录契约要求：多个标准实例并存且未显式指定路径时，应交由用户决策
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
