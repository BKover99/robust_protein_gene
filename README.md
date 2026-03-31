# rpg_conv

`rpg_conv` resolves protein marker aliases (for example `ki--67`, `SMA`, `CD57`) to canonical gene symbols using a local SQLite database populated from a bundled Ensembl reference table.

## Install

```bash
pip install rpg_conv
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```python
from rpg_conv import GeneResolver

resolver = GeneResolver()  # creates/loads a local SQLite DB in ~/.rpg_conv

print(resolver.resolve_one("ki--67"))  # MKI67
print(resolver.resolve_one("ki67"))    # MKI67
print(resolver.resolve_one("SMA"))     # ACTA2
print(resolver.resolve_one("CD57"))    # B3GAT1
```

## CLI

```bash
rpg-conv "ki--67"
```

## Data model

The SQLite database stores:
- canonical gene symbols
- aliases/synonyms
- normalized alias keys used for robust lookup
- bundled Ensembl reference rows loaded on first initialization
- a tiny ground-truth override table for deterministic aliases (`KI67`, `SMA`, `CD57`, `PDCD1`)

## Optional Ensembl bootstrap

If you want to enrich synonyms from Ensembl:

```bash
pip install "rpg_conv[ensembl]"
```

Then use `rpg_conv.ensembl_import.bootstrap_from_ensembl(...)` in your own workflow.
