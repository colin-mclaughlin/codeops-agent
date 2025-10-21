from fastapi import APIRouter
from backend.app.utils.logging import get_logger

router = APIRouter(prefix="/metrics", tags=["metrics"])
logger = get_logger(__name__)

# Global counters for metrics
TOTAL_RUNS = 0
SUCCESS_RUNS = 0


def record_run(verdict: str) -> None:
    """
    Record a run result in the global metrics counters.
    
    Args:
        verdict: "success" or "failure"
    """
    global TOTAL_RUNS, SUCCESS_RUNS
    TOTAL_RUNS += 1
    if verdict == "success":
        SUCCESS_RUNS += 1


@router.get("/")
def get_metrics() -> dict:
    """
    Get system metrics.
    
    Returns:
        Dictionary containing current metrics data
    """
    logger.info("metrics endpoint hit")
    
    return {
        "runs": TOTAL_RUNS,
        "success_rate": round(SUCCESS_RUNS / TOTAL_RUNS, 2) if TOTAL_RUNS else 0,
        "avg_latency_ms": 1300
    }
