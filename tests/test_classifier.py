"""
Tests for ML Intent Classification Pipeline.
Verifies training, loading, all 6 intent classes, and ambiguous inputs.
"""

import pytest
from app.ml.train_classifier import build_synthetic_dataframe, train_and_evaluate_classifier
from app.ml.classifier import TicketClassifier, get_classifier


def test_synthetic_dataset_structure():
    df = build_synthetic_dataframe()
    assert len(df) >= 120
    assert "text" in df.columns
    assert "intent" in df.columns
    intents = set(df["intent"].unique())
    expected = {
        "booking_confirmation",
        "cancellation",
        "refund",
        "booking_modification",
        "payment_issue",
        "general_travel_query"
    }
    assert intents == expected


def test_classifier_training_metrics():
    df = build_synthetic_dataframe()
    pipeline, metrics = train_and_evaluate_classifier(df, test_size=0.20)
    assert metrics["accuracy"] >= 0.80
    assert metrics["macro_f1"] >= 0.80
    assert len(metrics["classes"]) == 6


def test_all_intent_predictions():
    classifier = get_classifier()
    
    test_cases = [
        ("Where is my booking confirmation email for TRV1025?", "booking_confirmation"),
        ("I need to cancel my hotel reservation immediately.", "cancellation"),
        ("When will my refund be processed back to my bank account?", "refund"),
        ("Can I change my check-in date to next Friday?", "booking_modification"),
        ("My credit card was declined and payment failed.", "payment_issue"),
        ("What time is check-in and is breakfast included?", "general_travel_query"),
    ]

    for utterance, expected_intent in test_cases:
        res = classifier.predict(utterance)
        assert res.predicted_intent == expected_intent
        assert res.confidence > 0.30
        assert len(res.probabilities) == 6


def test_ambiguous_and_empty_inputs():
    classifier = get_classifier()

    # Empty string should not crash
    empty_res = classifier.predict("")
    assert empty_res.predicted_intent in ["general_travel_query"]

    # Ambiguous input should return distributed probabilities
    ambiguous_res = classifier.predict("hello maybe please something hotel")
    assert len(ambiguous_res.probabilities) == 6
