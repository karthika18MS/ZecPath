
"""
ZecPath Day 60 - Optimized AI Services
======================================

Features:
1. Local-only semantic model loading.
2. Model reuse within a Python process.
3. Batch semantic inference.
4. Optional bounded embedding cache.
5. Separate model-loading and inference timing.
6. Throughput metrics.
7. Batch-size benchmarking.
8. Clear error messages and cache monitoring.

This module is a helper for the existing ZecPath AI pipeline.
It does not replace the Day 18 ATS scoring engine.
"""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_BATCH_SIZE = 16

# Maximum number of individual text embeddings cached.
EMBEDDING_CACHE_SIZE = 4096

# Keep True to prevent Hugging Face network requests.
LOCAL_ONLY = True

RESULTS_DIR = (
    Path(__file__).resolve().parent / "results"
)


# ---------------------------------------------------------
# MODEL LOADING
# ---------------------------------------------------------

@lru_cache(maxsize=2)
def get_semantic_model(model_name: str = MODEL_NAME):
    """
    Load the semantic model once per Python process.

    local_files_only=True prevents attempts to download
    missing model files from Hugging Face.

    The model must already exist in the local cache.
    """

    try:
        from sentence_transformers import SentenceTransformer

    except ImportError as exc:
        raise RuntimeError(
            "sentence-transformers is not installed.\n"
            "Run: pip install sentence-transformers numpy"
        ) from exc

    started = time.perf_counter()

    try:
        model = SentenceTransformer(
            model_name,
            local_files_only=LOCAL_ONLY,
        )

    except Exception as exc:
        raise RuntimeError(
            f"Unable to load model '{model_name}' locally.\n"
            "Check that all model files are cached.\n"
            "Run the local model test before continuing.\n"
            f"Original error: {exc}"
        ) from exc

    elapsed = time.perf_counter() - started

    print(
        f"[MODEL] Loaded '{model_name}' locally "
        f"in {elapsed:.3f} seconds."
    )

    return model


# ---------------------------------------------------------
# TEXT NORMALIZATION
# ---------------------------------------------------------

def normalize_texts(
    texts: Iterable[Any],
) -> list[str]:
    """
    Convert inputs to strings and normalize whitespace.

    None values become empty strings.
    """

    normalized = []

    for value in texts:

        if value is None:
            normalized.append("")

        else:
            normalized.append(
                " ".join(str(value).split())
            )

    return normalized


# ---------------------------------------------------------
# CACHE KEY
# ---------------------------------------------------------

def text_fingerprint(
    text: str,
    model_name: str = MODEL_NAME,
) -> str:
    """
    Generate a stable key for a text and model combination.
    """

    payload = (
        f"{model_name}\0{text}"
        .encode("utf-8", errors="replace")
    )

    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------
# SINGLE-TEXT EMBEDDING CACHE
# ---------------------------------------------------------

@lru_cache(maxsize=EMBEDDING_CACHE_SIZE)
def _cached_single_embedding(
    fingerprint: str,
    text: str,
    model_name: str,
) -> tuple[float, ...]:
    """
    Calculate and cache a single normalized embedding.

    Cached vectors are stored as tuples to avoid exposing
    mutable NumPy arrays through the cache.
    """

    model = get_semantic_model(model_name)

    vector = model.encode(
        [text],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]

    return tuple(
        float(value) for value in vector
    )


# ---------------------------------------------------------
# SEMANTIC BATCH INFERENCE
# ---------------------------------------------------------

