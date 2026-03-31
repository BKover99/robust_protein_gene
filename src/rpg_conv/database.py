from __future__ import annotations

import sqlite3
from pathlib import Path

from rpg_conv.normalize import normalize_marker
from rpg_conv.seed_data import core_seed_rows


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS gene_alias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_symbol TEXT NOT NULL,
    alias_raw TEXT NOT NULL,
    alias_norm TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'seed',
    UNIQUE(gene_symbol, alias_norm)
);

CREATE INDEX IF NOT EXISTS idx_gene_alias_alias_norm
ON gene_alias(alias_norm);
"""


def default_db_path() -> Path:
    base = Path.home() / ".rpg_conv"
    base.mkdir(parents=True, exist_ok=True)
    return base / "markers.sqlite3"


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or default_db_path()
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def upsert_alias(
    conn: sqlite3.Connection,
    *,
    gene_symbol: str,
    alias_raw: str,
    source: str = "seed",
) -> None:
    conn.execute(
        """
        INSERT INTO gene_alias(gene_symbol, alias_raw, alias_norm, source)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(gene_symbol, alias_norm) DO UPDATE SET
            alias_raw = excluded.alias_raw,
            source = excluded.source
        """,
        (gene_symbol.upper(), alias_raw, normalize_marker(alias_raw), source),
    )


def seed_core_data(conn: sqlite3.Connection) -> None:
    for gene_symbol, alias in core_seed_rows():
        upsert_alias(conn, gene_symbol=gene_symbol, alias_raw=alias, source="seed")
    conn.commit()
