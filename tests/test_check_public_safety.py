"""公开安全扫描器测试。"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.check_public_safety import (
    scan_git_history,
    scan_text,
    without_published_identity_emails,
)


class PublicSafetyTest(unittest.TestCase):
    def rule_ids(self, text: str) -> set[str]:
        findings = scan_text(Path("fixture.txt"), text)
        return {finding.rule_id for finding in findings}

    def test_accepts_neutral_documentation(self) -> None:
        text = "model path: /workspace/<user>/model\ncredential: <redacted>\n"
        self.assertEqual(self.rule_ids(text), set())

    def test_rejects_common_access_token(self) -> None:
        token = "sk-" + "a" * 24
        self.assertIn("cloud-token", self.rule_ids(token))

    def test_rejects_personal_email(self) -> None:
        email = "developer" + "@private.example"
        self.assertIn("personal-email", self.rule_ids(email))

    def test_accepts_placeholder_and_github_noreply_addresses(self) -> None:
        addresses = (
            "noreply" + "@example.com",
            "noreply" + "@github.com",
            "octocat" + "@users.noreply.github.com",
            "1+" + "octocat" + "@users.noreply.github.com",
        )
        for address in addresses:
            self.assertNotIn("personal-email", self.rule_ids(f"Author: Name <{address}>"))

    def test_keeps_published_identity_but_reports_message_email(self) -> None:
        published_address = "owner" + "@published.example"
        fresh_email = "owner" + "@new-private.example"
        text = "\n".join(
            [
                "Published Author",
                published_address,
                "Published Author",
                published_address,
                f"note {published_address}",
                fresh_email,
            ]
        )
        findings = scan_text(Path("commit.metadata"), text)
        kept = without_published_identity_emails(findings, text, {published_address})
        flagged_lines = {finding.line for finding in kept if finding.rule_id == "personal-email"}
        self.assertEqual(flagged_lines, {5, 6})

    def test_rejects_personal_path(self) -> None:
        path = "/Users/" + "developer/private/project"
        self.assertIn("personal-path", self.rule_ids(path))

    def test_rejects_device_identifier(self) -> None:
        container = "developer" + "_lape"
        self.assertIn("device-identifier", self.rule_ids(container))

    def test_rejects_runtime_uuid(self) -> None:
        identifier = "12345678-1234-1234-1234-" + "123456789abc"
        self.assertIn("runtime-uuid", self.rule_ids(identifier))

    def test_rejects_pasted_task_prompt(self) -> None:
        prompt = "请" + "完成如下修改：更新远端模型"
        self.assertIn("pasted-task-prompt", self.rule_ids(prompt))


class GitHistorySafetyTest(unittest.TestCase):
    def test_history_scan_ignores_published_identity_only(self) -> None:
        historical = "owner" + "@published.example"
        fresh = "owner" + "@new-private.example"
        leaked = "owner" + "@file-private.example"
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.git(repo, "init", "-b", "main")
            (repo / "README.md").write_text("neutral\n", encoding="utf-8")
            self.git(repo, "add", "README.md")
            self.commit(repo, "Add readme", historical)
            self.git(repo, "checkout", "-b", "topic")
            (repo / "NOTES.md").write_text(f"contact {leaked}\n", encoding="utf-8")
            self.git(repo, "add", "NOTES.md")
            self.commit(repo, f"Record contact {historical}", fresh)

            findings = [
                finding
                for finding in scan_git_history(repo, [])
                if finding.rule_id == "personal-email"
            ]
            metadata = [finding for finding in findings if finding.path.name.endswith(".metadata")]
            blobs = [finding for finding in findings if not finding.path.name.endswith(".metadata")]
            fresh_commit = self.rev_parse(repo, "HEAD")
            self.assertEqual(
                {(finding.path.name[:12], finding.line) for finding in metadata},
                {(fresh_commit[:12], 2), (fresh_commit[:12], 4), (fresh_commit[:12], 5)},
            )
            self.assertEqual(len(blobs), 1)
            self.assertTrue(str(blobs[0].path).endswith("NOTES.md"))

    def git(self, repo: Path, *args: str, env: dict[str, str] | None = None) -> None:
        subprocess.run(
            ["git", *args],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )

    def commit(self, repo: Path, message: str, email: str) -> None:
        env = os.environ.copy()
        env.update(
            {
                "GIT_AUTHOR_NAME": "Public Safety",
                "GIT_AUTHOR_EMAIL": email,
                "GIT_COMMITTER_NAME": "Public Safety",
                "GIT_COMMITTER_EMAIL": email,
            }
        )
        self.git(repo, "commit", "-m", message, env=env)

    def rev_parse(self, repo: Path, ref: str) -> str:
        result = subprocess.run(
            ["git", "rev-parse", ref],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()


if __name__ == "__main__":
    unittest.main()
