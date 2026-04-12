# Cine-NLP — Real-Time Linguistic Intelligence

Cine-NLP is a professional-grade NLP platform designed for sentiment analysis, abstractive summarization, spell correction, and trigram language modeling. It features a stunning, cinematic editorial web interface built with pure HTML/CSS/JS and a robust Flask backend.

![Cine-NLP Hero](https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&q=80&w=2059&ixlib=rb-4.0.3)

## ⚡ Core Pipeline Features

The application processes text through a meticulously engineered 6-stage pipeline:

1.  **Sentiment Analysis (VADER)**: Maps English words to emotional polarity scores to determine the overall tone (Positive, Negative, or Neutral).
2.  **Abstractive Summarization (BART)**: Uses Facebook's `BART-Large-CNN` to generate new, concise summaries rather than just extracting existing sentences.
3.  **Spell Correction (Levenshtein)**: A from-scratch implementation of the Minimum Edit Distance algorithm against a 230k+ word English dictionary.
4.  **Text Preprocessing**: Includes lowercasing, punctuation removal, tokenization (NLTK), stop-word filtering, and lemmatization (spaCy).
5.  **Trigram Language Model**: Computes conditional probabilities P(w₃|w₁,w₂) with Laplace smoothing to predict subsequent words.
6.  **Perplexity Evaluation**: Calculates the fluency and predictability of the input text based on the language model's surprise.

## 🎬 Movie Insights Integration

Cine-NLP integrates with the **TMDB API**, allowing users to:
- Search for any movie in the global database.
- Fetch official plot summaries, ratings, and posters.
- Automatically feed movie plots into the NLP pipeline for instant analysis.

## ✨ Quick Tools

-   **Standalone Summarizer**: A dedicated tool for instant abstractive summarization. It provides detailed metrics such as original word count, summary length, and compression ratio.

## 🛠️ Technology Stack

-   **Backend**: Python, Flask, Flask-CORS
-   **NLP Libraries**: NLTK, spaCy, Transformers (PyTorch), Scikit-learn
-   **Frontend**: Vanilla HTML5, CSS3 (Custom Design System with Glassmorphism), Modern JavaScript (ES6+)
-   **Typography**: *Instrument Serif* (Display), *DM Sans* (Body), *JetBrains Mono* (Code)

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- TMDB API Key (Optional, for Movie Search)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Sanjay2408/Cine-NLP.git
    cd Cine-NLP
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**:
    ```bash
    python server.py
    ```

4.  **Access the UI**:
    Open [http://localhost:5000](http://localhost:5000) in your browser.

## 📁 Project Structure

```text
├── frontend/             # Vanilla JS Frontend assets
│   ├── index.html        # Main entry point
│   ├── style.css         # Custom design system
│   └── app.js            # Frontend application logic
├── src/                  # Supporting modules & API integration
├── server.py             # Flask API & Static file server
├── preprocessing.py      # Text cleaning & tokenization
├── sentiment.py          # VADER sentiment logic
├── summarization.py      # BART summarization wrapper
├── spell_correction.py   # Custom Levenshtein distance
├── ngram_model.py        # Trigram model implementation
└── evaluation.py         # Perplexity calculations
```

## ⚖️ License

Distributed under the MIT License. See `LICENSE` for more information.
