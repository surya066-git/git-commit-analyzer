import os
import sys
import pandas as pd
import joblib
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, confusion_matrix
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.text_cleaner import clean_text

def evaluate_model():
    test_path = os.path.join('evaluation', 'test_set.csv')
    model_path = os.path.join('models', 'classifier.pkl')
    tfidf_path = os.path.join('models', 'tfidf.pkl')

    if not (os.path.exists(test_path) and os.path.exists(model_path) and os.path.exists(tfidf_path)):
        print("Missing required files (test set or models). Run train.py first.")
        return

    print("Loading test data and models...")
    test_df = pd.read_csv(test_path)
    
    # Handle NaN values explicitly
    test_df['message'] = test_df['message'].fillna('')
    
    classifier = joblib.load(model_path)
    vectorizer = joblib.load(tfidf_path)

    X_test_tfidf = vectorizer.transform(test_df['message'])
    y_test = test_df['true_category']

    print("Evaluating...")
    y_pred = classifier.predict(X_test_tfidf)

    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='weighted', zero_division=0)
    
    report = classification_report(y_test, y_pred, zero_division=0)
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()
    classes = classifier.classes_.tolist()

    metrics = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "classes": classes,
        "confusion_matrix": conf_matrix
    }

    metrics_path = os.path.join('evaluation', 'metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print("\n--- Evaluation Results ---")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    print("\nClassification Report:")
    print(report)
    print(f"\nMetrics saved to {metrics_path}")

if __name__ == "__main__":
    evaluate_model()
