"""
Script to execute the 100-case comparative evaluation benchmark.
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.evaluation_service import run_benchmark_evaluation


def main():
    print("Executing 100-case evaluation benchmark across 3 system architectures...")
    results = run_benchmark_evaluation(100)
    print("=" * 65)
    print("BENCHMARK EVALUATION RESULTS:")
    print(f"Total Evaluated Cases: {results['total_cases_evaluated']}")
    print(f"Intent Classification Accuracy: {results['intent_accuracy']:.2%}")
    print(f"RAG Retrieval Recall@k: {results['retrieval_recall_at_k']:.2%}")
    print(f"Booking Field Accuracy: {results['booking_field_accuracy']:.2%}")
    print(f"Escalation Precision: {results['escalation_precision']:.2%}")
    print(f"Escalation Recall: {results['escalation_recall']:.2%}")
    print(f"Eligible Resolution Rate: {results['eligible_resolution_rate']:.2%}")
    print(f"Average Workflow Latency: {results['average_latency_ms']:.1f} ms")
    print("=" * 65)
    print("Architecture Comparison:")
    for arch, data in results["system_comparison"].items():
        print(f"  - {arch}: Auditor Pass Rate = {data['auditor_pass_rate']:.1%}, Latency = {data['average_latency_ms']} ms")
    print("=" * 65)
    print("Evaluation results cached to data/synthetic/evaluation_results.json.")


if __name__ == "__main__":
    main()
