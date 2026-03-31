# robust-protein-gene

`robust-protein-gene` resolves protein marker aliases (for example `ki--67`, `SMA`, `CD57`) to canonical gene symbols using a local SQLite database.

## Install

```bash
pip install robust-protein-gene
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from robust_protein_gene import GeneResolver

resolver = GeneResolver()  # creates/loads a local SQLite DB in ~/.robust_protein_gene

print(resolver.resolve_one("ki--67"))  # MKI67
print(resolver.resolve_one("ki67"))    # MKI67
print(resolver.resolve_one("SMA"))     # ACTA2
print(resolver.resolve_one("CD57"))    # B3GAT1
```

## CLI

```bash
robust-protein-gene "ki--67"
```

## Data model

The SQLite database stores:
- canonical gene symbols
- aliases/synonyms
- normalized alias keys used for robust lookup

## Optional Ensembl bootstrap

If you want to enrich synonyms from Ensembl:

```bash
pip install "robust-protein-gene[ensembl]"
```

Then use `robust_protein_gene.ensembl_import.bootstrap_from_ensembl(...)` in your own workflow.
