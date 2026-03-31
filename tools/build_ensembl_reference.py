from __future__ import annotations

from pathlib import Path

import pandas as pd
from pybiomart import Dataset


def fetch_species(dataset_name: str) -> pd.DataFrame:
    dataset = Dataset(name=dataset_name, host="https://www.ensembl.org")
    df = dataset.query(
        attributes=["ensembl_gene_id", "external_gene_name", "external_synonym"]
    )
    df.columns = ["ensembl_gene_id", "gene_symbol", "alias"]
    return df


def build_reference() -> pd.DataFrame:
    human = fetch_species("hsapiens_gene_ensembl")
    mouse = fetch_species("mmusculus_gene_ensembl")
    combined = pd.concat([human, mouse], ignore_index=True)

    combined = combined.dropna(subset=["gene_symbol"])
    combined["gene_symbol"] = combined["gene_symbol"].astype(str).str.strip().str.upper()
    combined["alias"] = combined["alias"].astype(str).str.strip()
    combined = combined[combined["gene_symbol"] != ""]

    synonyms = combined[combined["alias"].notna() & (combined["alias"] != "")]
    self_aliases = (
        combined[["ensembl_gene_id", "gene_symbol"]]
        .drop_duplicates()
        .assign(alias=lambda d: d["gene_symbol"])
    )

    out = pd.concat(
        [synonyms[["ensembl_gene_id", "gene_symbol", "alias"]], self_aliases],
        ignore_index=True,
    )
    out["alias_norm"] = out["alias"].str.lower().str.replace(r"[^a-z0-9]+", "", regex=True)
    out = out[out["alias_norm"] != ""]
    out = out.drop_duplicates(subset=["gene_symbol", "alias_norm"]).reset_index(drop=True)
    return out


if __name__ == "__main__":
    output = Path("src/rpg_conv/data/ensembl_reference.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    df = build_reference()
    df.to_csv(output, index=False)
    print(f"Wrote {len(df)} rows to {output}")
