#!/usr/bin/env python3
"""Exercise output paths, failed-build provenance and CI cache boundaries.

The entry-point fixtures use a recording latexmk executable; full TeX/PDF
validation is performed separately by the normal production build.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="book-build-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repository"
        (self.repo / "scripts").mkdir(parents=True)
        (self.repo / "book").mkdir()
        shutil.copyfile(ROOT / "scripts/build_book.sh", self.repo / "scripts/build_book.sh")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        fake = self.bin / "latexmk"
        fake.write_text(f"#!{sys.executable}\n" + '''import json, os, sys
from pathlib import Path
record = Path(os.environ["LATEXMK_RECORD"])
record.write_text(json.dumps({"args": sys.argv[1:], "cwd": os.getcwd(),
                              "sha": os.environ.get("BOOK_BUILD_SHA")}))
sys.exit(int(os.environ.get("LATEXMK_EXIT", "0")))
''')
        fake.chmod(0o755)
        self.record = self.root / "latexmk.json"
        self.env = dict(os.environ)
        for key in ("BOOK_BUILD_DIR", "BOOK_BUILD_SHA", "GITHUB_SHA", "LATEXMK_EXIT"):
            self.env.pop(key, None)
        self.env.update(PATH=f"{self.bin}{os.pathsep}{os.environ['PATH']}",
                        BOOK_BUILD_SHA="1" * 40, LATEXMK_RECORD=str(self.record))

    def build(self, *args, **environment):
        return subprocess.run(["bash", str(self.repo / "scripts/build_book.sh"), *args],
                              env=self.env | environment, cwd=self.root,
                              capture_output=True, text=True)

    def invocation(self):
        return json.loads(self.record.read_text())

    def test_default_directory_and_incremental_revision(self):
        self.assertEqual(self.build().returncode, 0)
        output = self.repo / "book/build"
        self.assertIn(f"-outdir={output}", self.invocation()["args"])
        self.assertEqual(self.invocation()["cwd"], str(self.repo / "book"))
        self.assertIn("-g", self.invocation()["args"])
        self.assertEqual((output / ".source-revision").read_text().strip(), "1" * 40)
        self.assertEqual(self.build().returncode, 0)
        self.assertNotIn("-g", self.invocation()["args"])
        self.assertEqual(self.build(BOOK_BUILD_SHA="2" * 40).returncode, 0)
        self.assertIn("-g", self.invocation()["args"])
        self.assertEqual(self.invocation()["sha"], "2" * 40)

    def test_relative_output_with_spaces_is_relative_to_repository(self):
        self.assertEqual(self.build(BOOK_BUILD_DIR="scratch with spaces/book").returncode, 0)
        output = self.repo / "scratch with spaces/book"
        self.assertIn(f"-outdir={output}", self.invocation()["args"])
        self.assertTrue((output / ".source-revision").is_file())
        self.assertFalse((self.repo / "book/build/.source-revision").exists())

    def test_absolute_external_output_and_failed_revision_retry(self):
        output = self.root / "external build"
        self.assertEqual(self.build(BOOK_BUILD_DIR=str(output)).returncode, 0)
        failed = self.build(BOOK_BUILD_DIR=str(output), BOOK_BUILD_SHA="2" * 40,
                            LATEXMK_EXIT="7")
        self.assertEqual(failed.returncode, 7)
        self.assertEqual((output / ".source-revision").read_text().strip(), "1" * 40)
        self.assertEqual(self.build(BOOK_BUILD_DIR=str(output), BOOK_BUILD_SHA="2" * 40).returncode, 0)
        self.assertIn("-g", self.invocation()["args"])
        self.assertEqual((output / ".source-revision").read_text().strip(), "2" * 40)

    def test_reject_invalid_revision_and_conflicting_output_option(self):
        self.assertNotEqual(self.build(BOOK_BUILD_SHA="not-a-commit").returncode, 0)
        self.assertFalse(self.record.exists())
        for arg in ("-outdir=elsewhere", "-output-directory=elsewhere"):
            self.assertNotEqual(self.build(arg).returncode, 0)
            self.assertFalse(self.record.exists())


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="book-cache-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.cache = self.root / "cached auxiliary"
        self.build = self.root / "build"
        self.restored = self.root / "restored"
        self.build.mkdir()
        self.environment = "a" * 64

    def cache_action(self, action, build=None, environment=None):
        return subprocess.run(["bash", str(ROOT / "scripts/book_build_cache.sh"), action,
                               str(self.cache), str(build or self.build),
                               environment or self.environment], capture_output=True, text=True)

    def test_restores_auxiliary_data_but_never_pdf_log_or_up_to_date_state(self):
        files = ("main.aux", "main.toc", "main-luamml-mathml.html", "smoke/smoke-tagging.aux")
        for name in files + ("main.pdf", "main.log", "main.fdb_latexmk", ".source-revision"):
            path = self.build / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(name)
        self.assertEqual(self.cache_action("save").returncode, 0)
        for name in files:
            self.assertEqual((self.cache / name).read_text(), name)
        for name in ("main.pdf", "main.log", "main.fdb_latexmk", ".source-revision"):
            self.assertFalse((self.cache / name).exists())
            # Even an extraneous cache entry must not be restored.
            (self.cache / name).write_text("stale output")
        self.assertEqual(self.cache_action("restore", self.restored).returncode, 0)
        restored_files = {str(p.relative_to(self.restored))
                          for p in self.restored.rglob("*") if p.is_file()}
        self.assertEqual(restored_files, set(files))

    def test_missing_or_incompatible_environment_is_a_cold_build(self):
        self.assertEqual(self.cache_action("restore", self.restored).returncode, 0)
        self.assertFalse(self.restored.exists())
        (self.build / "main.aux").write_text("previous environment")
        self.assertEqual(self.cache_action("save").returncode, 0)
        self.assertEqual(self.cache_action("restore", self.restored, "b" * 64).returncode, 0)
        self.assertFalse(self.restored.exists())

    def test_save_removes_disappeared_auxiliary_files(self):
        (self.build / "main.toc").write_text("old contents")
        self.assertEqual(self.cache_action("save").returncode, 0)
        (self.build / "main.toc").unlink()
        self.assertEqual(self.cache_action("save").returncode, 0)
        self.assertFalse((self.cache / "main.toc").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
