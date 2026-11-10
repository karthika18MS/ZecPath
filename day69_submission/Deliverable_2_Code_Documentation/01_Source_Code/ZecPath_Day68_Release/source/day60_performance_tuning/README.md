# ZecPath Day 60 — Optimized AI Services

## Included
- `optimized_ai_services.py`: reusable semantic model loader, batch inference, bounded optional embedding cache, and timing metrics.
- `README.md`: integration and validation notes.

## Install
Activate the existing ZecPath virtual environment, then run:

```bat
pip install sentence-transformers numpy
```

## Smoke test
From the ZecPath project root:

```bat
python day60_performance_tuning\optimized_ai_services.py
```

If you put this file in the `day60_performance_tuning` folder, it can also be imported as:

```python
from day60_performance_tuning.optimized_ai_services import (
    encode_texts,
    get_semantic_model,
    cache_info,
    clear_embedding_cache,
)
```

## Example integration
```python
embeddings, metrics = encode_texts(
    candidate_texts,
    batch_size=16,
    use_cache=False,
)
print(metrics)
```

Use the embeddings in the existing semantic similarity calculation. This helper does not implement the complete ATS score and should not replace the existing Day 18 engine.

## Important validation
1. Keep a copy of existing outputs before integration.
2. Compare old and new semantic similarity results for the same candidates and job descriptions.
3. Verify final ATS scores remain consistent within a defined numerical tolerance.
4. Benchmark multiple runs; the first run may include model-loading overhead.
5. Test batch sizes against available RAM before increasing them.
6. The optional single-text cache is bounded, but embeddings still consume memory. Clear it when needed.
7. This is a proposed optimized helper, not proof that the complete ZecPath system has already been optimized.
