#!/usr/bin/env python3
"""Validate GitHub Actions YAML plus invariants that prevent accidental releases.

PyYAML BaseLoader preserves the literal YAML key 'on', unlike YAML 1.1 SafeLoader.
"""
from __future__ import annotations

from pathlib import Path
import re
import sys

import yaml


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
SHA_ACTION = re.compile(r"^[\w-]+(?:/[\w.-]+)+@[a-f0-9]{40}$")


def check(name: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(name)


def main() -> None:
    data = {}
    for path in sorted(WORKFLOWS.glob("*.yml")):
        loaded = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        check(f"{path.name}: top-level mapping", isinstance(loaded, dict))
        check(f"{path.name}: jobs", isinstance(loaded.get("jobs"), dict))
        check(f"{path.name}: 'on' declaration", isinstance(loaded.get("on"), dict))
        for job in loaded["jobs"].values():
            for step in job.get("steps", []):
                if "uses" in step:
                    check(f"{path.name}: pin action by immutable SHA: {step['uses']}",
                          bool(SHA_ACTION.fullmatch(step["uses"])))
        data[path.name] = loaded
    check("required workflows", {"build-latex.yml", "check-docs.yml",
          "check-compatibility.yml", "publish-release.yml"} <= data.keys())
    build = data["build-latex.yml"]
    steps = build["jobs"]["build-book"]["steps"]
    uploads = [step for step in steps if (step.get("uses") or "").startswith("actions/upload-artifact@")]
    artifact_names = [step["with"]["name"] for step in uploads]
    check("only one successful PDF artifact", artifact_names.count("ai-by-intuition-volume-01") == 1)
    check("one machine audit", artifact_names.count("pdfua2-machine-audit") == 1)
    check("failure-only diagnostics",
          any(s.get("with", {}).get("name") == "failed-build-diagnostics"
              and s.get("if") == "failure()" for s in uploads))
    check("no legacy experimental uploads",
          not {"experimental-heading-results", "experimental-mathml-logs",
               "tagged-pdf-diagnostics"} & set(artifact_names))
    text = (WORKFLOWS / "build-latex.yml").read_text()
    check("no historical experiments in release-critical build",
          "smoke-mathml.tex" not in text and "smoke-heading-" not in text)
    for required in ("Verify associated MathML", "Validate PDF/UA-2",
                     "Verify rendered PDF tags"):
        check(f"required gate: {required}", any(required in s.get("name", "") for s in steps))
    compat = data["check-compatibility.yml"]
    check("diagnostic workflow only manually triggered", list(compat["on"]) == ["workflow_dispatch"])
    release = data["publish-release.yml"]
    check("release workflow only manually triggered", list(release["on"]) == ["workflow_dispatch"])
    check("release job main guard", release["jobs"]["release"].get("if") ==
          "github.ref == 'refs/heads/main'")
    source = (WORKFLOWS / "publish-release.yml").read_text()
    for marker in ("gh release create", "head_repository.full_name",
                   'git merge-base --is-ancestor', "SHA256SUMS",
                   "build-audit.zip", "failedRules"):
        check(f"release provenance: {marker}", marker in source)
    print(f"Workflow QA passed: {len(data)} YAML workflows and release invariants")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, yaml.YAMLError) as exc:
        print(f"Workflow QA FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
