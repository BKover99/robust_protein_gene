from __future__ import annotations

import argparse

from rpg_conv.service import GeneResolver


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rpg-conv",
        description="Resolve protein markers to canonical gene symbols.",
    )
    parser.add_argument("marker", help="Protein marker alias to resolve.")
    parser.add_argument(
        "--only-return-confident",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="If true, only exact or Levenshtein-confident matches are returned.",
    )
    parser.add_argument(
        "--confidence-distance-lt",
        type=int,
        default=1,
        help="Strict confidence threshold for Levenshtein distance (default: <1).",
    )
    parser.add_argument(
        "--return-ensembl-id",
        action="store_true",
        help="Return Ensembl IDs instead of gene symbols.",
    )
    parser.add_argument(
        "--return-top",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Return only top hit (default true). If false, return all tied hits.",
    )
    parser.add_argument(
        "--sep",
        default=";",
        help="Separator for multi-hit scalar output.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print extra warnings for ambiguous/low-confidence cases.",
    )
    parser.add_argument(
        "--return-df",
        action="store_true",
        help="Return tabular rows with ensembl_id, gene_symbol, alias.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    resolver = GeneResolver()
    try:
        if args.return_df:
            df = resolver.resolve_df(
                args.marker,
                only_return_confident=args.only_return_confident,
                confidence_distance_lt=args.confidence_distance_lt,
                return_top=args.return_top,
                verbose=args.verbose,
            )
            if df.empty:
                print("NA")
            else:
                print(df.to_csv(index=False).strip())
            return
        result = resolver.resolve_value(
            args.marker,
            only_return_confident=args.only_return_confident,
            confidence_distance_lt=args.confidence_distance_lt,
            return_ensembl_id=args.return_ensembl_id,
            return_top=args.return_top,
            sep=args.sep,
            verbose=args.verbose,
        )
    finally:
        resolver.close()

    print(result)

__all__ = ["main"]
