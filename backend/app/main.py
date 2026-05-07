from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.query import router as query_router
from app.routes.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.embedder import embed_query
    from app.services.reranker import _get_reranker
    embed_query("warmup")
    _get_reranker()
    yield


app = FastAPI(
    title="MedLens",
    description="Clinical evidence retrieval engine over 30K+ PubMed abstracts",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router, prefix="/api")
app.include_router(health_router, prefix="/api")
