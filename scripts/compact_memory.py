#!/usr/bin/env python3
"""归档 agent_group 的 current 工作记忆，并滚动超长 ledger。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import shutil
import sys
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from context_budget import (  # noqa: E402
    LEDGER_NAMES,
    LEDGER_RECENT_ROWS,
    LEDGER_RECENT_SECTIONS,
    LEDGER_ROLL_CHARS,
    LEDGER_ROLL_LINES,
    LEDGER_SUMMARY_MAX_LINES,
    PROJECT_FACTS_MAX_CHARS,
    PROJECT_FACTS_MAX_LINES,
)


CURRENT_FILES = ["STATE.md", "epic.md", "acceptance.md", "tasks.csv", "tasks.meta.yml"]
TASK_COLUMNS = ["id", "title", "owner", "status", "risk", "depends_on", "inputs", "outputs", "notes"]
EMPTY_SUMMARY_LINES = {
    "No durable task records yet.",
    "No progress recorded yet.",
    "No decisions recorded yet.",
    "No risks recorded yet.",
    "None.",
}


@dataclass(frozen=True)
class LedgerRoll:
    source: Path
    archive_path: Path
    rewritten: str
    overflow: str
    archive_name: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="归档 current 状态和 worker 输出，并滚动 ledger")
    parser.add_argument("--target", required=True, help="agent_group 目录")
    parser.add_argument("--archive-name", required=True, help="archive 子目录名")
    parser.add_argument("--dry-run", action="store_true", help="只打印计划，不移动文件")
    parser.add_argument(
        "--no-reset-current",
        action="store_true",
        help="归档后不重建 current 热状态文件；默认会重建以保持实例可校验",
    )
    parser.add_argument(
        "--no-roll-ledgers",
        action="store_true",
        help="只归档 current/，不滚动 memory/ 下的耐久 ledger",
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


def _within(text: str, max_lines: int, max_chars: int) -> bool:
    return len(text.splitlines()) <= max_lines and len(text) <= max_chars


def _ensure_newline(text: str) -> str:
    if text.endswith("\n"):
        return text
    return text + "\n"


def _is_separator(line: str) -> bool:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return False
    inner = stripped.replace("|", "").replace(":", "").replace("-", "").replace(" ", "")
    return inner == ""


def _section_chunks(text: str) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.startswith("## ") and current:
            chunks.append("".join(current))
            current = [line]
        else:
            current.append(line)
    if current:
        chunks.append("".join(current))
    return chunks


def _split_summary(text: str) -> tuple[str, str, str]:
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.startswith("## Summary")), None)
    if start is None:
        preamble_lines: list[str] = []
        for line in lines:
            if line.startswith("## ") or line.lstrip().startswith("|"):
                break
            preamble_lines.append(line)
        preamble = "".join(preamble_lines)
        return preamble, "", text[len(preamble) :]

    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    preamble = "".join(lines[:start])
    summary = "".join(lines[start + 1 : end]).strip("\n")
    remainder = "".join(lines[end:])
    return preamble, summary, remainder


def _split_sections(text: str, keep: int) -> tuple[str, str] | None:
    chunks = _section_chunks(text)
    if not chunks:
        return None
    if chunks[0].startswith("## "):
        leading = ""
        sections = chunks
    else:
        leading = chunks[0]
        sections = chunks[1:]
    if keep < 1 or len(sections) <= keep:
        return None
    overflow = leading + "".join(sections[:-keep])
    recent = "".join(sections[-keep:])
    if not overflow.strip():
        return None
    return overflow, recent


def _split_table(text: str, recent_rows: int) -> tuple[str, str] | None:
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if line.lstrip().startswith("|")), None)
    if start is None:
        return None
    end = start
    while end < len(lines) and lines[end].lstrip().startswith("|"):
        end += 1
    table = lines[start:end]
    data = [line for line in table if not _is_separator(line)]
    if len(data) <= 1 or len(data) - 1 <= recent_rows:
        return None
    header = data[0]
    separator = next((line for line in table if _is_separator(line)), None)
    body = data[1:]
    old = body[:-recent_rows]
    kept = body[-recent_rows:]

    def render(rows: list[str]) -> str:
        parts = [header]
        if separator is not None:
            parts.append(separator)
        parts.extend(rows)
        return "".join(parts)

    prefix = "".join(lines[:start])
    suffix = "".join(lines[end:])
    return prefix + render(old), render(kept) + suffix


def _count_data_rows(text: str) -> int:
    rows = 0
    in_table = False
    for line in text.splitlines():
        stripped = line.lstrip()
        if not stripped.startswith("|"):
            in_table = False
            continue
        if _is_separator(stripped):
            continue
        if not in_table:
            in_table = True
            continue
        rows += 1
    return rows


def _cut_lines(text: str) -> tuple[str, str]:
    lines = text.splitlines(keepends=True)
    if len(lines) >= 2:
        keep = max(1, min(12, len(lines) // 2))
        return "".join(lines[:-keep]), "".join(lines[-keep:])
    if len(text) > 200:
        cut = len(text) // 2
        return text[:cut], text[cut:]
    return text, ""


def _divide(remainder: str, recent_rows: int, recent_sections: int) -> tuple[str, str]:
    section_split = _split_sections(remainder, recent_sections)
    if section_split is not None:
        return section_split
    table_split = _split_table(remainder, recent_rows)
    if table_split is not None:
        return table_split
    return _cut_lines(remainder)


def _shrink_once(recent: str) -> tuple[str, str]:
    chunks = _section_chunks(recent)
    if chunks and not chunks[0].startswith("## "):
        leading = chunks[0]
        sections = chunks[1:]
    else:
        leading = ""
        sections = chunks
    if len(sections) > 1:
        return "".join(sections[1:]), leading + sections[0]

    data_rows = _count_data_rows(recent)
    if data_rows > 1:
        table_split = _split_table(recent, data_rows - 1)
        if table_split is not None:
            overflow, kept = table_split
            return kept, overflow

    lines = recent.splitlines(keepends=True)
    if len(lines) > 1:
        return "".join(lines[1:]), lines[0]
    if len(recent) > 400:
        cut = min(400, len(recent) // 2)
        return recent[cut:], recent[:cut]
    return recent, ""


def _summarize_overflow(overflow: str, archive_relpath: str) -> str:
    headings: list[str] = []
    data_rows = 0
    in_table = False
    for line in overflow.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("|"):
            if _is_separator(stripped):
                continue
            if not in_table:
                in_table = True
                continue
            data_rows += 1
            continue
        in_table = False
        if line.startswith("## "):
            title = line[3:].strip()
            if title and title not in {"Summary", "Recent"}:
                headings.append(title)

    bits = [f"Older entries archived to `{archive_relpath}`."]
    if headings:
        shown = headings[:6]
        label = ", ".join(shown)
        extra = len(headings) - len(shown)
        if extra:
            label += f" (+{extra} more)"
        bits.append(f"Archived sections: {label}.")
    if data_rows:
        bits.append(f"Archived table rows: {data_rows}.")
    if not headings and not data_rows:
        bits.append(f"Archived lines: {len(overflow.splitlines())}.")
    return " ".join(bits)


def _merge_summary(existing: str, note: str, limit: int) -> str:
    lines = [
        line.rstrip()
        for line in existing.splitlines()
        if line.strip() and line.strip() not in EMPTY_SUMMARY_LINES
    ]
    lines.append(note)
    if len(lines) > limit:
        dropped = len(lines) - limit + 1
        lines = [f"Earlier rollups collapsed ({dropped} lines)."] + lines[-(limit - 1) :]
    return "\n".join(lines)


def _assemble(preamble: str, summary: str, recent: str) -> str:
    title = preamble.strip() or "# Ledger"
    recent_body = recent.strip()
    if recent_body.startswith("## Recent"):
        recent_part = recent_body
    elif recent_body:
        recent_part = "## Recent\n\n" + recent_body
    else:
        recent_part = "## Recent\n\nNone."
    return "\n".join(
        [
            title,
            "",
            "## Summary",
            "",
            summary.strip() or "None.",
            "",
            recent_part,
            "",
        ]
    )


def roll_ledger_text(
    text: str,
    archive_relpath: str,
    *,
    max_lines: int = LEDGER_ROLL_LINES,
    max_chars: int = LEDGER_ROLL_CHARS,
    recent_rows: int = LEDGER_RECENT_ROWS,
    recent_sections: int = LEDGER_RECENT_SECTIONS,
    summary_lines: int = LEDGER_SUMMARY_MAX_LINES,
) -> tuple[str, str | None]:
    """把超长 ledger 收成摘要加近期尾部。

    返回 (改写后的热文本, 归档溢出)。未超限时溢出为 None，热文本保持原样。
    """

    if _within(text, max_lines, max_chars):
        return text, None

    preamble, summary, remainder = _split_summary(text)
    overflow, recent = _divide(remainder, recent_rows, recent_sections)
    guard = 0
    while True:
        note = _summarize_overflow(overflow, archive_relpath)
        rewritten = _assemble(preamble, _merge_summary(summary, note, summary_lines), recent)
        if _within(rewritten, max_lines, max_chars):
            return _ensure_newline(rewritten), _ensure_newline(overflow)
        kept, extra = _shrink_once(recent)
        if not extra.strip():
            return _ensure_newline(rewritten), _ensure_newline(overflow)
        recent = kept
        overflow = extra + overflow
        guard += 1
        if guard > 40:
            return _ensure_newline(rewritten), _ensure_newline(overflow)


def plan_ledger_rolls(root: Path, archive_name: str) -> list[LedgerRoll]:
    rolls: list[LedgerRoll] = []
    for name in LEDGER_NAMES:
        source = root / "memory" / name
        if not source.is_file():
            continue
        archive_relpath = f"archive/ledgers/{name}"
        rewritten, overflow = roll_ledger_text(source.read_text(encoding="utf-8"), archive_relpath)
        if overflow is None:
            continue
        rolls.append(
            LedgerRoll(
                source=source,
                archive_path=root / "archive" / "ledgers" / name,
                rewritten=rewritten,
                overflow=overflow,
                archive_name=archive_name,
            )
        )
    return rolls


def apply_rolls(rolls: list[LedgerRoll]) -> None:
    for roll in rolls:
        roll.archive_path.parent.mkdir(parents=True, exist_ok=True)
        block = f"## Rolled {roll.archive_name}\n\n{roll.overflow}"
        if not block.endswith("\n"):
            block += "\n"
        if roll.archive_path.exists():
            existing = roll.archive_path.read_text(encoding="utf-8")
            if not existing.endswith("\n"):
                existing += "\n"
            roll.archive_path.write_text(existing + "\n" + block, encoding="utf-8")
        else:
            title = f"# Archived {roll.source.name}\n\n"
            roll.archive_path.write_text(title + block, encoding="utf-8")
        roll.source.write_text(roll.rewritten, encoding="utf-8")


def warn_project_facts(root: Path) -> None:
    facts = root / "memory" / "PROJECT_FACTS.md"
    if not facts.is_file():
        return
    text = facts.read_text(encoding="utf-8")
    if _within(text, PROJECT_FACTS_MAX_LINES, PROJECT_FACTS_MAX_CHARS):
        return
    print(
        "warning: memory/PROJECT_FACTS.md 超过热记忆上限，"
        f"请压缩到 {PROJECT_FACTS_MAX_LINES} 行 / {PROJECT_FACTS_MAX_CHARS} 字符以内"
    )


def main() -> int:
    args = parse_args()
    root = Path(args.target).expanduser().resolve()
    archive = root / "archive" / args.archive_name
    moves = plan_moves(root, archive)
    rolls = [] if args.no_roll_ledgers else plan_ledger_rolls(root, args.archive_name)
    warn_project_facts(root)

    if not moves and not rolls:
        print("没有可归档文件")
        return 0

    if moves:
        print(f"archive target: {archive}")
        for src, dst in moves:
            print(f"{src} -> {dst}")
    for roll in rolls:
        print(f"ledger roll: {roll.source} -> {roll.archive_path}")

    if args.dry_run:
        if moves:
            print("dry-run: 未执行移动")
            if not args.no_reset_current:
                print(
                    "dry-run: 归档成功后将重建 current/STATE.md、"
                    "current/epic.md、current/acceptance.md 和 current/tasks.csv"
                )
        if rolls:
            print("dry-run: 未改写 ledger")
        return 0

    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

    if moves and not args.no_reset_current:
        reset_current(root, args.archive_name)
        print("current reset complete")
    elif moves:
        (root / "current" / "agent_outputs").mkdir(parents=True, exist_ok=True)
        (root / "current" / "agent_outputs" / ".gitkeep").touch(exist_ok=True)

    if rolls:
        apply_rolls(rolls)
        print("ledger roll complete")
    if moves:
        print("archive complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
