import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

# Add parent directory to path to import preprocessing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocessing.text_cleaner import clean_text

def train_model():
    dataset_path = os.path.join('dataset', 'commits.csv')
    if not os.path.exists(dataset_path):
        print(f"Error: Dataset not found at {dataset_path}")
        return

    print("Loading dataset...")
    df = pd.read_csv(dataset_path)
    
    print("Cleaning text...")
    df['cleaned_message'] = df['commit_message'].apply(clean_text)
    
    # Drop empty messages after cleaning
    df = df[df['cleaned_message'].str.len() > 0]

    X = df['cleaned_message']
    y = df['category']

    # Train/validation/test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print("Extracting TF-IDF features...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_tfidf = vectorizer.fit_transform(X_train)
    
    print("Training Logistic Regression model...")
    # Using class_weight='balanced' to handle class imbalance
    classifier = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)
    classifier.fit(X_train_tfidf, y_train)

    print("Saving models...")
    os.makedirs('models', exist_ok=True)
    joblib.dump(classifier, os.path.join('models', 'classifier.pkl'))
    joblib.dump(vectorizer, os.path.join('models', 'tfidf.pkl'))
    
    # Save test set for evaluation
    os.makedirs('evaluation', exist_ok=True)
    test_df = pd.DataFrame({'message': X_test, 'true_category': y_test})
    test_df.to_csv(os.path.join('evaluation', 'test_set.csv'), index=False)
    
    print("Training complete!")

if __name__ == "__main__":
    train_model()
