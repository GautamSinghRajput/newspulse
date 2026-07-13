"""
cluster.py
Embeds articles locally (no API key needed) and clusters them into themes.
"""

from typing import List, Dict
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

_model = None


def _get_model():
    """Lazy-load the embedding model so app startup stays fast."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_articles(articles) -> np.ndarray:
    model = _get_model()
    texts = [f"{a.title}. {a.text}" for a in articles]
    return model.encode(texts, show_progress_bar=False, normalize_embeddings=True)


def choose_k(embeddings: np.ndarray, min_k: int = 2, max_k: int = 8) -> int:
    """Pick the cluster count with the best silhouette score."""
    n = len(embeddings)
    max_k = min(max_k, n - 1)
    if n < 4:
        return 1
    best_k, best_score = min_k, -1
    for k in range(min_k, max_k + 1):
        labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(embeddings)
        if len(set(labels)) < 2:
            continue
        score = silhouette_score(embeddings, labels)
        if score > best_score:
            best_k, best_score = k, score
    return best_k


def cluster_articles(articles, embeddings: np.ndarray, k: int = None) -> Dict[int, list]:
    """Return {cluster_id: [articles]} grouping."""
    if len(articles) < 4:
        return {0: articles}

    k = k or choose_k(embeddings)
    labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit_predict(embeddings)

    clusters: Dict[int, list] = {}
    for label, article in zip(labels, articles):
        clusters.setdefault(int(label), []).append(article)
    return clusters
