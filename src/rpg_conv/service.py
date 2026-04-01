from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
from typing import Any

import pandas as pd
from rapidfuzz.distance import Levenshtein
from rpg_conv.database import connect, initialize_database, load_packaged_reference
from rpg_conv.normalize import normalize_marker


@dataclass(frozen=True)
class MatchRow:
    ensembl_id: str | None
    gene_symbol: str | None
    alias: str
    distance: int
    source: str | None


@dataclass(frozen=True)
class ResolutionResult:
    query: str
    normalized_query: str
    hits: list[MatchRow]
    warning: str | None = None


class GeneResolver:
    def __init__(self, db_path: str | Path | None = None, *, auto_seed: bool = True):
        self._conn = connect(Path(db_path) if db_path else None)
        initialize_database(self._conn)
        if auto_seed:
            load_packaged_reference(self._conn)

    def close(self) -> None:
        self._conn.close()

    def _direct_matches(self, norm: str) -> list[MatchRow]:
        rows = self._conn.execute(
            """
            SELECT ensembl_id, gene_symbol, alias_raw, source
            FROM gene_alias
            WHERE alias_norm = ?
            ORDER BY gene_symbol ASC, alias_raw ASC
            """,
            (norm,),
        ).fetchall()
        return [
            MatchRow(
                ensembl_id=row[0],
                gene_symbol=row[1],
                alias=row[2],
                distance=0,
                source=row[3],
            )
            for row in rows
        ]

    def _fuzzy_best_matches(self, norm: str) -> tuple[list[MatchRow], int | None]:
        candidates = self._conn.execute(
            """
            SELECT ensembl_id, gene_symbol, alias_raw, alias_norm, source
            FROM gene_alias
            """
        ).fetchall()
        if not candidates:
            return [], None

        best_distance: int | None = None
        best_rows: list[MatchRow] = []
        for ensembl_id, gene_symbol, alias_raw, alias_norm, source in candidates:
            d = Levenshtein.distance(norm, alias_norm)
            if best_distance is None or d < best_distance:
                best_distance = d
                best_rows = [
                    MatchRow(
                        ensembl_id=ensembl_id,
                        gene_symbol=gene_symbol,
                        alias=alias_raw,
                        distance=d,
                        source=source,
                    )
                ]
            elif d == best_distance:
                best_rows.append(
                    MatchRow(
                        ensembl_id=ensembl_id,
                        gene_symbol=gene_symbol,
                        alias=alias_raw,
                        distance=d,
                        source=source,
                    )
                )
        best_rows.sort(key=lambda r: ((r.gene_symbol or ""), r.alias))
        return best_rows, best_distance

    def resolve(
        self,
        marker: str,
        *,
        only_return_confident: bool = True,
        confidence_distance_lt: int = 1,
        return_top: bool = True,
        verbose: bool = False,
    ) -> ResolutionResult:
        norm = normalize_marker(marker)

        direct = self._direct_matches(norm)
        warning: str | None = None
        hits: list[MatchRow]
        if direct:
            hits = direct
            if return_top:
                hits = hits[:1]
            if len(direct) > 1:
                warning = f"Ambiguous direct match ({len(direct)} hits) for '{marker}'."
        else:
            fuzzy_hits, best_distance = self._fuzzy_best_matches(norm)
            fuzzy_hits = fuzzy_hits or []
            is_confident_fuzzy = (
                best_distance is not None and best_distance < confidence_distance_lt
            )
            if is_confident_fuzzy:
                hits = fuzzy_hits[:1] if return_top else fuzzy_hits
                if len(fuzzy_hits) > 1:
                    warning = (
                        f"Ambiguous fuzzy match ({len(fuzzy_hits)} hits) at distance "
                        f"{best_distance} for '{marker}'."
                    )
            elif only_return_confident:
                hits = []
                warning = (
                    f"No confident match for '{marker}' (best distance: {best_distance})."
                )
            else:
                hits = [
                    MatchRow(
                        ensembl_id=None,
                        gene_symbol=None,
                        alias=marker,
                        distance=best_distance if best_distance is not None else 999,
                        source="fallback:query",
                    )
                ]
                warning = (
                    f"No confident match for '{marker}'. Returning query as fallback alias."
                )

        if verbose and warning:
            print(f"[rpg_conv warning] {warning}")

        return ResolutionResult(
            query=marker,
            normalized_query=norm,
            hits=hits,
            warning=warning,
        )

    def resolve_value(
        self,
        marker: str,
        *,
        only_return_confident: bool = True,
        confidence_distance_lt: int = 1,
        return_ensembl_id: bool = False,
        return_top: bool = True,
        sep: str = ";",
        verbose: bool = False,
    ) -> str:
        result = self.resolve(
            marker,
            only_return_confident=only_return_confident,
            confidence_distance_lt=confidence_distance_lt,
            return_top=return_top,
            verbose=verbose,
        )
        if not result.hits:
            return "NA"

        if return_top:
            hit = result.hits[0]
            if return_ensembl_id:
                return hit.ensembl_id or "NA"
            if hit.source == "fallback:query":
                return hit.alias
            return hit.gene_symbol or "NA"

        if return_ensembl_id:
            values = [hit.ensembl_id or "NA" for hit in result.hits]
        else:
            values = [
                hit.alias if hit.source == "fallback:query" else (hit.gene_symbol or "NA")
                for hit in result.hits
            ]
        return sep.join(values)

    def resolve_df(
        self,
        marker: str,
        *,
        only_return_confident: bool = True,
        confidence_distance_lt: int = 1,
        return_top: bool = True,
        verbose: bool = False,
    ) -> pd.DataFrame:
        result = self.resolve(
            marker,
            only_return_confident=only_return_confident,
            confidence_distance_lt=confidence_distance_lt,
            return_top=return_top,
            verbose=verbose,
        )
        rows: list[dict[str, Any]] = []
        for hit in result.hits:
            rows.append(
                {
                    "ensembl_id": hit.ensembl_id if hit.ensembl_id is not None else "NA",
                    "gene_symbol": hit.gene_symbol if hit.gene_symbol is not None else "NA",
                    "alias": hit.alias,
                }
            )
        return pd.DataFrame(rows, columns=["ensembl_id", "gene_symbol", "alias"])

    def resolve_one(self, marker: str, **kwargs: Any) -> str:
        return self.resolve_value(marker, **kwargs)

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn
