import chromadb
from chromadb.utils import embedding_functions
import hashlib
import json
import time
from typing import List, Dict

class LongTermMemory:
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "agent_memory"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embed_fn
        )
    
    def remember(self, goal: str, action: Dict, outcome: str, verification: Dict = None):
        doc = {
            "goal": goal,
            "action": action,
            "outcome": outcome,
            "verification": verification or {},
            "timestamp": time.time()
        }
        doc_str = json.dumps(doc, ensure_ascii=False)
        doc_id = hashlib.md5(doc_str.encode()).hexdigest()
        self.collection.add(documents=[doc_str], ids=[doc_id])
    
    def recall(self, query: str, n_results: int = 3) -> List[Dict]:
        try:
            results = self.collection.query(query_texts=[query], n_results=n_results)
            if results and results['documents']:
                return [json.loads(doc) for doc in results['documents'][0]]
            return []
        except Exception:
            return []