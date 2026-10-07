"""
TF-IDF Retriever
Core Data Science component of the chatbot.

Pipeline:
    1. Receive text chunks (list of dicts with 'text', 'source', 'type').
    2. Preprocess all chunk texts and the user's question.
    3. Fit a TF-IDF vectorizer on all chunk texts.
    4. For each question, compute cosine similarity between the question
       vector and all chunk vectors.
    5. Return the top-K most relevant chunks.
    6. Extract the most relevant sentences from those chunks as the answer.
"""

import re
import string
from typing import List, Dict, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
import numpy as np  # type: ignore


# ─────────────────────────────────────────────
# Text Preprocessing
# ─────────────────────────────────────────────

# Common English stopwords (subset – avoids NLTK download requirement)
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "dare",
    "ought", "used", "it", "its", "this", "that", "these", "those", "i",
    "me", "my", "we", "our", "you", "your", "he", "his", "she", "her",
    "they", "their", "what", "which", "who", "whom", "how", "when", "where",
    "why", "not", "no", "so", "if", "as", "about", "into", "through",
    "during", "before", "after", "above", "below", "between", "out", "up",
    "down", "then", "than", "also", "just", "more", "most", "other",
    "such", "like", "very", "still", "over", "each", "both", "few",
    "some", "any", "all", "there"
}


def preprocess_text(text: str) -> str:
    """
    Clean and normalize text for TF-IDF processing.

    Steps:
        - Lowercase
        - Remove punctuation
        - Normalize whitespace
        - Remove stopwords
    """
    if not text:
        return ""

    # Lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Remove stopwords
    tokens = text.split()
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 1]

    return " ".join(tokens)


# ─────────────────────────────────────────────
# Text Chunking
# ─────────────────────────────────────────────

def chunk_text(text: str, source: str, file_type: str,
               chunk_size: int = 150, overlap: int = 30) -> List[Dict]:
    """
    Split a large text into overlapping word-based chunks.

    Args:
        text       : Raw extracted text.
        source     : Original filename (for metadata).
        file_type  : 'pdf', 'txt', 'image', 'audio', 'video' (for metadata).
        chunk_size : Number of words per chunk.
        overlap    : Number of words to overlap between adjacent chunks.

    Returns:
        List of chunk dicts: {'text': ..., 'source': ..., 'type': ...}
    """
    if not text or not text.strip():
        return []

    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text_str = " ".join(chunk_words).strip()

        if chunk_text_str:
            chunks.append({
                "text": chunk_text_str,
                "source": source,
                "type": file_type
            })

        # Move forward by (chunk_size - overlap)
        step = chunk_size - overlap
        if step <= 0:
            step = 1
        start += step

    return chunks


# ─────────────────────────────────────────────
# TF-IDF Retriever Class
# ─────────────────────────────────────────────

