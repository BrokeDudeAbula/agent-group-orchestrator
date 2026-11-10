"""实例路径解析与初始化测试。"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.agent_group_paths import (
    CLAUDE_HOST_SIGNALS,
    CODEX_HOST_SIGNALS,
    describe_resolution,
    detect_backend,
    resolve_instance_path,
    skill_root,
)


HOST_SIGNALS = (*CLAUDE_HOST_SIGNALS, *CODEX_HOST_SIGNALS, "AGENT_GROUP_BACKEND")


class AgentGroupPathsTest(unittest.TestCase):
    def setUp(self) -> None:
        self._saved = {name: os.environ.get(name) for name in HOST_SIGNALS}
        for name in HOST_SIGNALS:
            os.environ.pop(name, None)

    def tearDown(self) -> None:
        for name, value in self._saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def test_skill_root_ignores_plugin_root_signal(self) -> None:
        os.environ["CLAUDE_PLUGIN_ROOT"] = str(Path("/tmp") / "not-the-skill-pack")
        root = skill_root()
        self.assertTrue((root / "SKILL.md").is_file())
        self.assertTrue((root / "assets" / "templates" / "instance").is_dir())
        self.assertNotEqual(root, Path(os.environ["CLAUDE_PLUGIN_ROOT"]))

    def test_auto_defaults_to_neutral_without_host_signals(self) -> None:
        self.assertEqual(detect_backend("auto"), "neutral")
        self.assertEqual(describe_resolution(root=Path("."))["default_relpath"], ".agent_group")

    def test_claude_plugin_root_selects_claude_backend_only(self) -> None:
        os.environ["CLAUDE_PLUGIN_ROOT"] = str(Path("/tmp") / "claude-signal-only")
        self.assertEqual(detect_backend("auto"), "claude-code")
        info = describe_resolution(root=Path("."))
        self.assertEqual(info["default_relpath"], os.path.join(".claude", "agent_group"))
        self.assertTrue((skill_root() / "scripts" / "init_agent_group.py").is_file())

    def test_explicit_backend_overrides_host_signals(self) -> None:
        os.environ["CLAUDECODE"] = "1"
        os.environ["CODEX_THREAD_ID"] = "thread-demo"
        self.assertEqual(detect_backend("neutral"), "neutral")
        self.assertEqual(detect_backend("codex"), "codex")
        self.assertEqual(detect_backend("claude"), "claude-code")

    def test_codex_signal_selects_codex_when_claude_is_absent(self) -> None:
        os.environ["CODEX_CI"] = "1"
        self.assertEqual(detect_backend("auto"), "codex")

    def test_claude_signal_wins_over_codex_signal(self) -> None:
        os.environ["CLAUDE_CODE_SESSION"] = "session-demo"
        os.environ["CODEX_SANDBOX"] = "seatbelt"
        self.assertEqual(detect_backend("auto"), "claude-code")

    def test_agent_group_backend_alias(self) -> None:
        os.environ["AGENT_GROUP_BACKEND"] = "cursor"
        self.assertEqual(detect_backend("auto"), "neutral")

    def test_unknown_backend_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            detect_backend("unknown-host")

    def test_single_existing_instance_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            legacy = root / ".codex" / "agent_group"
            legacy.mkdir(parents=True)
            resolved = resolve_instance_path(root=root, backend="neutral")
            self.assertEqual(resolved, legacy.resolve())

    def test_multiple_instances_follow_backend_preference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            neutral = root / ".agent_group"
            claude = root / ".claude" / "agent_group"
            codex = root / ".codex" / "agent_group"
            for path in (neutral, claude, codex):
                path.mkdir(parents=True)
            self.assertEqual(
                resolve_instance_path(root=root, backend="codex"),
                codex.resolve(),
            )
            self.assertEqual(
                resolve_instance_path(root=root, backend="neutral"),
                neutral.resolve(),
            )

    def test_preference_missing_among_multiple_uses_first_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude = root / ".claude" / "agent_group"
            codex = root / ".codex" / "agent_group"
            claude.mkdir(parents=True)
            codex.mkdir(parents=True)
            self.assertEqual(
                resolve_instance_path(root=root, backend="neutral"),
                claude.resolve(),
            )

    def test_explicit_target_overrides_existing_instances(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".agent_group").mkdir()
            chosen = root / "custom-instance"
            self.assertEqual(
                resolve_instance_path(root=root, target=chosen, backend="neutral"),
                chosen.resolve(),
            )

    def test_cli_warns_when_multiple_instances_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".agent_group").mkdir()
            (root / ".codex" / "agent_group").mkdir(parents=True)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(skill_root() / "scripts" / "agent_group_paths.py"),
                    "--root",
                    str(root),
                    "--backend",
                    "neutral",
                ],
                check=False,
                capture_output=True,
                text=True,
                env=self._clean_env(),
            )
            self.assertEqual(completed.returncode, 0)
            self.assertIn(str((root / ".agent_group").resolve()), completed.stdout)
            self.assertIn("多个 agent_group 实例", completed.stderr)

    def test_init_legacy_backend_and_neutral_default(self) -> None:
        script = skill_root() / "scripts" / "init_agent_group.py"
        with tempfile.TemporaryDirectory() as tmp:
            legacy_root = Path(tmp) / "legacy"
            neutral_root = Path(tmp) / "neutral"
            plugin_root = Path(tmp) / "missing-plugin-root"
            legacy_root.mkdir()
            neutral_root.mkdir()

            legacy = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--backend",
                    "claude-code",
                    "--root",
                    str(legacy_root),
                    "--project-name",
                    "legacy-demo",
                ],
                check=False,
                capture_output=True,
                text=True,
                env=self._clean_env(),
            )
            self.assertEqual(legacy.returncode, 0, legacy.stderr)
            legacy_instance = legacy_root / ".claude" / "agent_group"
            self.assertTrue((legacy_instance / "rules" / "BOOTSTRAP.md").is_file())
            self.assertIn(
                "execution_backend: claude-code",
                (legacy_instance / "config.yml").read_text(encoding="utf-8"),
            )

            neutral_env = self._clean_env()
            neutral_env["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
            neutral = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--backend",
                    "neutral",
                    "--root",
                    str(neutral_root),
                    "--project-name",
                    "neutral-demo",
                ],
                check=False,
                capture_output=True,
                text=True,
                env=neutral_env,
            )
            self.assertEqual(neutral.returncode, 0, neutral.stderr)
            neutral_instance = neutral_root / ".agent_group"
            self.assertTrue((neutral_instance / "current" / "tasks.csv").is_file())
            self.assertIn(
                "execution_backend: neutral",
                (neutral_instance / "config.yml").read_text(encoding="utf-8"),
            )
            self.assertFalse(plugin_root.exists())

            validate = subprocess.run(
                [
                    sys.executable,
                    str(skill_root() / "scripts" / "validate_agent_group.py"),
                    "--strict",
                    str(neutral_instance),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)

    def _clean_env(self) -> dict[str, str]:
        env = os.environ.copy()
        for name in HOST_SIGNALS:
            env.pop(name, None)
        return env


if __name__ == "__main__":
    unittest.main()
