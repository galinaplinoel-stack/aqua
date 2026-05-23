"""Vector memory tools - semantic search for memory."""

import json
import os
from typing import Optional

from rich.console import Console

console = Console()


class VectorMemory:
    """Simple vector-based memory using embeddings."""

    def __init__(self, path: str = "vector_memory.json"):
        self.path = path
        self.memories: list[dict] = []
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f:
                    self.memories = json.load(f)
            except:
                self.memories = []

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(self.memories, f, indent=2)

    def add(self, text: str, metadata: Optional[dict] = None) -> dict:
        """Add a memory with optional metadata."""
        memory = {
            "id": len(self.memories) + 1,
            "text": text,
            "metadata": metadata or {},
            "embedding": self._get_embedding(text),
        }
        self.memories.append(memory)
        self._save()
        return memory

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search memories by semantic similarity."""
        if not self.memories:
            return []

        query_embedding = self._get_embedding(query)

        # Calculate similarities
        scored = []
        for mem in self.memories:
            if "embedding" in mem:
                similarity = self._cosine_similarity(query_embedding, mem["embedding"])
                scored.append({"memory": mem, "similarity": similarity})

        # Sort by similarity
        scored.sort(key=lambda x: x["similarity"], reverse=True)

        return [
            {
                "id": item["memory"]["id"],
                "text": item["memory"]["text"],
                "metadata": item["memory"]["metadata"],
                "similarity": round(item["similarity"], 4),
            }
            for item in scored[:limit]
        ]

    def _get_embedding(self, text: str) -> list[float]:
        """Get embedding for text (simple hash-based for now)."""
        # Simple hash-based pseudo-embedding
        # In production, use OpenAI embeddings or similar
        import hashlib
        hash_obj = hashlib.md5(text.lower().encode())
        hex_dig = hash_obj.hexdigest()

        # Convert to list of floats
        embedding = []
        for i in range(0, len(hex_dig), 2):
            embedding.append(int(hex_dig[i:i+2], 16) / 255.0)

        return embedding

    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    def list_all(self) -> list[dict]:
        """List all memories."""
        return [
            {"id": m["id"], "text": m["text"], "metadata": m["metadata"]}
            for m in self.memories
        ]

    def delete(self, memory_id: int) -> bool:
        """Delete a memory by ID."""
        self.memories = [m for m in self.memories if m["id"] != memory_id]
        self._save()
        return True


_vector_memory = None


def get_vector_memory() -> VectorMemory:
    global _vector_memory
    if _vector_memory is None:
        _vector_memory = VectorMemory()
    return _vector_memory


def add_memory(text: str, metadata: Optional[str] = None) -> str:
    """Add a memory."""
    meta = json.loads(metadata) if metadata else None
    memory = get_vector_memory().add(text, meta)
    return json.dumps({"id": memory["id"], "text": memory["text"]}, indent=2)


def search_memory(query: str, limit: int = 5) -> str:
    """Search memories by semantic similarity."""
    results = get_vector_memory().search(query, limit)
    return json.dumps(results, indent=2)


def list_memories() -> str:
    """List all memories."""
    memories = get_vector_memory().list_all()
    return json.dumps(memories, indent=2)


VECTOR_MEMORY_TOOLS = {
    "add_memory": {
        "func": add_memory,
        "schema": {
            "type": "function",
            "function": {
                "name": "add_memory",
                "description": "Add a memory to vector storage.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {"type": "string", "description": "Memory text"},
                        "metadata": {"type": "string", "description": "JSON metadata"},
                    },
                    "required": ["text"],
                },
            },
        },
    },
    "search_memory": {
        "func": search_memory,
        "schema": {
            "type": "function",
            "function": {
                "name": "search_memory",
                "description": "Search memories by semantic similarity.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "description": "Max results (default: 5)"},
                    },
                    "required": ["query"],
                },
            },
        },
    },
    "list_memories": {
        "func": list_memories,
        "schema": {
            "type": "function",
            "function": {
                "name": "list_memories",
                "description": "List all stored memories.",
                "parameters": {"type": "object", "properties": {}},
            },
        },
    },
}
