from ..ingestion import pdf_parser, web_scraper, cleaner
from ..processing.text_splitter import split_text
from .embedding import embed_text
from .vector_store import VectorStore


def ingest_source(source: str, type: str):
    if type == "pdf":
        txt = pdf_parser.parse_pdf(source)
    elif type == "url":
        txt = web_scraper.scrape_url(source)
    else:
        txt = source
    txt = cleaner.clean_text(txt)
    chunks = split_text(txt)
    vectors = embed_text(chunks)
    store = VectorStore()
    store.add(chunks, vectors)
    return store
