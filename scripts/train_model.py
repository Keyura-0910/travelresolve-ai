"""
Script to train the TF-IDF + Logistic Regression Intent Classifier.
"""

import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.ml.train_classifier import run_training_pipeline


def main():
    print("Starting ML Intent Classifier training on synthetic travel utterances...")
    metrics = run_training_pipeline()
    print("=" * 60)
    print("TRAINING & EVALUATION SUMMARY:")
    print(f"Total Samples: {metrics['total_samples']} (Train: {metrics['train_samples']}, Test: {metrics['test_samples']})")
    print(f"Test Accuracy: {metrics['accuracy']:.2%}")
    print(f"Macro-F1 Score: {metrics['macro_f1']:.2%}")
    print(f"Macro-Precision: {metrics['macro_precision']:.2%}")
    print(f"Macro-Recall: {metrics['macro_recall']:.2%}")
    print("=" * 60)
    print("Model pipeline and evaluation metrics successfully saved to disk.")


if __name__ == "__main__":
    main()
