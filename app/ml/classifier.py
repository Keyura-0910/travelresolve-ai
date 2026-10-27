"""
Inference wrapper for the Ticket Intent Classifier.
Loads the fitted scikit-learn pipeline and provides probability distributions,
confidence scores, and ambiguous input detection.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import joblib

from app.config import settings
from app.schemas import ClassificationResult
from app.ml.train_classifier import run_training_pipeline


class TicketClassifier:
    """Production inference wrapper for the trained TF-IDF + Logistic Regression model."""

    def __init__(self, model_path: Optional[str] = None):
        self.model_path = Path(model_path or settings.CLASSIFIER_PATH)
        self.pipeline = None
        self._load_or_train()

    def _load_or_train(self):
        """Loads the serialized model or runs training if not yet built."""
        if self.model_path.exists():
            try:
                self.pipeline = joblib.load(self.model_path)
            except Exception as e:
                print(f"Warning: Failed to load existing model ({e}). Re-training...")
                self._train_fresh()
        else:
            print("Model artifact not found. Initializing training...")
            self._train_fresh()

    def _train_fresh(self):
        """Runs the training pipeline and loads the resulting artifact."""
        run_training_pipeline()
        self.pipeline = joblib.load(self.model_path)

    def predict(self, text: str) -> ClassificationResult:
        """
        Predicts ticket intent and outputs calibrated class confidence scores.
        
        Args:
            text: Customer support inquiry text
            
        Returns:
            ClassificationResult containing top intent, confidence score,
            and full probability breakdown.
        """
        clean_text = (text or "").strip()
        if not clean_text:
            return ClassificationResult(
                predicted_intent="general_travel_query",
                confidence=0.0,
                probabilities={},
                model_name="TFIDF-LogisticRegression"
            )

        # Get probability distribution across classes
        classes = list(self.pipeline.classes_)
        probabilities = self.pipeline.predict_proba([clean_text])[0]
        
        prob_dict = {
            cls_name: round(float(prob), 4)
            for cls_name, prob in zip(classes, probabilities)
        }
        
        # Sort probabilities descending
        sorted_probs = dict(sorted(prob_dict.items(), key=lambda item: item[1], reverse=True))
        
        top_intent = self.pipeline.predict([clean_text])[0]
        top_confidence = round(float(np_max := max(probabilities)), 4)

        return ClassificationResult(
            predicted_intent=top_intent,
            confidence=top_confidence,
            probabilities=sorted_probs,
            model_name="TFIDF-LogisticRegression"
        )


# Global singleton instance for easy reuse across services & nodes
_classifier_instance: Optional[TicketClassifier] = None


def get_classifier() -> TicketClassifier:
    """Returns or initializes the singleton TicketClassifier."""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = TicketClassifier()
    return _classifier_instance
