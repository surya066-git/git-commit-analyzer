import os
import joblib
from preprocessing.text_cleaner import clean_text

class CommitClassifier:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'classifier.pkl')
        self.tfidf_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'tfidf.pkl')
        self.classifier = None
        self.vectorizer = None
        self._load_models()

    def _load_models(self):
        try:
            self.classifier = joblib.load(self.model_path)
            self.vectorizer = joblib.load(self.tfidf_path)
        except Exception as e:
            print(f"Warning: Could not load models: {e}")
            self.classifier = None
            self.vectorizer = None

    def predict(self, commit_message: str) -> tuple[str, float]:
        if not self.classifier or not self.vectorizer:
            return "OTHER", 0.0
            
        cleaned = clean_text(commit_message)
        if not cleaned.strip():
            return "OTHER", 0.0

        features = self.vectorizer.transform([cleaned])
        
        # Get category
        category = self.classifier.predict(features)[0]
        
        # Get confidence (probability of predicted class)
        probs = self.classifier.predict_proba(features)[0]
        class_index = self.classifier.classes_.tolist().index(category)
        confidence = float(probs[class_index])
        
        return category, confidence

classifier_service = CommitClassifier()
