import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

def download_nltk_resources():
    try:
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('omw-1.4', quiet=True)
    except Exception as e:
        print(f"Warning: NLTK download failed: {e}")

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    
    try:
        stop_words = set(stopwords.words('english'))
    except LookupError:
        download_nltk_resources()
        stop_words = set(stopwords.words('english'))
        
    lemmatizer = WordNetLemmatizer()
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    
    return ' '.join(tokens)
