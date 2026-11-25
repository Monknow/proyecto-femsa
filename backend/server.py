"""Single-container entrypoint: serves the React build and mounts the API under /api."""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from main import app as api_app

STATIC_DIR = Path(os.getenv("STATIC_DIR", Path(__file__).parent / "static")).resolve()

# Reuse the API lifespan (DB table creation) since mounted sub-apps don't run theirs.
app = FastAPI(lifespan=api_app.router.lifespan_context, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/api", api_app)

if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        candidate = (STATIC_DIR / full_path).resolve()
        if full_path and candidate.is_file() and STATIC_DIR in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html")
