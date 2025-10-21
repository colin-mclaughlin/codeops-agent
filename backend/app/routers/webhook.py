from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db import get_session
from backend.app.models.run_log import RunLog

router = APIRouter(prefix="", tags=["webhook"])


@router.post("/webhook")
async def webhook(
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> dict:
    # Get the GitHub event type from headers
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    
    # Get the JSON payload
    payload = await request.json()
    
    # Create and insert the RunLog record
    run_log = RunLog(
        event_type=event_type,
        payload=payload
    )
    session.add(run_log)
    await session.commit()
    
    return {"status": "received"}
