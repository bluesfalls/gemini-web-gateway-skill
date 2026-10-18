"""Offline publication and documentation checks; no accounts/network/GUI."""
import hashlib
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/deploy-gemini-web-gateway"
REFERENCE = SKILL / "references/file-tools-and-agents.md"
CONTENT_FILES = (
    ".gitignore", "README.md", "REVIEW.md",
    "skills/deploy-gemini-web-gateway/SKILL.md",
    "skills/deploy-gemini-web-gateway/agents/openai.yaml",
    "skills/deploy-gemini-web-gateway/assets/mac-compose.yaml",
    "skills/deploy-gemini-web-gateway/references/file-tools-and-agents.md",
    "skills/deploy-gemini-web-gateway/references/gui-clients.md",
    "skills/deploy-gemini-web-gateway/references/mac-local.md",
    "skills/deploy-gemini-web-gateway/references/nas-gateway.md",
    "skills/deploy-gemini-web-gateway/references/validation-and-diagnosis.md",
    "skills/deploy-gemini-web-gateway/scripts/build_workbuddy_models.py",
    "tests/test_build_workbuddy_models.py", "tests/test_public_contract.py",
)


class PublicContractTests(unittest.TestCase):
    def test_manifest_matches_explicit_content_allowlist(self):
        lines = (ROOT / "PUBLICATION_MANIFEST.sha256").read_text().splitlines()
        actual = dict(line.split("  ", 1)[::-1] for line in lines)
        self.assertEqual(len(actual), len(lines))
        self.assertEqual(set(actual), set(CONTENT_FILES))
        for name in CONTENT_FILES:
            path = ROOT / name
            self.assertTrue(path.is_file())
            self.assertFalse(path.is_symlink())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), actual[name])

    def test_public_tree_has_no_unlisted_files_or_generated_deployments(self):
        files = {str(p.relative_to(ROOT)) for p in ROOT.rglob("*")
                 if p.is_file() and ".git" not in p.relative_to(ROOT).parts
                 and "__pycache__" not in p.relative_to(ROOT).parts}
        self.assertEqual(files, set(CONTENT_FILES) | {"PUBLICATION_MANIFEST.sha256"})

    def test_all_relative_markdown_links_resolve_inside_public_tree(self):
        for name in CONTENT_FILES:
            if not name.endswith(".md"):
                continue
            path = ROOT / name
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                candidate = (path.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(candidate.is_relative_to(ROOT.resolve()), target)
                self.assertTrue(candidate.is_file(), target)

    def test_all_example_ipv4_addresses_are_loopback_or_wildcard(self):
        for name in CONTENT_FILES:
            addresses = re.findall(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])",
                                   (ROOT / name).read_text())
            self.assertTrue(set(addresses) <= {"127.0.0.1", "0.0.0.0"}, name)



if __name__ == "__main__":
    unittest.main()
