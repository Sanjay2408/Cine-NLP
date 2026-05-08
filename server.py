"""
Cine-NLP Backend Server
Flask API wrapping all NLP pipeline modules.
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import traceback
import tempfile

# Import existing NLP modules
from preprocessing import clean_and_normalize, preprocess_text
from spell_correction import spell_correct_text
from summarization import generate_summary
from sentiment import analyze_sentiment
from ngram_model import TrigramModel
from evaluation import compute_perplexity
from src.api_integration import TMDBAPI
from voice_integration import speech_to_text, text_to_speech

app = Flask(__name__, static_folder=None)
CORS(app)


# ─── System API ──────────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health_check():
    """System health verification."""
    return jsonify({
        'status': 'healthy',
        'version': '1.1.0',
        'nlp_loaded': True,
        'environment': os.getenv('FLASK_ENV', 'development')
    })


# ─── NLP Pipeline API ────────────────────────────────────────
@app.route('/api/analyze', methods=['POST'])
def run_pipeline():
    """Run the full NLP pipeline on input text."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON body'}), 400
            
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

        # Steps 4 & 5: Sentiment & Summarization in parallel
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as executor:
            sentiment_future = executor.submit(analyze_sentiment, text)
            summary_future = executor.submit(generate_summary, text)
            
            sentiment = sentiment_future.result()
            summary = summary_future.result()

        # Step 6: Trigram Model (Local instance for thread-safety)
        model = TrigramModel()
        model.train(corrected_tokens)

        # Context words for prediction
        c_w1, c_w2 = "<s>", "<s>"
        if len(corrected_tokens) >= 2:
            c_w1, c_w2 = corrected_tokens[-2], corrected_tokens[-1]
        elif len(corrected_tokens) == 1:
            c_w2 = corrected_tokens[0]

        predictions = model.generate_predictions(c_w1, c_w2, num_predictions=5)
        predictions_list = [{'word': w, 'probability': round(p, 6)} for w, p in predictions]

        # Step 7: Perplexity
        perplexity = compute_perplexity(model, corrected_tokens)

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
            'perplexity': round(perplexity, 4),
            'status': 'success'
        })

    except Exception as e:
        app.logger.error(f"Pipeline Error: {traceback.format_exc()}")
        return jsonify({'error': f"Processing failed: {str(e)}"}), 500


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


# ─── Voice Integration API ───────────────────────────────────
@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Convert speech from uploaded audio file to text."""
    try:
        # Check if audio file is provided
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            audio_file.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Get API key from request
            groq_api_key = request.form.get('groq_api_key') or request.headers.get('X-Groq-API-Key')
            
            # Convert speech to text
            transcribed_text = speech_to_text(temp_path, api_key=groq_api_key)
            
            if not transcribed_text:
                return jsonify({'error': 'Failed to transcribe audio'}), 500
            
            return jsonify({
                'text': transcribed_text,
                'status': 'success'
            })
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/transcribe-and-analyze', methods=['POST'])
def transcribe_and_analyze():
    """Transcribe audio and run full NLP pipeline in one call."""
    try:
        # Check if audio file is provided
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No audio file selected'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp:
            audio_file.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Get API key from request
            groq_api_key = request.form.get('groq_api_key') or request.headers.get('X-Groq-API-Key')
            
            # Step 1: Convert speech to text
            transcribed_text = speech_to_text(temp_path, api_key=groq_api_key)
            
            if not transcribed_text:
                return jsonify({'error': 'Failed to transcribe audio'}), 500
            
            # Step 2: Run through NLP pipeline
            cleaned = clean_and_normalize(transcribed_text)
            preprocessed_tokens = preprocess_text(cleaned)
            corrected_tokens = spell_correct_text(preprocessed_tokens)
            corrected_text = " ".join(corrected_tokens)
            sentiment = analyze_sentiment(transcribed_text)
            summary = generate_summary(transcribed_text)
            
            # Step 3: Trigram Model
            global trigram_model
            trigram_model = TrigramModel()
            trigram_model.train(corrected_tokens)
            
            c_w1, c_w2 = "<s>", "<s>"
            if len(corrected_tokens) >= 2:
                c_w1, c_w2 = corrected_tokens[-2], corrected_tokens[-1]
            
            predictions = trigram_model.generate_predictions(c_w1, c_w2, num_predictions=5)
            predictions_list = [{'word': w, 'probability': round(p, 6)} for w, p in predictions]
            
            # Step 4: Perplexity
            perplexity = compute_perplexity(trigram_model, corrected_tokens)
            
            return jsonify({
                'original_text': transcribed_text,
                'cleaned_text': cleaned,
                'corrected_text': corrected_text,
                'preprocessed_tokens': preprocessed_tokens,
                'corrected_tokens': corrected_tokens,
                'sentiment': sentiment,
                'summary': summary,
                'context_words': [c_w1, c_w2],
                'predictions': predictions_list,
                'perplexity': round(perplexity, 4),
                'status': 'success'
            })
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/synthesize', methods=['POST'])
def synthesize_speech():
    """Convert text to speech."""
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        lang = data.get('lang', 'en')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Generate audio file
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
        result = text_to_speech(text, lang=lang, output_file=output_file)
        
        if result and os.path.exists(result):
            # Return audio file info
            return jsonify({
                'status': 'success',
                'audio_file': result,
                'text': text
            })
        else:
            return jsonify({'error': 'Failed to generate speech'}), 500
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


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

        summary = "Unable to summarize"
        try:
            summary = generate_summary(text)
        except Exception as gen_err:
            print(f"[WARN] generate_summary failed: {gen_err}")
            # Fallback to direct model
            try:
                from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
                tokenizer = AutoTokenizer.from_pretrained('facebook/bart-large-cnn')
                model = AutoModelForSeq2SeqLM.from_pretrained('facebook/bart-large-cnn')
                inputs = tokenizer(text[:1024], return_tensors='pt', truncation=True)
                summary_ids = model.generate(
                    inputs['input_ids'],
                    max_length=130,
                    min_length=30,
                    no_repeat_ngram_size=3,
                    early_stopping=True
                )
                summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
                print(f"[INFO] Fallback summarization succeeded")
            except Exception as fallback_err:
                print(f"[ERROR] Fallback summarization failed: {fallback_err}")
                return jsonify({'error': f'Summarization failed: {str(fallback_err)[:100]}'}), 500

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
