import nltk

try:
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words', quiet=True)

from nltk.corpus import words

# Load English dictionary and convert to a set of lowercased words
try:
    english_vocab = set(word.lower() for word in words.words())
except Exception as e:
    print(f"Warning: Could not load english words vocabulary. {e}")
    english_vocab = set()

def levenshtein_distance(s1, s2):
    """
    Computes the Minimum Edit Distance (Levenshtein Distance) FROM SCRATCH.
    Returns the integer distance between string s1 and s2.
    """
    m, n = len(s1), len(s2)
    
    # Initialize dynamic programming table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
        
    # Fill the DP table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1
                
            dp[i][j] = min(
                dp[i - 1][j] + 1,       # deletion
                dp[i][j - 1] + 1,       # insertion
                dp[i - 1][j - 1] + cost # substitution
            )
                           
    return dp[m][n]

def correct_word(word):
    """
    Replace incorrect word with closest match from dictionary.
    """
    if not english_vocab:
        return word # Fallback if dictionary failed to load
        
    # Only try to correct alphabetic tokens
    if not word.isalpha():
        return word
        
    # If word is valid, return it without modification
    if word in english_vocab:
        return word
        
    # Optimization: Filter candidate words by length to avoid O(N*M) over huge N
    # We only consider words that have a length difference of at most 2
    target_len = len(word)
    candidate_words = [w for w in english_vocab if abs(len(w) - target_len) <= 2]
    
    min_dist = float('inf')
    closest_match = word
    
    for valid_word in candidate_words:
        # Early skip if the length difference itself is >= current min_dist
        if abs(target_len - len(valid_word)) >= min_dist:
            continue
            
        dist = levenshtein_distance(word, valid_word)
        if dist < min_dist:
            min_dist = dist
            closest_match = valid_word
            
        # Early stopping if distance is 1 (the lowest possible edit cost for a misspelled word)
        if min_dist == 1: 
            break
            
    return closest_match

def spell_correct_text(tokens):
    """
    Accepts a list of tokens and returns a list of corrected tokens.
    """
    return [correct_word(token) for token in tokens]
