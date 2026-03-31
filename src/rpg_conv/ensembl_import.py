from __future__ import annotations

from typing import Iterable
import sqlite3

from rpg_conv.database import upsert_alias


def _iter_rows(df) -> Iterable[tuple[str, str]]:
    for _, row in df.iterrows():
        symbol = str(row["external_gene_name"]).strip()
        synonym = str(row["external_synonym"]).strip()
        if not symbol or symbol.lower() == "nan":
            continue
        if not synonym or synonym.lower() == "nan":
            continue
        yield symbol, synonym


def bootstrap_from_ensembl(conn: sqlite3.Connection, species: str = "human") -> int:
    """
    Import aliases from Ensembl via pybiomart.

    species: "human" -> hsapiens_gene_ensembl
             "mouse" -> mmusculus_gene_ensembl
    """
    from pybiomart import Dataset  # optional dependency

    dataset_name = {
        "human": "hsapiens_gene_ensembl",
        "mouse": "mmusculus_gene_ensembl",
    }.get(species.lower())
    if dataset_name is None:
        raise ValueError("species must be either 'human' or 'mouse'")

    dataset = Dataset(name=dataset_name, host="http://www.ensembl.org")
    df = dataset.query(attributes=["external_gene_name", "external_synonym"])

    n = 0
    for symbol, synonym in _iter_rows(df):
        upsert_alias(
            conn,
            gene_symbol=symbol,
            alias_raw=synonym,
            source=f"ensembl:{species.lower()}",
        )
        n += 1
    conn.commit()
    return n

__all__ = ["bootstrap_from_ensembl"]