class TFIDFRetriever:
    """
    Builds a TF-IDF index over text chunks and answers questions
    using cosine similarity retrieval.
    """

    def __init__(self, similarity_threshold: float = 0.05, top_k: int = 3):
        """
        Args:
            similarity_threshold : Minimum cosine similarity to consider a chunk relevant.
            top_k                : Number of top chunks to retrieve.
        """
        self.similarity_threshold = similarity_threshold
        self.top_k = top_k

        self.chunks: List[Dict] = []          # Raw chunk dicts
        self.processed_texts: List[str] = []  # Preprocessed chunk texts
        self.vectorizer = TfidfVectorizer(
            max_features=10000,
            ngram_range=(1, 2),   # Unigrams + bigrams
            sublinear_tf=True     # Apply log normalization to TF
        )
        self.tfidf_matrix = None
        self.is_fitted = False

    def add_chunks(self, chunks: List[Dict]) -> None:
        """Add a list of chunk dicts to the knowledge base."""
        for chunk in chunks:
            if chunk.get("text", "").strip():
                self.chunks.append(chunk)
                self.processed_texts.append(preprocess_text(chunk["text"]))

    def build_index(self) -> bool:
        """
        Fit the TF-IDF vectorizer on all stored chunks.

        Returns:
            True if index was built successfully, False otherwise.
        """
        if not self.chunks:
            print("[ERROR] No chunks available to build the index.")
            return False

        # Filter out any empty preprocessed texts
        valid_pairs = [
            (chunk, pt)
            for chunk, pt in zip(self.chunks, self.processed_texts)
            if pt.strip()
        ]

        if not valid_pairs:
            print("[ERROR] All chunks became empty after preprocessing.")
            return False

        self.chunks, self.processed_texts = zip(*valid_pairs)
        self.chunks = list(self.chunks)
        self.processed_texts = list(self.processed_texts)

        try:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_texts)
            self.is_fitted = True
            print(f"[INFO] TF-IDF index built: {len(self.chunks)} chunks, "
                  f"{self.tfidf_matrix.shape[1]} features.")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to build TF-IDF index: {e}")
            return False

    def retrieve(self, question: str) -> List[Tuple[Dict, float]]:
        """
        Find the most relevant chunks for a given question.

        Args:
            question: The user's question string.

        Returns:
            List of (chunk_dict, similarity_score) tuples, sorted descending.
        """
        if not self.is_fitted:
            return []

        question_processed = preprocess_text(question)

        if not question_processed.strip():
            return []

        try:
            question_vec = self.vectorizer.transform([question_processed])
            similarities = cosine_similarity(question_vec, self.tfidf_matrix)[0]

            # Get indices sorted by descending similarity
            ranked_indices = np.argsort(similarities)[::-1]

            results = []
            for idx in ranked_indices[:self.top_k]:
                score = float(similarities[idx])
                if score >= self.similarity_threshold:
                    results.append((self.chunks[idx], score))

            return results

        except Exception as e:
            print(f"[ERROR] Retrieval failed: {e}")
            return []

    def answer(self, question: str) -> Tuple[str, str]:
        """
        Generate an extractive answer for the given question.

        Args:
            question: The user's question.

        Returns:
            (answer_text, source_filename) tuple.
        """
        results = self.retrieve(question)

        if not results:
            return (
                "I could not find enough relevant information in the uploaded files.",
                ""
            )

        # Use the top chunk as the primary source
        top_chunk, top_score = results[0]

        # Extract the most relevant sentences from the top chunks
        # Combine text from all retrieved chunks (deduplicated by source similarity)
        combined_text = " ".join(r[0]["text"] for r in results)

        answer_sentences = _extract_relevant_sentences(
            combined_text, question, max_sentences=4
        )

        if not answer_sentences:
            # Fall back to returning the top chunk directly
            answer_text = top_chunk["text"][:600]
        else:
            answer_text = " ".join(answer_sentences)

        source = top_chunk["source"]
        return answer_text, source

    @property
    def chunk_count(self) -> int:
        """Total number of chunks in the knowledge base."""
        return len(self.chunks)

    @property
    def document_count(self) -> int:
        """Number of unique source documents."""
        return len(set(c["source"] for c in self.chunks))


# ─────────────────────────────────────────────
# Sentence Extraction Helper
# ─────────────────────────────────────────────

def _split_into_sentences(text: str) -> List[str]:
    """Simple sentence splitter using punctuation."""
    # Split on '. ', '! ', '? ', '\n'
    sentence_endings = re.compile(r'(?<=[.!?])\s+|\n+')
    sentences = sentence_endings.split(text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def _extract_relevant_sentences(text: str, question: str,
                                 max_sentences: int = 4) -> List[str]:
    """
    From the retrieved chunk text, extract sentences most relevant
    to the question using simple keyword overlap.

    Args:
        text         : Combined text from retrieved chunks.
        question     : User's question.
        max_sentences: Max number of sentences to return.

    Returns:
        List of relevant sentence strings.
    """
    sentences = _split_into_sentences(text)

    if not sentences:
        return []

    # Get question keywords (after preprocessing)
    q_processed = preprocess_text(question)
    q_keywords = set(q_processed.split())

    if not q_keywords:
        return sentences[:max_sentences]

    # Score each sentence by keyword overlap
    scored = []
    for sent in sentences:
        sent_words = set(preprocess_text(sent).split())
        overlap = len(q_keywords & sent_words)
        scored.append((sent, overlap))

    # Sort by overlap score (descending), then by position (ascending)
    scored.sort(key=lambda x: -x[1])

    # Return top sentences (preserve original order for readability)
    top_sentences = [s for s, score in scored[:max_sentences] if score > 0]

    if not top_sentences:
        # No keyword overlap — just return the first few sentences
        top_sentences = sentences[:max_sentences]

    # Re-sort by their original position in the sentence list
    original_order = {s: i for i, s in enumerate(sentences)}
    top_sentences.sort(key=lambda s: original_order.get(s, 999))

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for s in top_sentences:
        normalized = s.lower().strip()
        if normalized not in seen:
            seen.add(normalized)
            deduped.append(s)

    return deduped
