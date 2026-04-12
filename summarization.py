from transformers import pipeline

_GLOBAL_SUMMARIZER = None

class TextSummarizer:
    """Class to encapsulate summarization model loading and predictions"""
    def __init__(self, model_name="facebook/bart-large-cnn"):
        """Use pre-trained models like facebook/bart-large-cnn or t5-small."""
        global _GLOBAL_SUMMARIZER
        if _GLOBAL_SUMMARIZER is None:
            # Initializing the pipeline can take a moment if not cached.
            _GLOBAL_SUMMARIZER = pipeline("summarization", model=model_name)
        self.summarizer = _GLOBAL_SUMMARIZER

    def summarize(self, text, max_length=130, min_length=30):
        # Prevent summarizing non-sense or extremely short phrases
        if not text or len(text.strip()) < 50:
            return text 

        # Pre-process text to avoid input_length > model_limit
        text_truncated = text[:1024]
        input_len = len(text_truncated.split())
        
        # Max length should not exceed sequence length if sequence is small
        adj_max = min(max_length, max(min_length + 5, int(input_len * 0.8)))
        
        try:
            summary_list = self.summarizer(
                text_truncated, 
                max_length=adj_max, 
                min_length=min_length, 
                do_sample=False
            )
            return summary_list[0]['summary_text']
        except Exception as e:
            return f"Summarization Error: {str(e)}"

def generate_summary(text):
    """
    Summarize a long paragraph into a shorter version.
    Utilizes transformer's pipeline retaining older original features.
    """
    summarizer = TextSummarizer()
    return summarizer.summarize(text)
