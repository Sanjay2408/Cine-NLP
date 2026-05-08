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

_CORRECTION_CACHE = {}

def correct_word(word):
    """
    Replace incorrect word with closest match from dictionary.
    """
    if not english_vocab:
        return word 
        
    # Only try to correct alphabetic tokens
    if not word.isalpha():
        return word
        
    # If word is valid, return it 
    if word in english_vocab:
        return word
        
    # Check cache
    if word in _CORRECTION_CACHE:
        return _CORRECTION_CACHE[word]
        
    # Optimization: Filter candidate words by length and first letter
    target_len = len(word)
    
    # Heuristic: Most misspellings share the first letter or have length difference <= 1
    # We expand the search gradually
    for max_len_diff in [1, 2]:
        candidates = [w for w in english_vocab if abs(len(w) - target_len) <= max_len_diff]
        
        # Further filter: many misspellings preserve the first letter
        if target_len > 3:
            first_letter_matches = [w for w in candidates if w[0] == word[0]]
            if first_letter_matches:
                candidates = first_letter_matches

        min_dist = float('inf')
        closest_match = word
        
        for valid_word in candidates:
            dist = levenshtein_distance(word, valid_word)
            if dist < min_dist:
                min_dist = dist
                closest_match = valid_word
            if min_dist == 1: 
                break
        
        if min_dist <= max_len_diff:
            break

    _CORRECTION_CACHE[word] = closest_match
    return closest_match

def spell_correct_text(tokens):
    """
    Accepts a list of tokens and returns a list of corrected tokens.
    """
    return [correct_word(token) for token in tokens]
