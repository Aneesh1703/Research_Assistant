"""Minimal entrypoint for the scaffolded research assistant app."""
from fastapi import FastAPI
from app.api.v1.endpoints import ingest, query, health

app = FastAPI(title="research_assistant")

app.include_router(health.router, prefix="/api/v1")
app.include_router(ingest.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
