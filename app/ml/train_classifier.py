"""
Synthetic dataset generator and training pipeline for Ticket Intent Classification.
Uses scikit-learn TF-IDF + Logistic Regression with rigorous train-test splitting,
stratification, metric calculation, and pipeline persistence.
"""

import os
import json
from pathlib import Path
from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score
)
import joblib

from app.config import settings, MODELS_DIR, SYNTHETIC_DIR

# -----------------------------------------------------------------------------
# 1. Synthetic Dataset Definition (Diverse, Reproducible Utterances)
# -----------------------------------------------------------------------------
SYNTHETIC_DATA: Dict[str, list[str]] = {
    "booking_confirmation": [
        "Can you send my booking confirmation email again?",
        "Did my hotel reservation go through for TRV1025?",
        "I haven't received confirmation for my Miami stay yet.",
        "Where can I find my itinerary and booking confirmation code?",
        "Please re-send my booking voucher and confirmation receipt.",
        "Is my reservation confirmed at Grand Horizon Resort?",
        "I want to verify if my hotel booking is active and confirmed.",
        "Can you confirm that my room is booked for tomorrow night?",
        "Need a copy of my booking confirmation document for visa purposes.",
        "I booked 10 minutes ago, where is my reservation confirmation?",
        "Please check if my booking reference TRV1025 is valid and active.",
        "Could you verify my booking status? I never got a confirmation text.",
        "I need the official confirmation voucher for check-in at the front desk.",
        "Is my hotel booking confirmed under Elena Rostova?",
        "Where is my reservation receipt? I need to print the confirmation.",
        "Can you check if my hotel booking is confirmed or pending?",
        "Confirmation email missing from my inbox for booking TRV1029.",
        "Please verify if my reservation was successfully booked.",
        "Can I get proof of my confirmed booking for my company expense report?",
        "Is my reservation secured for my upcoming trip next week?",
        "Send confirmation details for my room reservation please.",
        "Did the hotel receive my confirmation from your website?",
        "I need my confirmation number to check in online.",
        "Can you resend the confirmation letter for TRV1027?",
        "Check confirmation status for my holiday stay.",
    ],
    "cancellation": [
        "I need to cancel my hotel reservation TRV1026 immediately.",
        "Please cancel my hotel stay at Alpine Pine Lodge.",
        "How do I cancel my upcoming trip?",
        "Can I cancel my room without incurring penalty fees?",
        "Need to cancel my reservation due to a medical family emergency.",
        "Cancel booking TRV1029 please as my flights were cancelled.",
        "I won't be able to travel, please process cancellation.",
        "Cancel my reservation for next week and confirm when done.",
        "Is it possible to cancel my hotel room today?",
        "Please cancel booking TRV1027, my plans have changed.",
        "I want to cancel my reservation right now.",
        "Please abort my booking and cancel all hotel nights.",
        "How much does it cost to cancel my room at Grand Horizon?",
        "Requesting urgent cancellation for reservation TRV1025.",
        "Can I cancel my booking online or do you have to do it?",
        "I have to cancel our vacation reservation immediately.",
        "Please initiate the cancellation process for my booking.",
        "Cancel my room reservation, cannot make the journey.",
        "I am writing to cancel my hotel booking TRV1026.",
        "Cancel this reservation before the deadline passes.",
        "Please drop my reservation for Aspen this weekend.",
        "Need to cancel my stay, how soon will the cancellation take effect?",
        "Can you cancel my booking and send a cancellation confirmation?",
        "I want to void my room booking at Canal Bridge Hotel.",
        "Please cancel my hotel booking right away.",
    ],
    "refund": [
        "When will I get my refund back for the cancelled room?",
        "I was charged after cancelling and want a full refund.",
        "Please issue a full refund to my original credit card.",
        "Has my refund been processed yet for booking TRV1028?",
        "Where is my refund receipt and reference number?",
        "I need my money back for the cancelled booking.",
        "Why haven't I received my refund of $560.00 yet?",
        "How many business days does a refund take to appear in my bank?",
        "I am entitled to a 100% refund according to your cancellation policy.",
        "The hotel was closed, I demand an immediate refund.",
        "Can I get a refund for the unused night of my stay?",
        "Please verify if the refund of $1240.00 was approved.",
        "I cancelled within the free cancellation window, where is my refund?",
        "My refund status shows pending for over 10 days, please help.",
        "Requesting refund reimbursement for travel interruption.",
        "Why was my refund partial instead of full?",
        "Please release the refunded amount back to my debit card.",
        "Is there a refund processing fee deducted from my return?",
        "Can you expedite my refund payout?",
        "I need clarification on the refund amount credited to my account.",
        "When will the refund show up on my credit card statement?",
        "The room was uninhabitable, refund my money immediately.",
        "Check the refund status for cancelled reservation TRV1028.",
        "Please credit the refund back to PayPal.",
        "How long do refunds take for international bookings?",
    ],
    "booking_modification": [
        "Can I change my check-in date to next Friday?",
        "I need to add another guest to my room reservation.",
        "Can we change from a Queen room to an Ocean View King bed suite?",
        "Please modify my travel dates for booking TRV1027.",
        "Can I extend my stay by two extra nights at the hotel?",
        "Need to change the primary guest name on the reservation.",
        "Is it possible to reschedule my booking to next month?",
        "I want to arrive one day early, can you adjust my booking?",
        "Can I shorten my reservation by one night?",
        "Please upgrade my room type for booking TRV1025.",
        "How do I modify my hotel dates without cancelling the booking?",
        "Can I switch my reservation to a different branch of the hotel?",
        "Please update the contact phone number and guest count on my file.",
        "I need to reschedule our vacation dates due to work conflicts.",
        "Can we change our check-out date from Tuesday to Thursday?",
        "Please change the booking name to my colleague's name.",
        "How do I add breakfast to my existing hotel reservation?",
        "Can I modify the room preference to non-smoking and high floor?",
        "We want to change our suite type, what is the price difference?",
        "Please amend my booking dates for TRV1029.",
        "Can you push my check-in back by two days?",
        "I would like to update the guest details for my stay.",
        "Requesting a date change on my pending reservation.",
        "Can we shift our trip dates to the following weekend?",
        "Modify my reservation to include two twin beds instead of one king.",
    ],
    "payment_issue": [
        "My credit card was declined during hotel checkout payment.",
        "I was charged twice on my card for booking TRV1030.",
        "I received a payment failed notification, how can I retry?",
        "Can I switch my payment method for my upcoming hotel stay?",
        "Payment error occurred while processing my card.",
        "Why is my payment status showing failed for TRV1030?",
        "There is an unexpected charge on my bank statement from your site.",
        "Can I pay with a different credit card at the hotel upon arrival?",
        "My card was debited but the website says payment not received.",
        "How do I update an expired credit card on my active reservation?",
        "I keep getting an invalid CVV payment error code.",
        "Can I pay with PayPal or Apple Pay instead of card?",
        "Why was I billed in USD instead of EUR?",
        "The payment gateway crashed when I clicked complete booking.",
        "Need help resolving a failed payment transaction for my booking.",
        "I got an unauthorized duplicate charge for $780.00.",
        "Payment verification link expired, can you send a new link?",
        "Can you verify if my payment of $890.50 was successfully cleared?",
        "The system says payment pending, but funds were deducted from my bank.",
        "How do I clear the payment error on my account?",
        "Can I split the payment between two credit cards?",
        "The hotel front desk says my booking isn't paid, but you charged me.",
        "Payment failed due to 3D Secure verification timeout.",
        "Please help me complete the payment for my pending reservation.",
        "Why did my transaction fail on the payment screen?",
    ],
    "general_travel_query": [
        "What time is check-in and check-out at the resort?",
        "Does Grand Horizon Resort offer free Wi-Fi and valet parking?",
        "Is breakfast included in my room rate or is it an extra charge?",
        "Do you have an airport shuttle service from Miami International?",
        "Are pets allowed in the hotel rooms?",
        "What amenities does Alpine Pine Lodge offer in the winter?",
        "Can the hotel store our luggage before our room is ready?",
        "Is there an age requirement to check in at the front desk?",
        "Do the rooms have a mini-fridge and coffee maker?",
        "How far is the hotel from the downtown city center and metro?",
        "Does the hotel have an indoor swimming pool and fitness gym?",
        "Can I request a quiet room on an upper floor away from the elevator?",
        "Are there vegetarian dining options available in the hotel restaurant?",
        "What is the hotel's policy on smoking and noise hours?",
        "Is the front desk open 24 hours for early morning departures?",
        "Does the resort charge a daily resort fee upon arrival?",
        "What electrical outlet plugs are used in the hotel rooms?",
        "Can the hotel concierge arrange local sightseeing tours?",
        "Is tap water drinkable at the property?",
        "Do you provide baby cribs or extra rollaway beds?",
        "What is the distance between the hotel and the beach?",
        "Are there conference and meeting facilities at the hotel?",
        "Can I receive postal packages at the hotel front desk before arrival?",
        "Is there a spa and sauna available for hotel guests?",
        "What are the restaurant opening hours for dinner?",
    ],
}


