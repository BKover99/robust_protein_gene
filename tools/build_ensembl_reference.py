from __future__ import annotations

from pathlib import Path

import pandas as pd
from pybiomart import Dataset


def fetch_human() -> pd.DataFrame:
    dataset = Dataset(name="hsapiens_gene_ensembl", host="http://www.ensembl.org")
    df = dataset.query(
        attributes=["ensembl_gene_id", "external_gene_name", "external_synonym"]
    )
    df.columns = ["ensembl_id", "gene_symbol", "alias"]
    return df


def fetch_mouse() -> pd.DataFrame:
    dataset = Dataset(name="mmusculus_gene_ensembl", host="http://www.ensembl.org")
    df = dataset.query(
        attributes=["ensembl_gene_id", "mgi_symbol", "external_synonym"]
    )
    df.columns = ["ensembl_id", "gene_symbol", "alias"]
    return df


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(subset=["gene_symbol"])
    df["ensembl_id"] = df["ensembl_id"].astype(str).str.strip()
    df["gene_symbol"] = df["gene_symbol"].astype(str).str.strip().str.upper()
    df["alias"] = df["alias"].fillna("").astype(str).str.strip()
    return df[df["gene_symbol"] != ""]


def _with_self_aliases(df: pd.DataFrame) -> pd.DataFrame:
    synonyms = df[df["alias"] != ""]
    self_aliases = (
        df[["ensembl_id", "gene_symbol"]]
        .drop_duplicates()
        .assign(alias=lambda d: d["gene_symbol"])
    )
    return pd.concat(
        [synonyms[["ensembl_id", "gene_symbol", "alias"]], self_aliases],
        ignore_index=True,
    )


def build_reference() -> pd.DataFrame:
    human = _with_self_aliases(_clean(fetch_human()))
    mouse = _with_self_aliases(_clean(fetch_mouse()))
    out = pd.concat([human, mouse], ignore_index=True)
    out["alias_norm"] = out["alias"].str.lower().str.replace(r"[^a-z0-9]+", "", regex=True)
    out = out[out["alias_norm"] != ""]
    out = out.drop_duplicates(subset=["ensembl_id", "gene_symbol", "alias_norm"]).reset_index(drop=True)
    out["source"] = "ensembl:reference"
    return out


if __name__ == "__main__":
    output = Path("src/rpg_conv/data/ensembl_reference.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    df = build_reference()
    df.to_csv(output, index=False)
    print(f"Wrote {len(df)} rows to {output}")
