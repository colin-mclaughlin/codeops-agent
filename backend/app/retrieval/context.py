import json
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.run_log import RunLog
from backend.app.retrieval.embeddings import get_embedding
from backend.app.retrieval.vector_store import VectorStore
from backend.app.utils.logging import get_logger

logger = get_logger(__name__)


class ContextRetriever:
    """
    Retrieval module for extracting and combining context from repository files and CI logs.
    
    This class provides stubs for future implementation of code parsing, log extraction,
    and context combination for the CodeOps Agent. Now includes embedding-based context indexing.
    """
    
    def __init__(self, db_session: AsyncSession) -> None:
        """
        Initialize the ContextRetriever with a database session.
        
        Args:
            db_session: Async SQLAlchemy session for database operations
        """
        self.db_session = db_session
        self.vector_store = VectorStore()
    
    async def parse_repo_files(self, repo_path: str) -> List[str]:
        """
        Parse repository files to extract code and comments.
        
        This is a stub implementation that will later extract code and comments
        from repository files for context retrieval.
        
        Args:
            repo_path: Path to the repository directory
            
        Returns:
            List of parsed file contents (currently empty)
        """
        return []
    
    async def parse_ci_logs(self, run_id: int) -> str:
        """
        Parse CI logs for a specific run ID.
        
        This is a stub implementation that will later extract CI log text
        from RunLog database records or filesystem.
        
        Args:
            run_id: ID of the CI run to parse logs for
            
        Returns:
            Extracted log text (currently empty string)
        """
        return ""
    
    async def get_context(self, commit_sha: str) -> Dict[str, any]:
        """
        Get combined context for a specific commit.
        
        This is a stub implementation that will later combine parsed code
        and logs into a comprehensive context dictionary.
        
        Args:
            commit_sha: Git commit SHA to get context for
            
        Returns:
            Dictionary containing commit_sha, files, and logs
        """
        return {
            "commit_sha": commit_sha,
            "files": [],
            "logs": ""
        }
    
    async def build_context_index(self) -> None:
        """
        Build a vector index from all RunLog payloads in the database.
        
        Retrieves all RunLog records, generates embeddings for their payloads,
        and stores them in the vector store for semantic search.
        """
        try:
            # Query all RunLog records
            stmt = select(RunLog)
            result = await self.db_session.execute(stmt)
            run_logs = result.scalars().all()
            
            logger.info(f"Found {len(run_logs)} RunLog records to index")
            
            for run_log in run_logs:
                # Convert payload to JSON string for embedding
                payload_text = json.dumps(run_log.payload, sort_keys=True)
                
                # Generate embedding
                embedding = await get_embedding(payload_text)
                
                # Create metadata
                metadata = {
                    "run_log_id": run_log.id,
                    "event_type": run_log.event_type,
                    "created_at": run_log.created_at.isoformat() if run_log.created_at else None,
                    "payload": run_log.payload
                }
                
                # Add to vector store
                vector_id = f"run_log_{run_log.id}"
                self.vector_store.add(vector_id, embedding, metadata)
            
            logger.info(f"Context index built with {len(run_logs)} entries")
            
        except Exception as e:
            logger.error(f"Error building context index: {e}")
    
    async def query_context(self, query: str) -> List[Dict[str, Any]]:
        """
        Query the context index for relevant information.
        
        Args:
            query: Natural language query string
            
        Returns:
            List of relevant context entries with scores and metadata
        """
        try:
            # Generate embedding for the query
            query_embedding = await get_embedding(query)
            
            # Query the vector store
            results = self.vector_store.query(query_embedding, top_k=5)
            
            logger.info(f"Context query returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error querying context: {e}")
            return []