def build_synthetic_dataframe() -> pd.DataFrame:
    """Flattens the synthetic dictionary into a Pandas DataFrame."""
    rows = []
    for intent, examples in SYNTHETIC_DATA.items():
        for text in examples:
            rows.append({"text": text, "intent": intent})
    df = pd.DataFrame(rows)
    return df


def train_and_evaluate_classifier(
    df: pd.DataFrame,
    test_size: float = 0.20,
    random_state: int = 42
) -> Tuple[Pipeline, Dict[str, Any]]:
    """
    Trains a TF-IDF + LogisticRegression pipeline with strict train-test separation
    to prevent data leakage, and computes comprehensive evaluation metrics.
    """
    X = np.array(df["text"].tolist(), dtype=object)
    y = np.array(df["intent"].tolist(), dtype=object)

    # Stratified split ensures all 6 intents are represented proportionally in train & test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Scikit-learn Pipeline prevents TF-IDF leakage from test set
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1,
            strip_accents="unicode",
            lowercase=True
        )),
        ("clf", LogisticRegression(
            C=1.5,
            max_iter=1000,
            class_weight="balanced",
            random_state=random_state
        ))
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate on held-out test set
    y_pred = pipeline.predict(X_test)
    classes = list(np.unique(y))

    acc = float(accuracy_score(y_test, y_pred))
    macro_f1 = float(f1_score(y_test, y_pred, average="macro"))
    macro_prec = float(precision_score(y_test, y_pred, average="macro"))
    macro_rec = float(recall_score(y_test, y_pred, average="macro"))
    
    report_dict = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=classes).tolist()

    metrics = {
        "model_architecture": "TF-IDF (1,2 n-grams) + LogisticRegression (balanced)",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "total_samples": len(df),
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "macro_precision": round(macro_prec, 4),
        "macro_recall": round(macro_rec, 4),
        "classes": classes,
        "confusion_matrix": cm,
        "per_class_report": {
            cls: {
                "precision": round(report_dict[cls]["precision"], 4),
                "recall": round(report_dict[cls]["recall"], 4),
                "f1_score": round(report_dict[cls]["f1-score"], 4),
                "support": int(report_dict[cls]["support"])
            }
            for cls in classes if cls in report_dict
        },
        "dataset_disclaimer": "Trained on synthetic travel support utterances. Not validated on production customer data."
    }

    return pipeline, metrics


def save_model_artifacts(pipeline: Pipeline, metrics: Dict[str, Any]):
    """Saves the fitted model and evaluation metrics to disk."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)

    model_path = Path(settings.CLASSIFIER_PATH)
    metrics_path = Path(settings.CLASSIFIER_METRICS_PATH)
    data_path = SYNTHETIC_DIR / "intent_training_data.csv"

    # Save training dataset for reproducibility
    df = build_synthetic_dataframe()
    df.to_csv(data_path, index=False)

    # Save pipeline and metrics
    joblib.dump(pipeline, model_path)
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Classifier saved to: {model_path}")
    print(f"Metrics saved to: {metrics_path}")
    print(f"Accuracy: {metrics['accuracy']:.2%}, Macro-F1: {metrics['macro_f1']:.2%}")


def run_training_pipeline() -> Dict[str, Any]:
    """Top-level function to generate data, train, evaluate, and save artifacts."""
    df = build_synthetic_dataframe()
    pipeline, metrics = train_and_evaluate_classifier(df)
    save_model_artifacts(pipeline, metrics)
    return metrics


if __name__ == "__main__":
    run_training_pipeline()
