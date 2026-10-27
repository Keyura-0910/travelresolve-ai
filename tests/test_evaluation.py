"""
Tests for Resolution Quality Lab and Evaluation Engine.
Verifies synthetic dataset generation, metric math, and benchmark execution.
"""

from app.services.evaluation_service import (
    generate_synthetic_eval_dataset,
    run_benchmark_evaluation
)


def test_eval_dataset_generation():
    dataset = generate_synthetic_eval_dataset(num_cases=100)
    assert len(dataset) == 100
    for case in dataset:
        assert "case_id" in case
        assert "customer_message" in case
        assert "expected_intent" in case
        assert "expected_policy_id" in case
        assert "expected_should_escalate" in case


def test_benchmark_evaluation_sample():
    # Run a fast 10-case evaluation to verify metric computation
    results = run_benchmark_evaluation(sample_limit=10)
    assert results["total_cases_evaluated"] == 10
    assert 0.0 <= results["intent_accuracy"] <= 1.0
    assert 0.0 <= results["retrieval_recall_at_k"] <= 1.0
    assert 0.0 <= results["escalation_precision"] <= 1.0
    assert 0.0 <= results["escalation_recall"] <= 1.0
    assert "Baseline (Prompt only)" in results["system_comparison"]
    assert "TravelResolve AI (Full Workflow)" in results["system_comparison"]
