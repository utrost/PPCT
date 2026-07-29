from __future__ import annotations

import argparse
from datetime import date

from .target import TargetConfig, write_svg


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a PPCT A4 SVG calibration target.")
    parser.add_argument("-o", "--output", default="output/ppct-a4.svg", help="SVG output path (default: output/ppct-a4.svg)")
    parser.add_argument("--title", default=TargetConfig.title, help="Title printed in the metadata section")
    parser.add_argument("--operator", default="", help="Operator name printed in the metadata section")
    parser.add_argument("--date", default=date.today().isoformat(), help="Date printed in the metadata section (default: today)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = TargetConfig(title=args.title, operator=args.operator, date=args.date)
    output = write_svg(args.output, config)
    print(f"Wrote PPCT SVG: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
