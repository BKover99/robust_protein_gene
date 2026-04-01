from rpg_conv import GeneResolver


def _resolver(tmp_path):
    return GeneResolver(db_path=tmp_path / "test.sqlite3", auto_seed=True)


def test_direct_matches_from_reference(tmp_path):
    resolver = _resolver(tmp_path)
    try:
        assert resolver.resolve_one("ki67") == "MKI67"
        sma_all = resolver.resolve_one("a-sma", return_top=False)
        cd57_all = resolver.resolve_one("CD57", return_top=False)
        assert "ACTA2" in sma_all.split(";")
        assert "B3GAT1" in cd57_all.split(";")
        assert resolver.resolve_one("PDCD1") == "PDCD1"
    finally:
        resolver.close()


def test_only_return_confident_true_returns_na_when_not_exact(tmp_path):
    resolver = _resolver(tmp_path)
    try:
        assert resolver.resolve_one("ki--67", only_return_confident=True) == "MKI67"
        assert resolver.resolve_one("ki6", only_return_confident=True) == "NA"
        assert resolver.resolve_one("definitely-not-a-real-marker", only_return_confident=True) == "NA"
    finally:
        resolver.close()


def test_only_return_confident_false_falls_back_to_query(tmp_path):
    resolver = _resolver(tmp_path)
    try:
        assert (
            resolver.resolve_one("definitely-not-a-real-marker", only_return_confident=False)
            == "definitely-not-a-real-marker"
        )
        df = resolver.resolve_df(
            "definitely-not-a-real-marker", only_return_confident=False
        )
        assert df.shape[0] == 1
        assert df.iloc[0]["alias"] == "definitely-not-a-real-marker"
        assert df.iloc[0]["gene_symbol"] == "NA"
        assert df.iloc[0]["ensembl_id"] == "NA"
    finally:
        resolver.close()


def test_return_ensembl_and_df_shapes(tmp_path):
    resolver = _resolver(tmp_path)
    try:
        assert resolver.resolve_one("CD57", return_ensembl_id=True).startswith("ENSG")
        df_top = resolver.resolve_df("CD57", return_top=True)
        assert list(df_top.columns) == ["ensembl_id", "gene_symbol", "alias"]
        assert df_top.shape[0] == 1
    finally:
        resolver.close()


def test_return_all_hits_separator(tmp_path):
    resolver = _resolver(tmp_path)
    try:
        out = resolver.resolve_one(
            "hox1", return_top=False, sep="|", only_return_confident=False
        )
        assert "|" in out
    finally:
        resolver.close()
