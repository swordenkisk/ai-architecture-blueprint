"""Command-line interface for the architecture blueprint tool."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from aibp.engine import assess_spec, render_markdown, validate_spec


def load_spec(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise ValueError(f"Input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON at line {exc.lineno}: {exc.msg}") from exc

    if not isinstance(data, dict):
        raise ValueError("The JSON root must be an object.")
    return data


def command_validate(args: argparse.Namespace) -> int:
    try:
        spec = load_spec(args.input)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    errors = validate_spec(spec)
    if errors:
        print("Specification is invalid:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Specification structure is valid.")
    return 0


def command_build(args: argparse.Namespace) -> int:
    try:
        spec = load_spec(args.input)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    assessment = assess_spec(spec)
    output_dir: Path = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / "architecture-report.md"
    assessment_path = output_dir / "assessment.json"

    report_path.write_text(
        render_markdown(spec, assessment),
        encoding="utf-8",
    )
    assessment_path.write_text(
        json.dumps(assessment, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Report written to: {report_path}")
    print(f"Assessment written to: {assessment_path}")

    if assessment["errors"]:
        print("The specification has structural errors.")
        return 1

    if assessment["warnings"]:
        print(f"Review complete with {len(assessment['warnings'])} warning(s).")
    else:
        print("Review complete with no warnings.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aibp",
        description="Validate and report on a nine-layer AI system architecture.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Check the architecture JSON structure.",
    )
    validate_parser.add_argument("input", type=Path, help="Path to architecture JSON.")
    validate_parser.set_defaults(func=command_validate)

    build_parser = subparsers.add_parser(
        "build",
        help="Generate a Markdown review and JSON assessment.",
    )
    build_parser.add_argument("input", type=Path, help="Path to architecture JSON.")
    build_parser.add_argument(
        "--output",
        type=Path,
        default=Path("build"),
        help="Output directory (default: build).",
    )
    build_parser.set_defaults(func=command_build)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
