def test_parse_pdf():
    from app.ingestion.pdf_parser import parse_pdf
    assert "Dummy PDF" in parse_pdf("file.pdf")
