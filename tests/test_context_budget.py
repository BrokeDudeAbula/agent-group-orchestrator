"""热记忆上限、ledger 滚动和精简安装测试。"""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.agent_group_paths import skill_root
from scripts.compact_memory import roll_ledger_text
from scripts.context_budget import (
    LEDGER_RECENT_ROWS,
    LEDGER_ROLL_CHARS,
    LEDGER_ROLL_LINES,
    WORKER_OUTPUT_MAX_CHARS,
    WORKER_OUTPUT_MAX_LINES,
)


class LoadingProtocolTest(unittest.TestCase):
    def test_skill_starts_with_one_workflow_and_hot_files(self) -> None:
        text = (skill_root() / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("read every reference", text)
        self.assertNotIn("load them in this order", text)
        self.assertIn("rules/BOOTSTRAP.md", text)
        self.assertIn("current/STATE.md", text)
        self.assertIn("Load one workflow", text)

    def test_orchestrate_does_not_preload_pack_references(self) -> None:
        text = (skill_root() / "workflows" / "orchestrate.md").read_text(encoding="utf-8")
        self.assertNotIn("references/", text)
        self.assertIn("repo-explorer", text)
        self.assertIn("kernel-dev", text)
        self.assertIn(str(WORKER_OUTPUT_MAX_LINES), text)
        self.assertIn(str(WORKER_OUTPUT_MAX_CHARS), text)
        self.assertIn("memory/LEDGER_INDEX.md", text)

    def test_bootstrap_index_does_not_slurp_ledgers(self) -> None:
        text = (skill_root() / "assets" / "templates" / "instance" / "rules" / "BOOTSTRAP.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("On-demand index", text)
        self.assertIn("memory/LEDGER_INDEX.md", text)
        self.assertNotIn("memory/TASK_LEDGER.md", text)
        self.assertNotIn("memory/PROGRESS_LEDGER.md", text)
        self.assertNotIn("memory/DECISIONS.md", text)
        self.assertNotIn("memory/RISKS.md", text)
        self.assertIn("cheap read-only R0/R1", text)

    def test_output_contract_names_the_same_cap(self) -> None:
        text = (skill_root() / "references" / "output-contract.md").read_text(encoding="utf-8")
        self.assertIn(str(WORKER_OUTPUT_MAX_LINES), text)
        self.assertIn(str(WORKER_OUTPUT_MAX_CHARS), text)


class ValidateBudgetTest(unittest.TestCase):
    def test_sample_and_edge_strict(self) -> None:
        root = skill_root()
        for relative in ("examples/sample", "examples/edge-llm-research"):
            completed = self._validate(root / relative, strict=True)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)

    def test_worker_output_over_line_cap_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "sample"
            shutil.copytree(skill_root() / "examples" / "sample", instance)
            output = instance / "current" / "agent_outputs" / "SMP-20260616-01_repo-explorer.md"
            output.write_text(output.read_text(encoding="utf-8") + ("\nextra line" * 200), encoding="utf-8")
            completed = self._validate(instance, strict=False)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(str(WORKER_OUTPUT_MAX_LINES), completed.stdout)

    def test_missing_ledger_summary_fails_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "sample"
            shutil.copytree(skill_root() / "examples" / "sample", instance)
            ledger = instance / "memory" / "TASK_LEDGER.md"
            ledger.write_text("# Task Ledger\n\nA long note without a summary section.\n", encoding="utf-8")
            completed = self._validate(instance, strict=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("## Summary", completed.stdout)

    def _validate(self, instance: Path, *, strict: bool) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(skill_root() / "scripts" / "validate_agent_group.py")]
        if strict:
            command.append("--strict")
        command.append(str(instance))
        return subprocess.run(command, check=False, capture_output=True, text=True)


class CompactMemoryTest(unittest.TestCase):
    def test_table_roll_keeps_recent_rows(self) -> None:
        rows = [f"| T{i:02d} | title {i} | owner | done |" for i in range(1, 31)]
        text = "\n".join(
            [
                "# Task Ledger",
                "",
                "## Summary",
                "",
                "Previous summary.",
                "",
                "## Recent",
                "",
                "| Task ID | Title | Owner | Status |",
                "|---|---|---|---|",
                *rows,
                "",
            ]
        )
        rewritten, overflow = roll_ledger_text(text, "archive/ledgers/TASK_LEDGER.md", max_lines=24)
        self.assertIsNotNone(overflow)
        assert overflow is not None
        self.assertIn("## Summary", rewritten)
        self.assertIn("T30", rewritten)
        self.assertNotIn("T01", rewritten)
        self.assertIn("T01", overflow)
        self.assertIn("Archived table rows:", rewritten)
        recent_rows = [line for line in rewritten.splitlines() if line.startswith("| T") and "Task ID" not in line]
        self.assertLessEqual(len(rewritten.splitlines()), 24)
        self.assertEqual(len(recent_rows), LEDGER_RECENT_ROWS)

    def test_section_roll_and_second_pass_is_stable(self) -> None:
        sections = []
        for day in range(1, 9):
            bullets = "\n".join(f"- note {day}-{n}" for n in range(1, 9))
            sections.append(f"## 2026-06-{day:02d}\n\n{bullets}\n")
        text = "# Progress Ledger\n\n## Summary\n\nOld summary.\n\n" + "\n".join(sections)
        self.assertGreater(len(text.splitlines()), LEDGER_ROLL_LINES)
        rewritten, overflow = roll_ledger_text(text, "archive/ledgers/PROGRESS_LEDGER.md")
        self.assertIsNotNone(overflow)
        assert overflow is not None
        self.assertIn("2026-06-01", overflow)
        self.assertIn("2026-06-08", rewritten)
        self.assertLessEqual(len(rewritten.splitlines()), LEDGER_ROLL_LINES)
        self.assertLessEqual(len(rewritten), LEDGER_ROLL_CHARS)
        again, second_overflow = roll_ledger_text(rewritten, "archive/ledgers/PROGRESS_LEDGER.md")
        self.assertIsNone(second_overflow)
        self.assertEqual(again, rewritten)

    def test_cli_archives_current_and_rolls_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "group"
            (root / "current").mkdir(parents=True)
            (root / "memory").mkdir()
            (root / "current" / "STATE.md").write_text("# Current State\n\n## Active Goal\n\nDone.\n", encoding="utf-8")
            rows = "\n".join(f"| T{i:02d} | title {i} |" for i in range(1, 80))
            ledger = "\n".join(
                [
                    "# Task Ledger",
                    "",
                    "## Summary",
                    "",
                    "Growing.",
                    "",
                    "## Recent",
                    "",
                    "| Task ID | Title |",
                    "|---|---|",
                    rows,
                    "",
                ]
            )
            (root / "memory" / "TASK_LEDGER.md").write_text(ledger, encoding="utf-8")
            script = skill_root() / "scripts" / "compact_memory.py"
            dry = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--target",
                    str(root),
                    "--archive-name",
                    "20260616_demo",
                    "--dry-run",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertIn("dry-run: 未改写 ledger", dry.stdout)
            self.assertTrue((root / "current" / "STATE.md").is_file())
            self.assertIn("T01", (root / "memory" / "TASK_LEDGER.md").read_text(encoding="utf-8"))

            applied = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--target",
                    str(root),
                    "--archive-name",
                    "20260616_demo",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertIn("Previous phase archived", (root / "current" / "STATE.md").read_text(encoding="utf-8"))
            rolled = (root / "memory" / "TASK_LEDGER.md").read_text(encoding="utf-8")
            archived = (root / "archive" / "ledgers" / "TASK_LEDGER.md").read_text(encoding="utf-8")
            self.assertIn("## Summary", rolled)
            self.assertNotIn("| T01 |", rolled)
            self.assertIn("| T01 |", archived)
            self.assertLessEqual(len(rolled.splitlines()), LEDGER_ROLL_LINES)


class InstallSkillTest(unittest.TestCase):
    def test_install_copies_runtime_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest_root = Path(tmp) / "skills"
            script = skill_root() / "scripts" / "install_skill.py"
            dry = subprocess.run(
                [sys.executable, str(script), "--dest", str(dest_root), "--dry-run"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertIn("examples", dry.stdout)
            self.assertIn("ROADMAP.html", dry.stdout)
            self.assertFalse(dest_root.exists())

            completed = subprocess.run(
                [sys.executable, str(script), "--dest", str(dest_root)],
                check=False,
                capture_output=True,
                text=True,
                env=self._clean_env(),
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            dest = dest_root / "agent-group"
            self.assertTrue((dest / "SKILL.md").is_file())
            self.assertTrue((dest / "workflows" / "orchestrate.md").is_file())
            self.assertTrue((dest / "scripts" / "install_skill.py").is_file())
            self.assertTrue((dest / "references" / "routing-policy.md").is_file())
            self.assertTrue((dest / "assets" / "templates" / "instance" / "rules" / "BOOTSTRAP.md").is_file())
            for name in ("examples", "tests", "ROADMAP.html", "README.md", "AGENTS.md"):
                self.assertFalse((dest / name).exists(), name)

    def _clean_env(self) -> dict[str, str]:
        env = os.environ.copy()
        for name in ("CLAUDE_PLUGIN_ROOT", "CLAUDECODE", "CODEX_THREAD_ID"):
            env.pop(name, None)
        return env


if __name__ == "__main__":
    unittest.main()
