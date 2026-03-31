from __future__ import annotations

import csv
from importlib.resources import files
import sqlite3
from pathlib import Path

from rpg_conv.normalize import normalize_marker


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


def load_packaged_reference(conn: sqlite3.Connection) -> None:
    existing = conn.execute("SELECT COUNT(*) FROM gene_alias").fetchone()[0]
    if existing > 0:
        return

    data_path = files("rpg_conv.data").joinpath("ensembl_reference.csv")
    with data_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                row["gene_symbol"].upper(),
                row["alias"],
                row["alias_norm"] or normalize_marker(row["alias"]),
                row.get("source", "ensembl:reference"),
            )
            for row in reader
        ]

    conn.executemany(
        """
        INSERT INTO gene_alias(gene_symbol, alias_raw, alias_norm, source)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(gene_symbol, alias_norm) DO UPDATE SET
            alias_raw = excluded.alias_raw,
            source = excluded.source
        """,
        rows,
    )

    overrides_path = files("rpg_conv.data").joinpath("ground_truth_overrides.csv")
    with overrides_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        override_rows = [
            (
                row["gene_symbol"].upper(),
                row["alias"],
                row["alias_norm"] or normalize_marker(row["alias"]),
                row.get("source", "ground_truth"),
            )
            for row in reader
        ]
    conn.executemany(
        """
        INSERT INTO gene_alias(gene_symbol, alias_raw, alias_norm, source)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(gene_symbol, alias_norm) DO UPDATE SET
            alias_raw = excluded.alias_raw,
            source = excluded.source
        """,
        override_rows,
    )
    conn.commit()
