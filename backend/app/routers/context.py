from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from backend.app.retrieval import get_context, get_retrieval_store, add_context_texts
from backend.app.utils.logging import get_logger

router = APIRouter(prefix="/context", tags=["context"])
logger = get_logger(__name__)


@router.get("/")
async def get_context_for_commit(
    commit_sha: str = Query(..., description="Git commit SHA to get context for"),
    top_k: int = Query(5, description="Number of context snippets to return", ge=1, le=20)
) -> dict:
    """
    Get semantic context for a given commit SHA.
    
    This endpoint retrieves relevant code snippets, logs, and configuration
    information that might be related to the commit for debugging purposes.
    
    Args:
        commit_sha: Git commit SHA (can be full or abbreviated)
        top_k: Number of context snippets to return (1-20)
        
    Returns:
        Dictionary containing context information
    """
    try:
        if not commit_sha or len(commit_sha.strip()) < 4:
            raise HTTPException(
                status_code=400, 
                detail="commit_sha must be at least 4 characters long"
            )
        
        # Clean the commit SHA
        commit_sha = commit_sha.strip()
        
        # Get context from retrieval system
        context_snippets = await get_context(commit_sha, top_k=top_k)
        
        # Get store statistics
        store = get_retrieval_store()
        store_stats = store.get_stats()
        
        response = {
            "commit_sha": commit_sha,
            "context_snippets": context_snippets,
            "total_snippets": len(context_snippets),
            "store_stats": {
                "total_texts": store_stats["total_texts"],
                "index_size": store_stats["index_size"],
                "model_name": store_stats["model_name"]
            }
        }
        
        logger.info(f"Retrieved context for commit {commit_sha[:8]}: {len(context_snippets)} snippets")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving context for commit {commit_sha}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve context")


@router.post("/add")
async def add_context(
    texts: List[str],
    commit_sha: Optional[str] = None
) -> dict:
    """
    Add context texts to the retrieval store.
    
    This endpoint allows adding new context texts that can be retrieved
    later for semantic similarity search.
    
    Args:
        texts: List of text strings to add to the store
        commit_sha: Optional commit SHA associated with these texts
        
    Returns:
        Dictionary with operation result
    """
    try:
        if not texts:
            raise HTTPException(status_code=400, detail="No texts provided")
        
        if len(texts) > 100:
            raise HTTPException(status_code=400, detail="Too many texts (max 100)")
        
        # Add texts to the store
        await add_context_texts(texts)
        
        # Get updated store stats
        store = get_retrieval_store()
        store_stats = store.get_stats()
        
        response = {
            "message": f"Added {len(texts)} context texts",
            "commit_sha": commit_sha,
            "store_stats": {
                "total_texts": store_stats["total_texts"],
                "index_size": store_stats["index_size"]
            }
        }
        
        logger.info(f"Added {len(texts)} context texts to store")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding context texts: {e}")
        raise HTTPException(status_code=500, detail="Failed to add context texts")


@router.get("/stats")
async def get_context_stats() -> dict:
    """
    Get statistics about the context retrieval store.
    
    Returns:
        Dictionary with store statistics
    """
    try:
        store = get_retrieval_store()
        stats = store.get_stats()
        
        return {
            "store_stats": stats,
            "status": "healthy"
        }
        
    except Exception as e:
        logger.error(f"Error getting context stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get context stats")


@router.post("/query")
async def query_context(
    query_text: str,
    top_k: int = Query(5, description="Number of results to return", ge=1, le=20)
) -> dict:
    """
    Query the context store for similar texts.
    
    Args:
        query_text: Text to search for similar contexts
        top_k: Number of results to return
        
    Returns:
        Dictionary with query results
    """
    try:
        if not query_text or len(query_text.strip()) < 3:
            raise HTTPException(
                status_code=400, 
                detail="query_text must be at least 3 characters long"
            )
        
        store = get_retrieval_store()
        results = store.query(query_text.strip(), top_k=top_k)
        
        # Format results
        formatted_results = [
            {
                "text": text,
                "similarity_score": round(score, 4),
                "rank": i + 1
            }
            for i, (text, score) in enumerate(results)
        ]
        
        response = {
            "query": query_text.strip(),
            "results": formatted_results,
            "total_results": len(formatted_results)
        }
        
        logger.info(f"Query '{query_text[:50]}...' returned {len(results)} results")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying context: {e}")
        raise HTTPException(status_code=500, detail="Failed to query context")
