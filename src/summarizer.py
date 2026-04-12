from transformers import pipeline

class TextSummarizer:
    def __init__(self, model_name="facebook/bart-large-cnn"):
        """Use pre-trained models like facebook/bart-large-cnn or t5-small."""
        self.summarizer = pipeline("summarization", model=model_name)

    def summarize(self, text, max_length=130, min_length=30):
        if not text or len(text.strip()) < 50:
            return text # Too short to summarize

        # Pre-process text to avoid input_length > model_limit
        text_truncated = text[:1024]
        input_len = len(text_truncated.split())
        adj_max = min(max_length, max(min_length + 5, int(input_len * 0.8)))
        
        try:
            summary_list = self.summarizer(text_truncated, max_length=adj_max, min_length=min_length, do_sample=False)
            return summary_list[0]['summary_text']
        except Exception as e:
            return f"Summarization Error: {str(e)}"
