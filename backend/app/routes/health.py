from fastapi import APIRouter
from supabase import create_client

from app.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check():
    settings = get_settings()
    try:
        client = create_client(settings.supabase_url, settings.supabase_key)
        result = client.table("papers").select("pmid", count="exact").limit(1).execute()
        paper_count = result.count or 0
        return {"status": "healthy", "papers_indexed": paper_count}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}
