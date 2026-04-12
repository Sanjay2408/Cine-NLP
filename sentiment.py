import nltk

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    try:
        nltk.download('vader_lexicon', quiet=True)
    except:
        pass

from nltk.sentiment.vader import SentimentIntensityAnalyzer

def analyze_sentiment(text):
    """
    Perform sentiment classification (positive/negative/neutral) using VADER lexicon.
    """
    # Initialize the sentiment reasoning algorithm 
    sia = SentimentIntensityAnalyzer()
    
    # Evaluate compound polarity. 
    # VADER score compounds between -1.0 to 1.0. 
    # Usually >= 0.05 maps to Positive and <= -0.05 to Negative
    scores = sia.polarity_scores(text)
    
    compound = scores['compound']
    
    if compound >= 0.05:
        return "Positive"
    elif compound <= -0.05:
        return "Negative"
    else:
        return "Neutral"
