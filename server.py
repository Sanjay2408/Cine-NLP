"""
Cine-NLP Backend Server
Flask API wrapping all NLP pipeline modules.
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import traceback

# Import existing NLP modules
from preprocessing import clean_and_normalize, preprocess_text
from spell_correction import spell_correct_text
from summarization import generate_summary
from sentiment import analyze_sentiment
from ngram_model import TrigramModel
from evaluation import compute_perplexity
from src.api_integration import TMDBAPI

app = Flask(__name__, static_folder=None)
CORS(app)

# Global trigram model instance
trigram_model = TrigramModel()


# ─── NLP Pipeline API ────────────────────────────────────────
@app.route('/api/analyze', methods=['POST'])
def run_pipeline():
    """Run the full NLP pipeline on input text."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Step 1: Clean & Normalize
        cleaned = clean_and_normalize(text)

        # Step 2: Tokenize & Lemmatize
        preprocessed_tokens = preprocess_text(cleaned)

        # Step 3: Spell Correction
        corrected_tokens = spell_correct_text(preprocessed_tokens)
        corrected_text = " ".join(corrected_tokens)

        # Step 4: Sentiment Analysis
        sentiment = analyze_sentiment(text)

        # Step 5: Summarization
        summary = generate_summary(text)

        # Step 6: Trigram Model
        global trigram_model
        trigram_model = TrigramModel()
        trigram_model.train(corrected_tokens)

        # Context words for prediction
        c_w1, c_w2 = "<s>", "<s>"
        if len(corrected_tokens) >= 2:
            c_w1, c_w2 = corrected_tokens[-2], corrected_tokens[-1]

        predictions = trigram_model.generate_predictions(c_w1, c_w2, num_predictions=5)
        predictions_list = [{'word': w, 'probability': round(p, 6)} for w, p in predictions]

        # Step 7: Perplexity
        perplexity = compute_perplexity(trigram_model, corrected_tokens)

        return jsonify({
            'original_text': text,
            'cleaned_text': cleaned,
            'corrected_text': corrected_text,
            'preprocessed_tokens': preprocessed_tokens,
            'corrected_tokens': corrected_tokens,
            'sentiment': sentiment,
            'summary': summary,
            'context_words': [c_w1, c_w2],
            'predictions': predictions_list,
            'perplexity': round(perplexity, 4)
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/sentiment', methods=['POST'])
def live_sentiment():
    """Quick sentiment check for live typing feedback."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        if not text:
            return jsonify({'sentiment': 'Neutral'})
        result = analyze_sentiment(text)
        return jsonify({'sentiment': result})
    except Exception as e:
        return jsonify({'sentiment': 'Neutral', 'error': str(e)})


@app.route('/api/summarize', methods=['POST'])
def standalone_summarize():
    """Standalone text summarization endpoint."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        if len(text) < 50:
            return jsonify({'error': 'Text is too short to summarize. Please provide at least 50 characters.'}), 400

        summary = generate_summary(text)
        word_count_original = len(text.split())
        word_count_summary = len(summary.split())
        compression = round((1 - word_count_summary / word_count_original) * 100, 1) if word_count_original > 0 else 0

        return jsonify({
            'summary': summary,
            'original_length': word_count_original,
            'summary_length': word_count_summary,
            'compression_ratio': compression
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/movie/search', methods=['POST'])
def search_movie():
    """Search for movies via TMDB API."""
    try:
        data = request.get_json()
        query = data.get('query', '')
        api_key = data.get('api_key', '') or os.getenv('TMDB_API_KEY', '')

        if not api_key:
            return jsonify({'error': 'No TMDB API key provided'}), 400

        tmdb = TMDBAPI(api_key=api_key)
        results = tmdb.search_movies(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/movie/details', methods=['POST'])
def movie_details():
    """Get movie details from TMDB."""
    try:
        data = request.get_json()
        movie_id = data.get('movie_id', '')
        api_key = data.get('api_key', '') or os.getenv('TMDB_API_KEY', '')

        if not api_key:
            return jsonify({'error': 'No TMDB API key provided'}), 400

        tmdb = TMDBAPI(api_key=api_key)
        details = tmdb.get_details(movie_id)
        return jsonify(details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─── Serve Frontend (MUST be last to avoid catching API routes) ───
@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)


if __name__ == '__main__':
    print("Starting Cine-NLP Server...")
    print("Visit http://localhost:5000")
    app.run(debug=True, port=5000, use_reloader=False)
