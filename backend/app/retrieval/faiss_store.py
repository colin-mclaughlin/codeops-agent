import os
import pickle
import numpy as np
import faiss
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from backend.app.utils.logging import get_logger

logger = get_logger(__name__)


class RetrievalStore:
    """
    FAISS-based vector store for semantic retrieval of code context.
    
    Uses sentence-transformers for embeddings and FAISS for efficient similarity search.
    """
    
    def __init__(self, index_path: str = "faiss_index.bin", model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the retrieval store.
        
        Args:
            index_path: Path to save/load the FAISS index
            model_name: Name of the sentence transformer model to use
        """
        self.index_path = index_path
        self.model_name = model_name
        self.model = None
        self.index = None
        self.texts = []  # Store original texts for retrieval
        self.embedding_dim = 384  # Dimension for all-MiniLM-L6-v2
        
        self._initialize_model()
        self._initialize_index()
    
    def _initialize_model(self):
        """Initialize the sentence transformer model."""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Initialized sentence transformer model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize model {self.model_name}: {e}")
            raise
    
    def _initialize_index(self):
        """Initialize or load the FAISS index."""
        try:
            if os.path.exists(self.index_path):
                self._load_index()
                logger.info(f"Loaded existing FAISS index from {self.index_path}")
            else:
                # Create new index
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                logger.info(f"Created new FAISS index with dimension {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            raise
    
    def add_texts(self, texts: List[str]) -> None:
        """
        Add texts to the vector store.
        
        Args:
            texts: List of text strings to add
        """
        if not texts:
            logger.warning("No texts provided to add")
            return
        
        try:
            # Generate embeddings
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            embeddings = np.array(embeddings).astype('float32')
            
            # Add to FAISS index
            self.index.add(embeddings)
            
            # Store original texts
            self.texts.extend(texts)
            
            logger.info(f"Added {len(texts)} texts to vector store. Total: {len(self.texts)}")
            
        except Exception as e:
            logger.error(f"Failed to add texts to vector store: {e}")
            raise
    
    def query(self, query_text: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Query the vector store for similar texts.
        
        Args:
            query_text: Query string
            top_k: Number of top results to return
            
        Returns:
            List of tuples (text, similarity_score)
        """
        if not self.texts:
            logger.warning("No texts in vector store to query")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query_text], convert_to_tensor=False)
            query_embedding = np.array(query_embedding).astype('float32')
            
            # Search in FAISS index
            scores, indices = self.index.search(query_embedding, min(top_k, len(self.texts)))
            
            # Return results with original texts
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.texts):  # Valid index
                    # Convert L2 distance to similarity score (lower distance = higher similarity)
                    similarity = 1.0 / (1.0 + score)
                    results.append((self.texts[idx], similarity))
            
            logger.info(f"Query returned {len(results)} results for: {query_text[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Failed to query vector store: {e}")
            return []
    
    def save_index(self) -> None:
        """Save the FAISS index and texts to disk."""
        try:
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Save texts separately
            texts_path = self.index_path.replace('.bin', '_texts.pkl')
            with open(texts_path, 'wb') as f:
                pickle.dump(self.texts, f)
            
            logger.info(f"Saved FAISS index and texts to {self.index_path}")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    def _load_index(self) -> None:
        """Load the FAISS index and texts from disk."""
        try:
            # Load FAISS index
            self.index = faiss.read_index(self.index_path)
            
            # Load texts
            texts_path = self.index_path.replace('.bin', '_texts.pkl')
            if os.path.exists(texts_path):
                with open(texts_path, 'rb') as f:
                    self.texts = pickle.load(f)
            else:
                self.texts = []
            
            logger.info(f"Loaded FAISS index with {len(self.texts)} texts")
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            # Create new index if loading fails
            self.index = faiss.IndexFlatL2(self.embedding_dim)
            self.texts = []
    
    def get_stats(self) -> dict:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with store statistics
        """
        return {
            "total_texts": len(self.texts),
            "index_size": self.index.ntotal if self.index else 0,
            "embedding_dim": self.embedding_dim,
            "model_name": self.model_name,
            "index_path": self.index_path
        }
    
    def clear(self) -> None:
        """Clear all texts and reset the index."""
        self.texts = []
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        logger.info("Cleared vector store")
