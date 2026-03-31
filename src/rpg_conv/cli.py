from __future__ import annotations

import argparse

from rpg_conv.service import GeneResolver


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rpg-conv",
        description="Resolve protein markers to canonical gene symbols.",
    )
    parser.add_argument("marker", help="Protein marker alias to resolve.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    resolver = GeneResolver()
    try:
        result = resolver.resolve(args.marker)
    finally:
        resolver.close()

    if result.gene_symbol:
        print(result.gene_symbol)
    else:
        print("NOT_FOUND")

__all__ = ["main"]
