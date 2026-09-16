"""检查分发包入口与实际文件，防止再次发布缺失引用的 Skill。"""

import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]


class SkillPackageTests(unittest.TestCase):
    def test_skill_metadata_and_invocation(self):
        content = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        sections = content.split("---", 2)
        self.assertEqual(sections[0].strip(), "")
        self.assertEqual(len(sections), 3)
        metadata = yaml.safe_load(sections[1])
        self.assertRegex(metadata["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertTrue(metadata["description"].strip())
        self.assertTrue(sections[2].strip())
        interface = yaml.safe_load(
            (ROOT / "agents/openai.yaml").read_text(encoding="utf-8")
        )["interface"]
        self.assertIn("$" + metadata["name"], interface["default_prompt"])

    def test_published_markdown_links_resolve(self):
        documents = [ROOT / "README.md", ROOT / "SKILL.md"]
        for folder in ("references", "examples"):
            documents.extend((ROOT / folder).rglob("*.md"))
        for document in documents:
            content = document.read_text(encoding="utf-8")
            # 只校验实际 Markdown 链接；提示词中的示例路径不是包内依赖。
            for target in re.findall(r"!?\[[^\]]*\]\(([^\s)]+)\)", content):
                parts = urlsplit(target)
                if parts.scheme or parts.netloc or not parts.path:
                    continue
                with self.subTest(document=document.name, target=target):
                    resolved = (document.parent / unquote(parts.path)).resolve()
                    self.assertTrue(resolved.is_relative_to(ROOT))
                    self.assertTrue(resolved.exists(), f"缺少引用文件：{target}")


if __name__ == "__main__":
    unittest.main()
