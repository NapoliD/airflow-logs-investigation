"""Checks that the repository stays safe to have in public.

This suite exists because a security review of the public repo had to verify
these by hand. The two that matter most:

* no credential ever reaches a command line (it would land in shell history and
  in the process table, readable by any other user on the host);
* nothing that looks like a live key gets committed.

The patterns are deliberately narrow. A check that cries wolf on every `sk-`
in a docstring gets disabled within a week, and then it protects nothing.
"""

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", "assets", ".github"}

# Real key shapes, not the placeholders the docs use to show the format.
SECRET_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "OpenAI-style API key"),
    (re.compile(r"sk-ant-[A-Za-z0-9_\-]{32,}"), "Anthropic-style API key"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWS access key id"),
    (re.compile(r"-----BEGIN (RSA |OPENSSH |EC )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"ghp_[A-Za-z0-9]{36}"), "GitHub personal access token"),
]


def source_files():
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico"}:
            continue
        yield path


class NoCommittedSecrets(unittest.TestCase):

    def test_no_credential_shaped_strings(self):
        for path in source_files():
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for pattern, label in SECRET_PATTERNS:
                with self.subTest(file=path.relative_to(REPO_ROOT), kind=label):
                    self.assertIsNone(pattern.search(text),
                                      f"{label} found in {path.relative_to(REPO_ROOT)}")

    def test_gitignore_covers_the_usual_secret_files(self):
        ignored = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        for entry in (".env", "*.pem", "credentials"):
            self.assertIn(entry, ignored, f".gitignore does not cover {entry}")


class NoCredentialsOnTheCommandLine(unittest.TestCase):

    def test_scripts_do_not_accept_a_password_argument(self):
        """A --password flag is readable in `ps` and in the shell history.

        Credentials belong in an environment variable or an interactive prompt.
        """
        for path in (REPO_ROOT / "scripts").rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(script=path.name):
                self.assertNotIn('"--password"', text,
                                 f"{path.name} defines a --password argument")
                self.assertNotIn("'--password'", text,
                                 f"{path.name} defines a --password argument")


class LicenceIsRealAndMatchesTheReadme(unittest.TestCase):

    def test_licence_file_exists(self):
        licence = REPO_ROOT / "LICENSE"
        self.assertTrue(licence.is_file(), "README claims MIT but there is no LICENSE file")
        self.assertIn("MIT License", licence.read_text(encoding="utf-8"))


class OllamaIsNotPublished(unittest.TestCase):

    def test_ollama_port_is_bound_to_loopback(self):
        """Ollama ships with no authentication; publishing it exposes the host."""
        compose = (REPO_ROOT / "docker-compose.yml").read_text(encoding="utf-8")
        self.assertNotIn('- "11434:11434"', compose,
                         "Ollama is published on every interface")
        self.assertIn('127.0.0.1:11434:11434', compose)


if __name__ == "__main__":
    unittest.main()