def encode_texts(
    texts: Iterable[Any],
    *,
    model_name: str = MODEL_NAME,
    batch_size: int = DEFAULT_BATCH_SIZE,
    use_cache: bool = False,
) -> tuple[np.ndarray, dict[str, Any]]:
    """
    Encode multiple texts into semantic embeddings.

    Returns:
        embeddings:
            NumPy array of embeddings.

        metrics:
            Model-load timing when applicable,
            inference timing, throughput and cache settings.

    Recommended:
        use_cache=False for bulk batch processing.
        use_cache=True for repeated individual texts.
    """

    if batch_size < 1:
        raise ValueError(
            "batch_size must be at least 1."
        )

    normalized = normalize_texts(texts)

    if not normalized:

        return np.empty(
            (0, 0),
            dtype=np.float32,
        ), {
            "item_count": 0,
            "batch_size": batch_size,
            "model_name": model_name,
            "model_load_seconds": 0.0,
            "inference_seconds": 0.0,
            "total_seconds": 0.0,
            "items_per_second": 0.0,
            "cache_enabled": use_cache,
        }

    # Load or retrieve the cached model before timing inference.
    model_started = time.perf_counter()

    model = get_semantic_model(model_name)

    model_access_seconds = (
        time.perf_counter() - model_started
    )

    inference_started = time.perf_counter()

    if use_cache:

        vectors = []

        for text in normalized:

            fingerprint = text_fingerprint(
                text,
                model_name,
            )

            vector = _cached_single_embedding(
                fingerprint,
                text,
                model_name,
            )

            vectors.append(vector)

        embeddings = np.asarray(
            vectors,
            dtype=np.float32,
        )

    else:

        embeddings = model.encode(
            normalized,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        embeddings = np.asarray(
            embeddings,
            dtype=np.float32,
        )

    inference_seconds = (
        time.perf_counter() - inference_started
    )

    total_seconds = (
        model_access_seconds + inference_seconds
    )

    metrics = {
        "item_count": len(normalized),
        "batch_size": batch_size,
        "model_name": model_name,
        "model_load_seconds": round(
            model_access_seconds, 6
        ),
        "inference_seconds": round(
            inference_seconds, 6
        ),
        "total_seconds": round(
            total_seconds, 6
        ),
        "items_per_second": round(
            len(normalized) / inference_seconds, 3
        ) if inference_seconds > 0 else 0.0,
        "cache_enabled": use_cache,
    }

    return embeddings, metrics


# ---------------------------------------------------------
# CACHE MANAGEMENT
# ---------------------------------------------------------

def clear_embedding_cache() -> None:
    """
    Remove cached embeddings.
    """

    _cached_single_embedding.cache_clear()

    print("[CACHE] Embedding cache cleared.")


def cache_info() -> dict[str, Any]:
    """
    Return embedding cache statistics.
    """

    info = _cached_single_embedding.cache_info()

    return {
        "hits": info.hits,
        "misses": info.misses,
        "maxsize": info.maxsize,
        "currsize": info.currsize,
    }


# ---------------------------------------------------------
# BATCH-SIZE BENCHMARK
# ---------------------------------------------------------

def benchmark_encoding(
    texts: Sequence[Any],
    batch_sizes: Sequence[int] = (1, 8, 16, 32),
    *,
    model_name: str = MODEL_NAME,
    repetitions: int = 3,
) -> list[dict[str, Any]]:
    """
    Compare inference performance for several batch sizes.

    The model is loaded before the benchmark starts.
    The first inference can still include warm-up overhead.

    Scores are not calculated here; only embeddings
    and timing metrics are measured.
    """

    if repetitions < 1:
        raise ValueError(
            "repetitions must be at least 1."
        )

    # Load once before benchmarking different batch sizes.
    get_semantic_model(model_name)

    rows = []

    for size in batch_sizes:

        if size < 1:
            raise ValueError(
                "All batch sizes must be positive."
            )

        run_times = []

        for repetition in range(repetitions):

            _, metrics = encode_texts(
                texts,
                model_name=model_name,
                batch_size=size,
                use_cache=False,
            )

            run_times.append(
                metrics["inference_seconds"]
            )

        average_time = (
            sum(run_times) / len(run_times)
        )

        item_count = len(texts)

        rows.append({
            "batch_size": size,
            "repetitions": repetitions,
            "average_inference_seconds": round(
                average_time, 6
            ),
            "best_inference_seconds": round(
                min(run_times), 6
            ),
            "items_per_second": round(
                item_count / average_time, 3
            ) if average_time > 0 else 0.0,
        })

    return rows


# ---------------------------------------------------------
# SAVE JSON RESULTS
# ---------------------------------------------------------

def save_json_report(
    report: dict[str, Any],
    filename: str,
) -> Path:
    """
    Save a JSON report in the Day 60 results directory.
    """

    import json

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = RESULTS_DIR / filename

    output_path.write_text(
        json.dumps(
            report,
            indent=4,
        ),
        encoding="utf-8",
    )

    return output_path


# ---------------------------------------------------------
# SMOKE TEST
# ---------------------------------------------------------

def main() -> None:

    sample_texts = [
        (
            "Python developer experienced in REST APIs "
            "and relational databases."
        ),
        (
            "Machine learning engineer experienced in "
            "NLP and model evaluation."
        ),
        (
            "Backend developer skilled in Python, APIs "
            "and database design."
        ),
    ]

    print("=" * 60)
    print("ZecPath Day 60 - Optimized AI Services")
    print("=" * 60)

    print("\n[TEST] Running semantic inference smoke test.")

    try:

        embeddings, metrics = encode_texts(
            sample_texts,
            batch_size=8,
            use_cache=False,
        )

        report = {
            "service": "ZecPath Day 60 Optimized AI Services",
            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": "PASS",
            "embedding_shape": list(
                embeddings.shape
            ),
            "metrics": metrics,
            "cache_info": cache_info(),
        }

        report_path = save_json_report(
            report,
            "optimized_ai_services_smoke_test.json",
        )

        print("\n[PASS] Semantic inference completed.")

        print(
            f"Embedding shape: {embeddings.shape}"
        )

        print("Metrics:", metrics)

        print("Cache:", cache_info())

        print(f"Report saved to: {report_path}")

    except Exception as exc:

        report = {
            "service": "ZecPath Day 60 Optimized AI Services",
            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": "FAIL",
            "error": str(exc),
        }

        report_path = save_json_report(
            report,
            "optimized_ai_services_smoke_test.json",
        )

        print("\n[FAIL] Semantic inference failed.")
        print(f"Reason: {exc}")
        print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
