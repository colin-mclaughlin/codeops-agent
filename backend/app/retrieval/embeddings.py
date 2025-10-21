import json
from typing import List, Optional
from backend.app.config import settings
from backend.app.utils.logging import get_logger

logger = get_logger(__name__)

# Try to import OpenAI, but don't fail if not available
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI package not available, using fake embeddings")


async def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for the given text using OpenAI's text-embedding-3-small model.
    
    If OpenAI API key is not available or OpenAI package is not installed,
    returns a fake vector of fixed length.
    
    Args:
        text: Text to generate embedding for
        
    Returns:
        List of float values representing the embedding vector
    """
    try:
        # Check if OpenAI is available and API key is set
        if not OPENAI_AVAILABLE or not settings.OPENAI_API_KEY:
            logger.info("OpenAI not available or API key not set, using fake embedding")
            # Return fake embedding with standard text-embedding-3-small dimension
            fake_embedding = [0.0] * 1536
            logger.info("embedding generated (fake)")
            return fake_embedding
        
        # Initialize OpenAI client
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Generate embedding
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        
        embedding = response.data[0].embedding
        logger.info("embedding generated (OpenAI)")
        return embedding
        
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        # Fallback to fake embedding
        fake_embedding = [0.0] * 1536
        logger.info("embedding generated (fallback)")
        return fake_embedding
