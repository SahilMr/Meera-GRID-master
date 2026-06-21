import os
import json
import hashlib
import math
import threading
from typing import List, Tuple, Dict, Any

class EmbeddingModel:
    def __init__(self, model_name: str = "nvidia/llama-nemotron-embed-1b-v2"):
        self.model_name = model_name

    def embed_query(self, text: str) -> List[float]:
        dim = 1024
        vector = [0.0] * dim
        words = text.lower().split()
        if not words:
            vector[0] = 1.0
            return vector
            
        for word in words:
            # Consistent hashing across process starts
            hash_val = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            index = hash_val % dim
            vector[index] += 1.0
            
        l2_norm = math.sqrt(sum(x * x for x in vector))
        if l2_norm > 0:
            vector = [x / l2_norm for x in vector]
        else:
            vector[0] = 1.0
            
        return vector

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_query(text) for text in texts]

class FAISSIndex:
    def __init__(self, embedding_model: EmbeddingModel):
        self.embedding_model = embedding_model
        self.vectors: List[List[float]] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        for text, meta in zip(texts, metadatas):
            vector = self.embedding_model.embed_query(text)
            self.vectors.append(vector)
            self.metadatas.append(meta)

    def similarity_search_with_score(self, query: str, k: int = 3) -> List[Tuple[Dict[str, Any], float]]:
        if not self.vectors:
            return []
            
        query_vector = self.embedding_model.embed_query(query)
        
        results = []
        for vec, meta in zip(self.vectors, self.metadatas):
            dot_product = sum(q * v for q, v in zip(query_vector, vec))
            # Round score to 4 decimal places for consistency
            results.append((meta, round(dot_product, 4)))
            
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def save_local(self, folder_path: str):
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, "index.json")
        data = {
            "vectors": self.vectors,
            "metadatas": self.metadatas
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @classmethod
    def load_local(cls, folder_path: str, embedding_model: EmbeddingModel):
        file_path = os.path.join(folder_path, "index.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No FAISS index file found at {file_path}")
            
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        instance = cls(embedding_model)
        instance.vectors = data.get("vectors", [])
        instance.metadatas = data.get("metadatas", [])
        return instance
