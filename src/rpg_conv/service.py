from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3
import re

from rpg_conv.database import connect, initialize_database, load_packaged_reference
from rpg_conv.normalize import normalize_marker

_GENE_LIKE_SYMBOL = re.compile(r"^[A-Za-z0-9]{3,}$")


@dataclass(frozen=True)
class ResolutionResult:
    query: str
    normalized_query: str
    gene_symbol: str | None
    matched_alias: str | None
    source: str | None


class GeneResolver:
    def __init__(self, db_path: str | Path | None = None, *, auto_seed: bool = True):
        self._conn = connect(Path(db_path) if db_path else None)
        initialize_database(self._conn)
        if auto_seed:
            load_packaged_reference(self._conn)

    def close(self) -> None:
        self._conn.close()

    def add_alias(self, gene_symbol: str, alias: str, source: str = "custom") -> None:
        self._conn.execute(
            """
            INSERT INTO gene_alias(gene_symbol, alias_raw, alias_norm, source)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(gene_symbol, alias_norm) DO UPDATE SET
                alias_raw = excluded.alias_raw,
                source = excluded.source
            """,
            (gene_symbol.upper(), alias, normalize_marker(alias), source),
        )
        self._conn.commit()

    def resolve(self, marker: str) -> ResolutionResult:
        norm = normalize_marker(marker)
        row = self._conn.execute(
            """
            SELECT gene_symbol, alias_raw, source
            FROM gene_alias
            WHERE alias_norm = ?
            ORDER BY
                CASE source
                    WHEN 'ground_truth' THEN 0
                    WHEN 'curated' THEN 1
                    WHEN 'seed' THEN 2
                    ELSE 3
                END
            LIMIT 1
            """,
            (norm,),
        ).fetchone()

        if row is None:
            # Fallback: if input looks like a canonical symbol (e.g., PDCD1),
            # return the uppercase symbol even if not explicitly seeded.
            candidate = marker.strip()
            if _GENE_LIKE_SYMBOL.match(candidate):
                return ResolutionResult(
                    query=marker,
                    normalized_query=norm,
                    gene_symbol=candidate.upper(),
                    matched_alias=None,
                    source="fallback:symbol",
                )
            return ResolutionResult(
                query=marker,
                normalized_query=norm,
                gene_symbol=None,
                matched_alias=None,
                source=None,
            )

        return ResolutionResult(
            query=marker,
            normalized_query=norm,
            gene_symbol=row[0],
            matched_alias=row[1],
            source=row[2],
        )

    def resolve_one(self, marker: str) -> str | None:
        return self.resolve(marker).gene_symbol

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn
