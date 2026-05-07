"""
Direct seq2seq summarization using AutoTokenizer + AutoModelForSeq2SeqLM.
No pipeline() calls to avoid task compatibility issues across transformers versions.
"""
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

_GLOBAL_TOKENIZER = None
_GLOBAL_MODEL = None


class TextSummarizer:
    """Summarizer using direct tokenizer + model generation."""
    
    def __init__(self, model_name="facebook/bart-large-cnn"):
        global _GLOBAL_TOKENIZER, _GLOBAL_MODEL
        
        if _GLOBAL_TOKENIZER is None or _GLOBAL_MODEL is None:
            try:
                _GLOBAL_TOKENIZER = AutoTokenizer.from_pretrained(model_name)
                _GLOBAL_MODEL = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            except Exception as e:
                self._init_error = str(e)
                _GLOBAL_TOKENIZER = None
                _GLOBAL_MODEL = None
                return
        
        self._init_error = None
        self.tokenizer = _GLOBAL_TOKENIZER
        self.model = _GLOBAL_MODEL

    def summarize(self, text, max_length=130, min_length=30):
        """Generate a summary of the input text."""
        # Reject empty or too-short text
        if not text or len(text.strip()) < 50:
            return text

        # Check for initialization errors
        if getattr(self, '_init_error', None):
            return f"Summarization Error: {self._init_error}"

        try:
            # Truncate text to avoid very long inputs
            text_truncated = text[:1024]
            
            # Adjust max_length based on input size
            input_len = len(text_truncated.split())
            adj_max = min(max_length, max(min_length + 5, int(input_len * 0.8)))
            
            # Tokenize input
            inputs = self.tokenizer(text_truncated, return_tensors='pt', truncation=True, max_length=1024)
            
            # Generate summary
            summary_ids = self.model.generate(
                inputs['input_ids'],
                max_length=adj_max,
                min_length=min_length,
                no_repeat_ngram_size=3,
                early_stopping=True
            )
            
            # Decode summary
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary
            
        except Exception as e:
            return f"Summarization Error: {str(e)}"


def generate_summary(text):
    """Summarize text using the global summarizer."""
    summarizer = TextSummarizer()
    return summarizer.summarize(text)
