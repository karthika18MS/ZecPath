
"""
ZecPath - Semantic Matching Model
Day 60: Performance Tuning & Scalability

Purpose:
- Preserve Day 17 semantic score calculations.
- Reuse the Day 60 optimized semantic model service.
- Load the model from the local cache.
- Support batched embedding generation.
- Preserve the existing score output fields.
"""

from functools import lru_cache

from sklearn.metrics.pairwise import cosine_similarity

from day60_performance_tuning.optimized_ai_services import (
    get_semantic_model as get_day60_semantic_model,
    encode_texts,
)


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def normalize_text(text):
    """
    Normalize text using the original Day 17 approach.

    Converts text to lowercase, replaces the original
    encoded dash strings, and collapses extra whitespace.
    """
    if text is None:
        return ""

    text = str(text).lower()
    text = text.replace("ΓÇô", "-")
    text = text.replace("ΓÇö", "-")
    text = " ".join(text.split())

    return text


@lru_cache(maxsize=1)
def get_semantic_model():
    """
    Get the cached model through the Day 60 optimized service.

    The underlying service loads the model locally and reuses
    the same model instance across calls.
    """
    return get_day60_semantic_model(MODEL_NAME)


def calculate_semantic_similarity(resume_text, job_description):
    """
    Calculate semantic similarity between a resume and job description.

    The text normalization and cosine similarity calculation follow
    the Day 17 implementation. Embeddings are generated through
    the optimized Day 60 service.

    Returns:
        dict: Semantic score, raw score, and embedding dimensions.
    """
    # Step 1: Normalize both inputs using Day 17 rules.
    resume_text = normalize_text(resume_text)
    job_description = normalize_text(job_description)

    # Step 2: Validate the input text.
    if not resume_text:
        raise ValueError("Resume text is empty.")

    if not job_description:
        raise ValueError("Job description text is empty.")

    # Step 3: Generate embeddings using the Day 60 service.
    embeddings, metrics = encode_texts(
        [resume_text, job_description],
        model_name=MODEL_NAME,
        batch_size=2,
        use_cache=False,
    )

    # Step 4: Calculate cosine similarity.
    similarity = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]],
    )

    raw_score = float(similarity[0][0])
    percentage = raw_score * 100

    # Step 5: Return the expected score fields.
    return {
        "score": round(percentage, 2),
        "raw_score": round(raw_score, 4),
        "embedding_length": int(embeddings.shape[1]),
    }
