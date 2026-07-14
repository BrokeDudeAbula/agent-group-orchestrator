"""公开安全扫描器测试。"""

from __future__ import annotations

from pathlib import Path
import unittest

from scripts.check_public_safety import scan_text


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


if __name__ == "__main__":
    unittest.main()
