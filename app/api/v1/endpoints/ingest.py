
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.api.v1.schemas import URLIn, URLContentOut, PDFUploadOut
from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.web_scraper import scrape_url
import tempfile

router = APIRouter(prefix="/ingest", tags=["ingestion"])

@router.post("/url", response_model=URLContentOut)
async def ingest_url(payload: URLIn):
    try:
        result = scrape_url(payload.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pdf", response_model=PDFUploadOut)
async def ingest_pdf(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            text = parse_pdf(tmp.name)
        return {"filename": file.filename, "content": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

