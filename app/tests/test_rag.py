def test_pipeline():
    from app.rag.pipeline import ingest_source
    store = ingest_source("hello world", "text")
    assert store is not None
