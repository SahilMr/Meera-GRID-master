import os
import threading
from src.core.vectorstore import EmbeddingModel, FAISSIndex

# Thread lock for initialization
_init_lock = threading.RLock()

# Global singleton instances
_embedding_model = None
_faiss_index = None

VECTORSTORE_DIR = "./vectorstore/faiss_index"

def get_embedding_model() -> EmbeddingModel:
    global _embedding_model
    if _embedding_model is None:
        with _init_lock:
            if _embedding_model is None:
                _embedding_model = EmbeddingModel()
    return _embedding_model

def get_faiss_index() -> FAISSIndex:
    print("I AMA HERE")
    global _faiss_index
    if _faiss_index is None:
        with _init_lock:
            if _faiss_index is None:
                embed_model = get_embedding_model()
                if os.path.exists(os.path.join(VECTORSTORE_DIR, "index.json")):
                    try:
                        _faiss_index = FAISSIndex.load_local(VECTORSTORE_DIR, embed_model)
                        print(f"Loaded existing FAISS index from {VECTORSTORE_DIR}")
                    except Exception as e:
                        print(f"Error loading FAISS index: {e}. Re-initializing empty index.")
                        _faiss_index = FAISSIndex(embed_model)
                else:
                    _faiss_index = FAISSIndex(embed_model)
                    print("Initialized empty FAISS index at startup.")
    return _faiss_index
