def test_query_placeholder():
    from app.api.v1.endpoints.query import query
    class Req: question = "hi"
    res = query(Req())
    assert "answer" in res
