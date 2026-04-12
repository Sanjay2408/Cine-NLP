import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_tfidf_features(train_texts, test_texts, max_features=5000, save_dir=None):
    vectorizer = TfidfVectorizer(max_features=max_features)
    X_train = vectorizer.fit_transform(train_texts)
    X_test = vectorizer.transform(test_texts)
    
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
        joblib.dump(vectorizer, os.path.join(save_dir, 'tfidf_vectorizer.pkl'))
        
    return X_train, X_test, vectorizer
