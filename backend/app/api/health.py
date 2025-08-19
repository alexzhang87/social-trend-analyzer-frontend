from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["Health"])
async def health_check():
    """
    Health check endpoint to confirm the API is running.
    """
    return {"status": "ok"}