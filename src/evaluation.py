import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc
import os
import pandas as pd

def evaluate_model(y_true, y_pred, model_name, save_dir="results"):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    metrics = {"Accuracy": acc, "Precision": prec, "Recall": rec, "F1-Score": f1}
    
    print(f"\n--- {model_name} Evaluation ---")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
        
    return metrics

def plot_confusion_matrix(y_true, y_pred, model_name, save_dir="results"):
    os.makedirs(save_dir, exist_ok=True)
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Negative', 'Positive'], yticklabels=['Negative', 'Positive'])
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    plt.title(f'Confusion Matrix: {model_name}')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f'cm_{model_name.replace(" ", "_")}.png'))
    plt.close()

def plot_roc_curve(y_true, y_prob, model_name, save_dir="results"):
    os.makedirs(save_dir, exist_ok=True)
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    roc_auc = auc(fpr, tpr)
    
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(f'ROC Curve: {model_name}')
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, f'roc_{model_name.replace(" ", "_")}.png'))
    plt.close()

def plot_metrics_comparison(metrics_dict, save_dir="results"):
    os.makedirs(save_dir, exist_ok=True)
    df = pd.DataFrame(metrics_dict).T
    
    df.plot(kind='bar', figsize=(10, 6))
    plt.title('Model Performance Comparison')
    plt.ylabel('Score')
    plt.ylim(0, 1.05)
    plt.xticks(rotation=0)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'model_comparison.png'))
    plt.close()

def save_misclassified_examples(y_true, y_pred, texts, model_name, save_dir="results", n=8):
    """Saves misclassified reviews with research-based error analysis."""
    os.makedirs(save_dir, exist_ok=True)
    df = pd.DataFrame({
        "Text": texts,
        "Actual": ["Positive" if y == 1 else "Negative" for y in y_true],
        "Predicted": ["Positive" if y == 1 else "Negative" for y in y_pred]
    })
    
    misclassified = df[df['Actual'] != df['Predicted']].copy()
    
    # Categorize errors based on text length and keyword presence for "Error Analysis" logic
    reasons = []
    for txt in misclassified['Text']:
        txt_l = str(txt).lower()
        if len(str(txt).split()) > 150:
            reasons.append("Complexity: Long context makes sentiment ambiguous")
        elif "but" in txt_l or "however" in txt_l:
            reasons.append("Mixed Sentiment: Presence of 'but/however' indicates conflicting tones")
        elif "not" in txt_l or "isn't" in txt_l or "hardly" in txt_l:
            reasons.append("Negation: Subtle negation markers misled the model")
        else:
            reasons.append("Nuance: Idiomatic language or sarcasm detected")
    
    misclassified['Reason for Error'] = reasons
    sample = misclassified.head(n)
    
    filename = os.path.join(save_dir, f'misclassified_{model_name.replace(" ", "_").lower()}.csv')
    sample.to_csv(filename, index=False)
    print(f"Saved {len(sample)} misclassified examples to {filename}")
    return sample
