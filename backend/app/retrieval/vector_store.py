import json
from typing import List, Dict, Any, Optional
from backend.app.utils.logging import get_logger

logger = get_logger(__name__)

# Try to import FAISS, but don't fail if not available
try:
    import faiss
    import numpy as np
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logger.warning("FAISS not available, using in-memory fallback")


class VectorStore:
    """
    Vector storage with FAISS backend or in-memory fallback.
    
    Provides methods to add vectors with metadata and query for similar vectors.
    """
    
    def __init__(self, dimension: int = 1536):
        """
        Initialize the vector store.
        
        Args:
            dimension: Dimension of the embedding vectors
        """
        self.dimension = dimension
        self.metadata_store: Dict[str, Dict[str, Any]] = {}
        
        if FAISS_AVAILABLE:
            # Initialize FAISS index
            self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity)
            self.id_to_index: Dict[str, int] = {}
            self.index_to_id: Dict[int, str] = {}
            logger.info("VectorStore initialized with FAISS backend")
        else:
            # Fallback to in-memory storage
            self.vectors: Dict[str, List[float]] = {}
            logger.info("VectorStore initialized with in-memory fallback")
    
    def add(self, id: str, vector: List[float], metadata: Dict[str, Any]) -> None:
        """
        Add a vector with metadata to the store.
        
        Args:
            id: Unique identifier for the vector
            vector: Embedding vector
            metadata: Associated metadata
        """
        if len(vector) != self.dimension:
            logger.error(f"Vector dimension {len(vector)} does not match expected {self.dimension}")
            return
        
        # Store metadata
        self.metadata_store[id] = metadata
        
        if FAISS_AVAILABLE:
            # Add to FAISS index
            vector_array = np.array([vector], dtype=np.float32)
            # Normalize for cosine similarity
            faiss.normalize_L2(vector_array)
            
            index_pos = self.index.ntotal
            self.index.add(vector_array)
            self.id_to_index[id] = index_pos
            self.index_to_id[index_pos] = id
        else:
            # Store in memory
            self.vectors[id] = vector.copy()
        
        logger.info(f"vector added with id: {id}")
    
    def query(self, vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Query for similar vectors.
        
        Args:
            vector: Query vector
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries containing id, score, and metadata
        """
        if len(vector) != self.dimension:
            logger.error(f"Query vector dimension {len(vector)} does not match expected {self.dimension}")
            return []
        
        if FAISS_AVAILABLE:
            if self.index.ntotal == 0:
                logger.info("query executed (no vectors in index)")
                return []
            
            # Prepare query vector
            query_array = np.array([vector], dtype=np.float32)
            faiss.normalize_L2(query_array)
            
            # Search
            scores, indices = self.index.search(query_array, min(top_k, self.index.ntotal))
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1:  # Valid result
                    vector_id = self.index_to_id[idx]
                    result = {
                        "id": vector_id,
                        "score": float(score),
                        "metadata": self.metadata_store[vector_id]
                    }
                    results.append(result)
        else:
            # In-memory similarity search (cosine similarity)
            if not self.vectors:
                logger.info("query executed (no vectors in memory)")
                return []
            
            # Calculate cosine similarities
            similarities = []
            for vector_id, stored_vector in self.vectors.items():
                # Calculate cosine similarity
                dot_product = sum(a * b for a, b in zip(vector, stored_vector))
                norm_a = sum(a * a for a in vector) ** 0.5
                norm_b = sum(b * b for b in stored_vector) ** 0.5
                
                if norm_a > 0 and norm_b > 0:
                    similarity = dot_product / (norm_a * norm_b)
                    similarities.append((vector_id, similarity))
            
            # Sort by similarity and take top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            results = []
            for vector_id, score in similarities[:top_k]:
                result = {
                    "id": vector_id,
                    "score": score,
                    "metadata": self.metadata_store[vector_id]
                }
                results.append(result)
        
        logger.info(f"query executed (returned {len(results)} results)")
        return results
