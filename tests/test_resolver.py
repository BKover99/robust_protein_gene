from rpg_conv import GeneResolver


def _resolver(tmp_path):
    return GeneResolver(db_path=tmp_path / "test.sqlite3", auto_seed=True)


def test_ki67_variants_resolve_to_mki67(tmp_path):
    resolver = _resolver(tmp_path)
    try:
        assert resolver.resolve_one("ki--67") == "MKI67"
        assert resolver.resolve_one("ki67") == "MKI67"
        assert resolver.resolve_one("KI-67") == "MKI67"
        assert resolver.resolve_one("Ki 67") == "MKI67"
    finally:
        resolver.close()


def test_sma_resolves_to_acta2(tmp_path):
    resolver = _resolver(tmp_path)
    try:
        assert resolver.resolve_one("SMA") == "ACTA2"
        assert resolver.resolve_one("a-sma") == "ACTA2"
    finally:
        resolver.close()


def test_cd57_resolves_to_b3gat1(tmp_path):
    resolver = _resolver(tmp_path)
    try:
        assert resolver.resolve_one("CD57") == "B3GAT1"
    finally:
        resolver.close()


def test_unknown_marker_returns_none(tmp_path):
    resolver = _resolver(tmp_path)
    try:
        assert resolver.resolve_one("definitely-not-a-real-marker") is None
    finally:
        resolver.close()


def test_canonical_symbol_fallback_returns_uppercase_symbol(tmp_path):
    resolver = _resolver(tmp_path)
    try:
        assert resolver.resolve_one("PDCD1") == "PDCD1"
        assert resolver.resolve_one("pdcd1") == "PDCD1"
    finally:
        resolver.close()
