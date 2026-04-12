from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from transformers import AutoModelForSequenceClassification, AutoTokenizer

def build_logistic_regression():
    return LogisticRegression(max_iter=1000, random_state=42)

def build_naive_bayes():
    return MultinomialNB()

def build_transformer(model_name="distilbert-base-uncased", num_labels=2):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)
    return tokenizer, model
