from fastapi import APIRouter
from backend.app.utils.logging import get_logger

router = APIRouter(prefix="/metrics", tags=["metrics"])
logger = get_logger(__name__)


@router.get("/")
def get_metrics() -> dict:
    """
    Get system metrics.
    
    Returns:
        Dictionary containing dummy metrics data
    """
    logger.info("metrics endpoint hit")
    
    return {
        "runs": 42,
        "success_rate": 0.85,
        "avg_latency_ms": 1300
    }
