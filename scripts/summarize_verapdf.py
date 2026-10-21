#!/usr/bin/env python3
"""Summarize independent veraPDF machine-verifiable PDF/UA reports.

Advisory means failing PDF/UA checks don't fail the release workflow.
Do not confuse this machine report with human PDF/UA/assistive-tech review.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("report", type=Path)
    ap.add_argument("--advisory", action="store_true",
                    help="Report failures without blocking the release build")
    args = ap.parse_args()
    if not args.report.is_file() or args.report.stat().st_size == 0:
        print(f"veraPDF report missing or empty: {args.report}", file=sys.stderr)
        return 2
    try:
        root = ET.parse(args.report).getroot()
    except ET.ParseError as exc:
        print(f"Invalid veraPDF XML report: {exc}", file=sys.stderr)
        return 2

    reports = [n for n in root.iter() if local_name(n.tag) == "validationReport"]
    if len(reports) != 1:
        print(f"Expected one veraPDF validationReport, found {len(reports)}",
              file=sys.stderr)
        return 2
    report = reports[0]
    compliant = report.get("isCompliant")
    details = next((n for n in report if local_name(n.tag) == "details"), None)
    if compliant not in ("true", "false") or details is None:
        print("veraPDF report missing compliance or details fields",
              file=sys.stderr)
        return 2

    rules = [n for n in details if local_name(n.tag) == "rule"
             and n.get("status") == "failed"]
    summary = Counter()
    for rule in rules:
        key = (rule.get("specification", ""),
               rule.get("clause", ""),
               rule.get("testNumber", ""))
        summary[key] += int(rule.get("failedChecks", "0"))
    print(f"veraPDF PDF/UA-2: compliant={compliant}, "
          f"failedRules={details.get('failedRules','?')}, "
          f"failedChecks={details.get('failedChecks','?')}")
    for (spec, clause, test), failures in summary.most_common(15):
        print(f"  {spec} | clause {clause} test {test}: {failures} failures")
    if compliant == "false" and args.advisory:
        print("ADVISORY: PDF/UA-2 compliance is not yet established.")
        return 0
    return 0 if compliant == "true" else 1


if __name__ == "__main__":
    raise SystemExit(main())
