import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import get_settings

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        settings = get_settings()
        _model = SentenceTransformer(settings.embedding_model)
    return _model


def embed_query(text: str) -> list[float]:
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def embed_documents(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    model = _get_model()
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=batch_size, show_progress_bar=True)
    return embeddings.tolist()
