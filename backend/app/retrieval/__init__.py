from typing import List
from backend.app.retrieval.faiss_store import RetrievalStore
from backend.app.utils.logging import get_logger

logger = get_logger(__name__)

# Global retrieval store instance
_retrieval_store: RetrievalStore = None


def get_retrieval_store() -> RetrievalStore:
    """
    Get or create the global retrieval store instance.
    
    Returns:
        RetrievalStore instance
    """
    global _retrieval_store
    if _retrieval_store is None:
        _retrieval_store = RetrievalStore()
        logger.info("Initialized global retrieval store")
    return _retrieval_store


async def get_context(commit_sha: str, top_k: int = 5) -> List[str]:
    """
    Return top-k related snippets for given commit.
    
    This is a placeholder implementation that will be enhanced
    with real repository parsing in future phases.
    
    Args:
        commit_sha: Git commit SHA
        top_k: Number of context snippets to return
        
    Returns:
        List of context strings
    """
    try:
        store = get_retrieval_store()
        
        # For now, simulate context retrieval with placeholder data
        # In a real implementation, this would:
        # 1. Parse the repository at the given commit
        # 2. Extract relevant code snippets, logs, configs
        # 3. Use the retrieval store to find similar contexts
        
        placeholder_contexts = [
            f"Build configuration for commit {commit_sha[:8]}",
            f"Test suite execution logs from {commit_sha[:8]}",
            f"Error patterns detected in {commit_sha[:8]}",
            f"Dependency changes in {commit_sha[:8]}",
            f"Performance metrics for {commit_sha[:8]}"
        ]
        
        # Query the store for similar contexts
        query_text = f"commit {commit_sha} build failure diagnostics"
        results = store.query(query_text, top_k=top_k)
        
        # If we have real results, use them; otherwise use placeholders
        if results:
            context_strings = [text for text, score in results]
        else:
            context_strings = placeholder_contexts[:top_k]
        
        logger.info(f"Retrieved {len(context_strings)} context snippets for commit {commit_sha[:8]}")
        return context_strings
        
    except Exception as e:
        logger.error(f"Failed to get context for commit {commit_sha}: {e}")
        # Return fallback context
        return [f"Fallback context for commit {commit_sha[:8]}"]


async def add_context_texts(texts: List[str]) -> None:
    """
    Add context texts to the retrieval store.
    
    Args:
        texts: List of text strings to add to the store
    """
    try:
        store = get_retrieval_store()
        store.add_texts(texts)
        store.save_index()
        logger.info(f"Added {len(texts)} context texts to retrieval store")
    except Exception as e:
        logger.error(f"Failed to add context texts: {e}")


async def initialize_retrieval_store() -> None:
    """
    Initialize the retrieval store with some default context.
    This is called during app startup to populate the store.
    """
    try:
        store = get_retrieval_store()
        
        # Add some default context texts for demonstration
        default_contexts = [
            "Build failure: missing import statement in utils.py",
            "Test failure: assertion error in test_user_authentication",
            "Deployment error: environment variable not set",
            "Performance issue: slow database query in user service",
            "Configuration error: invalid YAML syntax in docker-compose.yml",
            "Dependency conflict: version mismatch in package.json",
            "Network timeout: connection refused to external API",
            "Memory leak: increasing memory usage in background process",
            "File permission error: cannot write to log directory",
            "SSL certificate error: expired certificate for domain"
        ]
        
        store.add_texts(default_contexts)
        store.save_index()
        
        logger.info("Initialized retrieval store with default contexts")
        
    except Exception as e:
        logger.error(f"Failed to initialize retrieval store: {e}")
