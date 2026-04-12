# Cine-NLP — Mathematical & Neural Linguistics

Cine-NLP is an academic research platform designed to demonstrate the intersection of classical linguistic algorithms and modern neural architectures. Built as a comprehensive pipeline, it analyzes cinematic narratives through six distinct stages of processing.

## 🎓 Technical Methodology

### 1. Lexicographical Sentiment Analysis
The system utilizes the **VADER** (Valence Aware Dictionary and sEntiment Reasoning) lexicon. It maps individual tokens to emotional polarity intensities, accounting for structural features like intensifiers ("very good") and contrastive conjunctions ("but").

### 2. Abstractive Neural Summarization
Unlike extractive methods, Cine-NLP utilizes a pre-trained **BART-Large-CNN** transformer model. This architecture reads the entire input sequence and generates new semantic tokens to capture the abstract essence of the text.

### 3. Minimum Edit Distance Correction
A custom implementation of the **Levenshtein Distance** algorithm. Using a dynamic programming matrix, the system calculates the optimal sequence of insertions, deletions, and substitutions to align noisy input strings with a 230k+ word English dictionary.

### 4. N-Gram Language Modeling
The system builds a **Trigram Model** ($P(w_3 | w_1, w_2)$) with **Laplace Smoothing** ($\alpha=1.0$). This allows the system to predict potential successor tokens based on observed local structural probabilities in English corpora.

### 5. Mathematical Evaluation (Perplexity)
We evaluate the fluency of the linguistic structure using **Perplexity** ($PP(W)$), calculated as the inverse probability of the test set, normalized by the number of words. Lower perplexity indicates the model follows standard English syntactic patterns.

---

## 🛠️ System Architecture

-   **Backend**: Python 3.10+ / Flask / RESTful API
-   **NLP Engine**: PyTorch / Transformers / NLTK / spaCy
-   **Frontend**: Vanilla HTML5 / CSS3 / ES6+ JavaScript
-   **Data Sync**: TMDB API Integration for real-time plot fetching

## 🚀 Deployment Instructions

### Local Development
1.  **Install Requirements**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Initial Setup**:
    ```python
    import nltk
    nltk.download(['vader_lexicon', 'punkt', 'stopwords', 'wordnet'])
    ```
3.  **Run Server**:
    ```bash
    python server.py
    ```
    Access at `http://localhost:5000`

### Production Note
For production-grade deployment, use a WSGI server like **Gunicorn**:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 server:app
```
