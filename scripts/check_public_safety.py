#!/usr/bin/env python3
"""扫描仓库中的凭证、真实环境标识和误粘贴运行时内容。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
from re import Pattern
import subprocess


SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "venv",
}
MAX_REPORTED_FINDINGS = 100


@dataclass(frozen=True)
class Rule:
    rule_id: str
    description: str
    pattern: Pattern[str]


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule_id: str
    description: str


def build_rules() -> tuple[Rule, ...]:
    pasted_prompts = ("请" + "完成如下修改", "请" + "修改 examples 路径下的 demo")
    return (
        Rule(
            "cloud-token",
            "疑似云服务或代码托管访问令牌",
            re.compile(
                r"(?:AKIA|ASIA)[0-9A-Z]{16}"
                r"|(?:sk|rk|pk)-(?:proj-)?[A-Za-z0-9_-]{16,}"
                r"|github_pat_[A-Za-z0-9_]{20,}"
                r"|gh[pousr]_[A-Za-z0-9]{20,}"
                r"|glpat-[A-Za-z0-9_-]{16,}"
                r"|xox[baprs]-[A-Za-z0-9-]{10,}"
                r"|AIza[0-9A-Za-z_-]{30,}"
            ),
        ),
        Rule(
            "private-key",
            "私钥头或 JWT",
            re.compile(
                r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"
                r"|eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"
            ),
        ),
        Rule(
            "personal-email",
            "疑似个人邮箱地址",
            re.compile(
                r"(?i)\b(?!noreply@example\.com\b)"
                r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
            ),
        ),
        Rule(
            "credential-assignment",
            "疑似硬编码凭证赋值",
            re.compile(
                r"(?i)\b(?:password|passwd|secret|token|api[_-]?key|access[_-]?key|"
                r"private[_-]?key|client[_-]?secret)\s*[:=]\s*[\"']?"
                r"(?!(?:<|example|placeholder|redacted|none|null|\$\{))"
                r"[A-Za-z0-9._~+/=-]{8,}"
            ),
        ),
        Rule(
            "personal-path",
            "真实用户或工作区绝对路径",
            re.compile(
                r"/(?:Users|home|workspace)/"
                r"(?!(?:<[^>]+>|example|user|username|your-[^/\s]+)(?:/|\b))"
                r"[^/\s`\"']+(?:/[^\s`\"']*)?"
            ),
        ),
        Rule(
            "device-identifier",
            "具体远端设备或容器标识",
            re.compile(r"\b(?:orin_[A-Za-z0-9_-]+|[A-Za-z0-9._-]+_lape)\b", re.I),
        ),
        Rule(
            "runtime-uuid",
            "疑似样本、任务或线程 UUID",
            re.compile(
                r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
            ),
        ),
        Rule(
            "pasted-task-prompt",
            "疑似误粘贴的用户任务提示",
            re.compile("|".join(re.escape(marker) for marker in pasted_prompts)),
        ),
        Rule(
            "generated-perf-output",
            "疑似项目本地性能报告路径",
            re.compile(r"\bperf_runs_[A-Za-z0-9_.-]+\b"),
        ),
    )


RULES = build_rules()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="扫描公开仓库中的敏感内容")
    parser.add_argument(
        "--git-history",
        action="store_true",
        help="同时扫描所有本地可达 Git 历史及提交元数据",
    )
    parser.add_argument(
        "--history-ref",
        action="append",
        default=[],
        help="仅扫描指定 Git ref，可重复传入；默认扫描全部 refs",
    )
    parser.add_argument("root", nargs="?", default=".", help="待扫描的仓库根目录")
    return parser.parse_args()


def iter_files(root: Path) -> list[Path]:
    paths: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.is_symlink():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        paths.append(path)
    return sorted(paths)


def scan_text(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for rule in RULES:
            if rule.pattern.search(line):
                findings.append(
                    Finding(
                        path=path,
                        line=line_number,
                        rule_id=rule.rule_id,
                        description=rule.description,
                    )
                )
    return findings


def scan_file(path: Path) -> list[Finding]:
    data = path.read_bytes()
    return scan_bytes(path, data)


def scan_bytes(path: Path, data: bytes) -> list[Finding]:
    if b"\0" in data:
        return []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []
    return scan_text(path, text)


def git_output(root: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"无法读取 Git 历史: {error}") from error
    return result.stdout


def scan_git_history(root: Path, refs: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    object_paths: dict[str, str] = {}
    revision_args = refs or ["--all"]
    object_lines = git_output(
        root, "rev-list", "--objects", *revision_args
    ).decode("utf-8")
    for line in object_lines.splitlines():
        object_id, separator, path = line.partition(" ")
        if separator and path:
            object_paths.setdefault(object_id, path)

    for object_id, path in object_paths.items():
        object_type = git_output(root, "cat-file", "-t", object_id).strip()
        if object_type != b"blob":
            continue
        data = git_output(root, "cat-file", "blob", object_id)
        history_path = root / ".git-history" / object_id[:12] / path
        findings.extend(scan_bytes(history_path, data))

    metadata = git_output(
        root,
        "log",
        "--format=%H%x1f%an%x1f%ae%x1f%cn%x1f%ce%x1f%B%x1e",
        *revision_args,
    ).decode("utf-8")
    for record in metadata.split("\x1e"):
        fields = record.strip().split("\x1f", maxsplit=5)
        if len(fields) != 6:
            continue
        commit_id, author, author_email, committer, committer_email, message = fields
        commit_text = "\n".join(
            [author, author_email, committer, committer_email, message]
        )
        metadata_path = root / ".git-history" / f"{commit_id[:12]}.metadata"
        findings.extend(scan_text(metadata_path, commit_text))

    return findings


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"扫描目标不是目录: {root}")

    findings: list[Finding] = []
    for path in iter_files(root):
        findings.extend(scan_file(path))
    if args.git_history:
        findings.extend(scan_git_history(root, args.history_ref))

    if findings:
        print("public safety scan failed:")
        for finding in findings[:MAX_REPORTED_FINDINGS]:
            relative_path = finding.path.relative_to(root)
            print(
                f"- {relative_path}:{finding.line}: "
                f"[{finding.rule_id}] {finding.description}"
            )
        omitted = len(findings) - MAX_REPORTED_FINDINGS
        if omitted > 0:
            print(f"- 另有 {omitted} 条发现未展开")
        print(f"共发现 {len(findings)} 条问题")
        return 1

    print(f"public safety scan passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
