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


# 这些地址不是个人收件箱：文档占位符、GitHub noreply 身份，
# 以及 Cursor Agent 的机器人提交身份。其它 @cursor.com 地址仍视为个人邮箱。
NONPERSONAL_EMAILS = (
    r"noreply@example\.com",
    r"noreply@github\.com",
    r"[A-Z0-9._%+-]+@users\.noreply\.github\.com",
    r"cursoragent@cursor\.com",
)


def personal_email_pattern() -> Pattern[str]:
    allowed = "|".join(NONPERSONAL_EMAILS)
    return re.compile(
        rf"(?i)\b(?!(?:{allowed})\b)"
        r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
    )


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
            personal_email_pattern(),
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


def git_ref_exists(root: Path, ref: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", ref],
        cwd=root,
        capture_output=True,
    )
    return result.returncode == 0


def default_branch_ref(root: Path) -> str | None:
    """解析已发布历史所在的默认分支。

    CI 以 detached merge ref 检出，已发布提交在 origin/main，而不是当前 HEAD。
    """
    head = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    candidates: list[str] = []
    if head.returncode == 0:
        ref = head.stdout.strip()
        if ref.startswith("refs/remotes/"):
            candidates.append(ref.removeprefix("refs/remotes/"))
    candidates.extend(["origin/main", "main", "origin/master", "master"])
    for candidate in candidates:
        if git_ref_exists(root, candidate):
            return candidate
    return None


def published_identity_emails(root: Path) -> set[str]:
    """返回默认分支上已经公开的作者和提交者邮箱。

    这些地址位于已发布提交的身份字段中。扫描仍会检查文件内容和提交说明。
    """
    ref = default_branch_ref(root)
    if ref is None:
        return set()
    raw = git_output(root, "log", "--format=%ae%x1f%ce", ref).decode("utf-8", errors="replace")
    emails: set[str] = set()
    for line in raw.splitlines():
        for part in line.split("\x1f"):
            address = part.strip().lower()
            if address:
                emails.add(address)
    return emails


def single_line(value: str) -> str:
    return " ".join(value.replace("\r", " ").splitlines()).strip()


def without_published_identity_emails(
    findings: list[Finding],
    commit_text: str,
    published: set[str],
) -> list[Finding]:
    """去掉默认分支身份字段中的已知邮箱。

    commit_text 的前四行固定为作者名、作者邮箱、提交者名、提交者邮箱。
    提交说明和文件内容中的个人邮箱仍会报告。
    """
    if not published:
        return findings
    lines = commit_text.splitlines()
    kept: list[Finding] = []
    for finding in findings:
        if finding.rule_id != "personal-email" or finding.line not in (2, 4):
            kept.append(finding)
            continue
        if finding.line > len(lines):
            kept.append(finding)
            continue
        if lines[finding.line - 1].strip().lower() not in published:
            kept.append(finding)
    return kept


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
    published_emails = published_identity_emails(root)
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
            [
                single_line(author),
                single_line(author_email),
                single_line(committer),
                single_line(committer_email),
                message,
            ]
        )
        metadata_path = root / ".git-history" / f"{commit_id[:12]}.metadata"
        findings.extend(
            without_published_identity_emails(
                scan_text(metadata_path, commit_text),
                commit_text,
                published_emails,
            )
        )

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
