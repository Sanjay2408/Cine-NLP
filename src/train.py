import torch # Load torch first to avoid DLL issues on Windows
import os
import joblib
import pandas as pd
import numpy as np
from datasets import load_dataset

from src.preprocessing import clean_text, download_nltk_resources
from src.feature_engineering import extract_tfidf_features
from src.models import build_logistic_regression, build_naive_bayes, build_transformer
from src.evaluation import evaluate_model, plot_confusion_matrix, plot_roc_curve, plot_metrics_comparison, save_misclassified_examples

# For BERT
import torch
from transformers import Trainer, TrainingArguments, DataCollatorWithPadding
import scipy.special

def compute_metrics(eval_preds):
    logits, labels = eval_preds
    predictions = np.argmax(logits, axis=-1)
    acc = np.mean(predictions == labels)
    return {"accuracy": float(acc)}

def run_pipeline(sample_size=None, bert_sample_size=2000):
    print("Downloading NLP resources...")
    download_nltk_resources()
    
    print("Loading IMDB dataset from Hugging Face...")
    dataset = load_dataset("imdb")
    
    if sample_size:
        train_data = dataset['train'].shuffle(seed=42).select(range(sample_size))
        test_data = dataset['test'].shuffle(seed=42).select(range(sample_size))
    else:
        train_data = dataset['train']
        test_data = dataset['test']
        
    print(f"Dataset Size => Train: {len(train_data)}, Test: {len(test_data)}")
    
    print("\nPreprocessing Text (This might take a while)...")
    train_texts = [clean_text(text) for text in train_data['text']]
    test_texts = [clean_text(text) for text in test_data['text']]
    
    y_train = train_data['label']
    y_test = test_data['label']
    
    print("\nGenerating TF-IDF Features...")
    os.makedirs("results", exist_ok=True)
    X_train_tfidf, X_test_tfidf, vectorizer = extract_tfidf_features(
        train_texts, test_texts, max_features=5000, save_dir="results"
    )
    
    all_metrics = {}
    
    print("\n[1/3] Training Logistic Regression...")
    lr_model = build_logistic_regression()
    lr_model.fit(X_train_tfidf, y_train)
    joblib.dump(lr_model, "results/logistic_regression.pkl")
    
    lr_preds = lr_model.predict(X_test_tfidf)
    lr_probs = lr_model.predict_proba(X_test_tfidf)[:, 1]
    
    lr_metrics = evaluate_model(y_test, lr_preds, "Logistic Regression")
    plot_confusion_matrix(y_test, lr_preds, "Logistic Regression")
    plot_roc_curve(y_test, lr_probs, "Logistic Regression")
    save_misclassified_examples(y_test, lr_preds, test_texts, "Logistic Regression")
    all_metrics["Logistic Regression"] = lr_metrics
    
    print("\n[2/3] Training Naive Bayes...")
    nb_model = build_naive_bayes()
    nb_model.fit(X_train_tfidf, y_train)
    joblib.dump(nb_model, "results/naive_bayes.pkl")
    
    nb_preds = nb_model.predict(X_test_tfidf)
    nb_probs = nb_model.predict_proba(X_test_tfidf)[:, 1]
    
    nb_metrics = evaluate_model(y_test, nb_preds, "Naive Bayes")
    plot_confusion_matrix(y_test, nb_preds, "Naive Bayes")
    plot_roc_curve(y_test, nb_probs, "Naive Bayes")
    all_metrics["Naive Bayes"] = nb_metrics
    
    print("\n[3/3] Fine-tuning DistilBERT (on a subset of data)...")
    model_name = "distilbert-base-uncased"
    tokenizer, bert_model = build_transformer(model_name)
    tokenizer.save_pretrained("results/distilbert-sentiment")
    
    def tokenize_function(examples):
        return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=256)
    
    bert_train_sample = min(bert_sample_size, len(train_data))
    bert_test_sample = min(bert_sample_size // 4, len(test_data))
    
    bert_train = train_data.shuffle(seed=42).select(range(bert_train_sample))
    bert_test = test_data.shuffle(seed=42).select(range(bert_test_sample))
    
    tokenized_train = bert_train.map(tokenize_function, batched=True)
    tokenized_test = bert_test.map(tokenize_function, batched=True)
    
    training_args = TrainingArguments(
        output_dir="results/bert_trainer",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        num_train_epochs=2,
        weight_decay=0.01,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
    )
    
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
    
    trainer = Trainer(
        model=bert_model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_test,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )
    
    trainer.train()
    trainer.save_model("results/distilbert-sentiment")
    
    print("\nEvaluating DistilBERT...")
    bert_preds_output = trainer.predict(tokenized_test)
    bert_preds = np.argmax(bert_preds_output.predictions, axis=-1)
    
    bert_probs = scipy.special.softmax(bert_preds_output.predictions, axis=-1)[:, 1]
    bert_y_true = tokenized_test['label']
    
    bert_metrics = evaluate_model(bert_y_true, bert_preds, "DistilBERT")
    plot_confusion_matrix(bert_y_true, bert_preds, "DistilBERT")
    plot_roc_curve(bert_y_true, bert_probs, "DistilBERT")
    save_misclassified_examples(bert_y_true, bert_preds, bert_test['text'], "DistilBERT")
    all_metrics["DistilBERT"] = bert_metrics
    
    print("\nComparing performance of all models...")
    plot_metrics_comparison(all_metrics)
    
    print("\nTraining Pipeline complete! Artifacts are available in 'results/'")

if __name__ == "__main__":
    # You can pass sample_size=N to limit the total dataset for quick testing
    run_pipeline(sample_size=None, bert_sample_size=2000)
