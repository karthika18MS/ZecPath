
"""
ZecPath Day 60 - Batch Performance Benchmark
============================================

Tests semantic inference with different batch sizes.
Saves the results as JSON in the Day 60 results folder.

Run from the ZecPath project root:
    python day60_performance_tuning\run_batch_benchmark.py
"""

import sys
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------
# PATH CONFIGURATION
# ---------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Allow imports from the directory containing this script.
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# Import sibling module after configuring the path.
from optimized_ai_services import (
    benchmark_encoding,
    get_semantic_model,
    save_json_report,
)


# ---------------------------------------------------------
# BENCHMARK INPUT
# ---------------------------------------------------------

SAMPLE_TEXTS = [
    "Python developer experienced in REST APIs and relational databases.",
    "Machine learning engineer experienced in NLP and model evaluation.",
    "Backend developer skilled in Python, APIs and database design.",
    "Software engineer experienced in testing, debugging and application development.",
    "Data analyst skilled in Python, SQL and data visualization.",
    "Full stack developer experienced in React, Node.js and MongoDB.",
    "Cloud engineer experienced in deployment, monitoring and automation.",
    "QA engineer experienced in test cases, automation and defect tracking.",
    "Java developer experienced in object-oriented programming and backend services.",
    "AI engineer experienced in semantic search and machine learning models.",
]


# ---------------------------------------------------------
# MAIN BENCHMARK
# ---------------------------------------------------------

def main():
    print("=" * 65)
    print("ZecPath Day 60 - Batch Performance Benchmark")
    print("=" * 65)

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Texts to process: {len(SAMPLE_TEXTS)}")
    print("Batch sizes: 1, 8, 16, 32")
    print("Repetitions per batch size: 3")

    try:
        # Load the model before measuring batch inference.
        print("\n[1/3] Loading local semantic model...")
        get_semantic_model()

        # Benchmark each batch size.
        print("\n[2/3] Running benchmark...")
        results = benchmark_encoding(
            SAMPLE_TEXTS,
            batch_sizes=(1, 8, 16, 32),
            repetitions=3,
        )

        # Build the report.
        report = {
            "benchmark": "ZecPath Day 60 Batch Benchmark",
            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "status": "PASS",
            "model": (
                "sentence-transformers/all-MiniLM-L6-v2"
            ),
            "text_count": len(SAMPLE_TEXTS),
            "batch_sizes": [1, 8, 16, 32],
            "repetitions_per_batch_size": 3,
            "results": results,
            "notes": [
                "Uses synthetic sample texts.",
                "Model is loaded before batch timing.",
                "First inference may include warm-up overhead.",
                "Timing measures inference, not the full ATS pipeline.",
                "Results must be measured; no speed improvement is assumed.",
            ],
        }

        print("\n[3/3] Saving benchmark report...")
        output_path = save_json_report(
            report,
            "batch_performance_benchmark.json",
        )

        # Display summary.
        print("\n" + "=" * 65)
        print("BENCHMARK RESULTS")
        print("=" * 65)

        for row in results:
            print(
                f"Batch size: {row['batch_size']:>2} | "
                f"Average inference: "
                f"{row['average_inference_seconds']:.6f} sec | "
                f"Best inference: "
                f"{row['best_inference_seconds']:.6f} sec | "
                f"Throughput: "
                f"{row['items_per_second']:.3f} texts/sec"
            )

        if results:
            best = max(
                results,
                key=lambda row: row["items_per_second"],
            )

            print(
                f"\nHighest measured throughput: "
                f"batch size {best['batch_size']} "
                f"({best['items_per_second']:.3f} texts/sec)"
            )

        print(f"\nReport saved to:\n{output_path}")
        print("\nBenchmark completed successfully.")

    except Exception as exc:
        print("\n[FAIL] Benchmark could not complete.")
        print(f"Error: {type(exc).__name__}: {exc}")
        print(
            "\nCheck that optimized_ai_services.py exists in "
            "the day60_performance_tuning folder and that "
            "the local model is available."
        )
        raise


if __name__ == "__main__":
    main()
