from collections.abc import Iterable


def core_seed_rows() -> Iterable[tuple[str, str]]:
    """
    Curated ground-truth aliases to canonical genes.

    This is intentionally small and high-confidence. Users can extend with
    project-specific data or Ensembl ingestion.
    """
    return [
        ("MKI67", "MKI67"),
        ("MKI67", "KI67"),
        ("MKI67", "KI-67"),
        ("MKI67", "KI 67"),
        ("MKI67", "KI--67"),
        ("ACTA2", "ACTA2"),
        ("ACTA2", "SMA"),
        ("ACTA2", "A-SMA"),
        ("ACTA2", "ALPHA-SMA"),
        ("B3GAT1", "B3GAT1"),
        ("B3GAT1", "CD57"),
        ("B3GAT1", "HNK-1"),
    ]
