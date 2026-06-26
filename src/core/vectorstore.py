import os
import json
import hashlib
import math
import threading
from typing import List, Tuple, Dict, Any

class EmbeddingModel:
    def __init__(self, model_name: str = "nvidia/llama-nemotron-embed-1b-v2", backend: str = "auto"):
        self.model_name = model_name
        self.backend = backend
        self.tokenizer = None
        self.model = None

    def _detect_backend(self) -> str:
        # 1. Check if Ollama is responsive
        import requests
        try:
            res = requests.get("http://127.0.0.1:11434/api/tags", timeout=1)
            if res.status_code == 200:
                print("EmbeddingModel: Detected local Ollama service. Using 'ollama' backend.")
                return "ollama"
        except Exception:
            pass

        # 2. Check if torch & transformers are installed
        try:
            import torch
            import transformers
            print("EmbeddingModel: Detected 'torch' and 'transformers'. Using HF backend on CPU.")
            return "transformers"
        except ImportError:
            pass

        # 3. Check if llama_cpp is installed
        try:
            import llama_cpp
            print("EmbeddingModel: Detected 'llama_cpp'. Using 'llama_cpp' backend.")
            return "llama_cpp"
        except ImportError:
            pass

        # 4. Fallback to mock
        import logging
        logging.warning(
            "EmbeddingModel: No ML frameworks (torch/transformers, llama_cpp) or Ollama service detected. "
            "FALLING BACK TO MOCK HASHING EMBEDDINGS. This will not run a real model inference!"
        )
        return "mock"

    def _embed_query_transformers(self, text: str) -> List[float]:
        import torch
        if self.tokenizer is None or self.model is None:
            from transformers import AutoTokenizer, AutoModel
            print(f"Loading local Hugging Face model and tokenizer for: {self.model_name} on CPU...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.eval()

        # Tokenize text
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        
        # Forward pass without gradient tracking
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Extract the final hidden state (outputs.last_hidden_state)
        # Sequence dimension is 1, batch dimension is 0
        token_embeddings = outputs.last_hidden_state
        attention_mask = inputs["attention_mask"]
        
        # Perform mean-pooling, ignoring padding tokens
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        query_embedding = sum_embeddings / sum_mask
        
        # Extract to list
        vector = query_embedding[0].tolist()
        return vector

    def _embed_query_ollama(self, text: str) -> List[float]:
        import requests
        # Attempt standard /api/embed (newer)
        try:
            res = requests.post(
                "http://127.0.0.1:11434/api/embed",
                json={"model": self.model_name, "input": text},
                timeout=15
            )
            if res.status_code == 200:
                return res.json()["embeddings"][0]
        except Exception:
            pass

        # Fallback to /api/embeddings (older)
        try:
            res = requests.post(
                "http://127.0.0.1:11434/api/embeddings",
                json={"model": self.model_name, "prompt": text},
                timeout=15
            )
            if res.status_code == 200:
                return res.json()["embedding"]
            else:
                raise RuntimeError(f"Ollama returned status {res.status_code}: {res.text}")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch embeddings from Ollama API: {e}")

    def _embed_query_llama_cpp(self, text: str) -> List[float]:
        import os
        model_path = os.getenv("LLAMA_MODEL_PATH")
        if not model_path:
            ggufs = [f for f in os.listdir(".") if f.endswith(".gguf")]
            if ggufs:
                model_path = ggufs[0]
            else:
                raise ValueError("LLAMA_MODEL_PATH environment variable not set, and no GGUF file found in current directory.")

        if self.model is None:
            from llama_cpp import Llama
            self.model = Llama(model_path=model_path, embedding=True, verbose=False)

        res = self.model.create_embedding(text)
        return res["data"][0]["embedding"]

    def _embed_query_mock(self, text: str) -> List[float]:
        dim = 1024
        vector = [0.0] * dim
        words = text.lower().split()
        if not words:
            vector[0] = 1.0
            return vector
            
        for word in words:
            hash_val = int(hashlib.md5(word.encode('utf-8')).hexdigest(), 16)
            index = hash_val % dim
            vector[index] += 1.0
            
        return vector

    def embed_query(self, text: str) -> List[float]:
        if self.backend == "auto":
            self.backend = self._detect_backend()

        if self.backend == "transformers":
            vector = self._embed_query_transformers(text)
        elif self.backend == "ollama":
            vector = self._embed_query_ollama(text)
        elif self.backend == "llama_cpp":
            vector = self._embed_query_llama_cpp(text)
        elif self.backend == "mock":
            vector = self._embed_query_mock(text)
        else:
            raise ValueError(f"Unknown embedding backend: {self.backend}")

        # Validation: Raise a loud exception if vector norm is below 0.01
        l2_norm = math.sqrt(sum(x * x for x in vector))
        if l2_norm < 0.01:
            raise ValueError(
                f"Embedding vector L2 norm ({l2_norm:.6f}) is below the threshold of 0.01. "
                "This indicates a potential model failure (silent zero output, OOM, or layer extraction issue)."
            )

        # L2 Normalize the vector to ensure it's normalized for FAISS index compatibility
        vector = [x / l2_norm for x in vector]
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