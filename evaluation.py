import math

def compute_perplexity(model, test_tokens):
    """
    Compute Perplexity of the language model on the provided test sequence.
    Perplexity represents the exponential of the negative average log probability.
    """
    if not test_tokens:
        return float('inf')
        
    # Since text usually contains context boundaries, we append padding tokens dynamically.
    padded_tokens = ["<s>", "<s>"] + test_tokens + ["</s>"]
    
    # N total word evaluations will be evaluated (including the end token generation)
    N = len(test_tokens) + 1
    
    log_prob_sum = 0.0
    
    for i in range(len(padded_tokens) - 2):
        w1, w2, w3 = padded_tokens[i], padded_tokens[i+1], padded_tokens[i+2]
        
        # Calculate smoothed probability from the LM module
        prob = model.get_probability(w1, w2, w3)
        
        # Add to total cumulative log probability sum. base 2 log is typical for bits estimation.
        log_prob_sum += math.log2(prob)
        
    avg_log_prob = log_prob_sum / N
    
    # Perplexity = 2^(-(1/N) * SUM(log2 P))
    perplexity = math.pow(2, -avg_log_prob)
    
    return perplexity
