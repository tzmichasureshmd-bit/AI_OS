"""Knowledge Service (RAG) - PDF/FAQ upload, vector search, contextual answers."""

import uuid
from typing import Optional
from ..config import get_settings


class KnowledgeService:
    def __init__(self):
        self._qdrant = None

    def _client(self):
        if not self._qdrant:
            from qdrant_client import QdrantClient
            self._qdrant = QdrantClient(url=get_settings().qdrant_url)
        return self._qdrant

    async def get_context(self, collection: str, query: str, top_k: int = 3) -> str:
        """Get relevant knowledge for a conversation turn."""
        try:
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer("all-MiniLM-L6-v2")
            embedding = model.encode(query).tolist()
            results = self._client().search(collection_name=collection, query_vector=embedding, limit=top_k, score_threshold=0.45)
            if results:
                context = "COMPANY KNOWLEDGE:\n"
                context += "\n".join(f"- {r.payload.get('text', '')}" for r in results)
                return context
        except Exception:
            pass
        return ""

    async def ingest_text(self, collection: str, text: str, source: str = "manual") -> int:
        """Chunk and store text in vector DB."""
        try:
            from qdrant_client.models import VectorParams, Distance, PointStruct
            from sentence_transformers import SentenceTransformer

            client = self._client()
            try:
                client.create_collection(collection, vectors_config=VectorParams(size=384, distance=Distance.COSINE))
            except Exception:
                pass

            model = SentenceTransformer("all-MiniLM-L6-v2")
            chunks = [text[i:i+500] for i in range(0, len(text), 450)]
            embeddings = model.encode(chunks)

            points = [
                PointStruct(id=str(uuid.uuid4()), vector=emb.tolist(), payload={"text": chunk, "source": source})
                for chunk, emb in zip(chunks, embeddings)
            ]
            client.upsert(collection_name=collection, points=points)
            return len(chunks)
        except Exception:
            return 0
