"""Local RAG knowledge agent. Uses TF-IDF + cosine similarity (sklearn) over the markdown
knowledge base — lightweight, no external vector DB required. Falls back to a clear
'nothing relevant found' message when similarity is too low."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import get_settings
from app.services.llm_provider import get_llm_provider

SIMILARITY_THRESHOLD = 0.08


class KnowledgeIndex:
    def __init__(self, docs: list[tuple[str, str]]):
        self.names = [d[0] for d in docs]
        self.texts = [d[1] for d in docs]
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = self.vectorizer.fit_transform(self.texts) if self.texts else None

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        if self.matrix is None:
            return []
        q_vec = self.vectorizer.transform([query])
        sims = cosine_similarity(q_vec, self.matrix)[0]
        ranked = sorted(range(len(sims)), key=lambda i: -sims[i])[:top_k]
        return [{"doc": self.names[i], "score": round(float(sims[i]), 4), "text": self.texts[i]} for i in ranked if sims[i] >= SIMILARITY_THRESHOLD]


@lru_cache
def _get_index() -> KnowledgeIndex:
    settings = get_settings()
    docs = []
    for path in sorted(Path(settings.KNOWLEDGE_DIR).glob("*.md")):
        docs.append((path.stem, path.read_text(encoding="utf-8")))
    return KnowledgeIndex(docs)


def ask_knowledge(question: str) -> dict:
    index = _get_index()
    matches = index.search(question)
    if not matches:
        return {
            "question": question,
            "matches": [],
            "answer": "No relevant information was found in the local knowledge base for this question. "
                      "Try rephrasing, or ask about a core ML/stats concept (regression, classification, "
                      "clustering, precision, recall, F1, RMSE, R2, overfitting, feature importance, "
                      "preprocessing, train-test split, cross-validation, confusion matrix, ROC-AUC).",
        }

    llm = get_llm_provider()
    context = "\n\n".join(f"[{m['doc']}]\n{m['text']}" for m in matches)
    if llm.is_available():
        answer = llm.complete(
            system="Answer the user's question using ONLY the provided knowledge-base context. Be concise and clear for a beginner. If the context does not fully answer it, say so.",
            prompt=f"Context:\n{context}\n\nQuestion: {question}",
        )
    else:
        answer = matches[0]["text"].strip()

    return {"question": question, "matches": [{"doc": m["doc"], "score": m["score"]} for m in matches], "answer": answer}
