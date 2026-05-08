import re
import spacy
import nltk
import warnings
import subprocess
import sys

# Suppress Security Violation [pathsec.ZipFile] warnings from NLTK in Python 3.12+ (Windows Store version)
warnings.filterwarnings("ignore", category=RuntimeWarning, message=r"Security Violation \[pathsec.ZipFile\]")

# Ensure required NLTK resources are available
def download_nltk_resources():
    resources = ['stopwords', 'punkt', 'punkt_tab']
    for res in resources:
        try:
            nltk.data.find(f'corpora/{res}')
        except LookupError:
            try:
                nltk.data.find(f'tokenizers/{res}')
            except LookupError:
                nltk.download(res, quiet=True)

download_nltk_resources()

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Load spacy model for lemmatization
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


def clean_and_normalize(text):
    """
    Convert text to lowercase
    Remove punctuation and unnecessary characters
    """
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def preprocess_text(text):
    """
    Tokenization
    Stop-word removal
    Lemmatization using spaCy
    """
    # 1. Tokenization
    tokens = word_tokenize(text)
    
    # 2. Stop-word removal
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    # 3. Lemmatization using spaCy
    # Spacy works best on text, so we join the tokens, or process them one by one.
    text_for_spacy = " ".join(filtered_tokens)
    doc = nlp(text_for_spacy)
    lemmatized_tokens = [token.lemma_ for token in doc]
    
    return lemmatized_tokens
