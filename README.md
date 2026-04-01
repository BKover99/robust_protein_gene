# rpg_conv

`rpg_conv` resolves protein marker aliases (for example `ki67`, `SMA`, `CD57`) to canonical gene symbols using a local SQLite database populated from a bundled merged Ensembl reference table (human + mouse aliases together).

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

print(resolver.resolve_one("ki67"))    # MKI67
print(resolver.resolve_one("a-sma", return_top=False)) # contains ACTA2 among merged aliases
print(resolver.resolve_one("CD57", return_top=False))  # contains B3GAT1 among merged aliases
print(resolver.resolve_one("PDCD1"))   # PDCD1
```

## CLI

```bash
rpg-conv "ki--67"
rpg-conv "ki--67" --no-only-return-confident
rpg-conv "CD57" --return-ensembl-id
rpg-conv "hox1" --no-return-top --sep "|"
rpg-conv "hox1" --return-df --verbose
```

## Data model

The SQLite database stores one merged alias table with:
- Ensembl gene ID
- canonical gene symbols
- aliases/synonyms
- normalized alias keys used for robust lookup
- bundled Ensembl reference rows loaded on first initialization

## Matching behavior

- Direct normalized DB match is tried first.
- If no direct match, fuzzy search uses `rapidfuzz.distance.Levenshtein`.
- `only_return_confident=True` means only exact or strict fuzzy (`distance < confidence_distance_lt`) matches are accepted.
- If `only_return_confident=False`, worst-case fallback returns the original query string.
