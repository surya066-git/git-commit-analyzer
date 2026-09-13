import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Ensure resources are downloaded
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')
    nltk.download('punkt_tab')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text: str) -> str:
    """
    Cleans commit messages for ML pipeline.
    """
    if not text:
        return ""
    
    # Lowercase normalization
    text = text.lower()
    
    # Remove URLs, issue numbers (#123), and special characters
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'#\d+', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    
    # Tokenization
    tokens = word_tokenize(text)
    
    # Stop-word handling and Lemmatization
    cleaned_tokens = [
        lemmatizer.lemmatize(word) 
        for word in tokens 
        if word not in stop_words and len(word) > 1
    ]
    
    return ' '.join(cleaned_tokens)
