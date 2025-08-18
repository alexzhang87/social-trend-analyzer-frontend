from fastapi import APIRouter

router = APIRouter()

@router.get("/api/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to confirm the API is running.
    """
    return {"status": "ok"}