from collections import defaultdict, Counter

class TrigramModel:
    def __init__(self):
        # Maps (w1, w2) to a dictionary of (w3 -> frequency)
        self.trigram_counts = defaultdict(Counter)
        # Maps (w1, w2) to total frequency
        self.bigram_counts = Counter()
        # Set of unique vocabulary words
        self.vocab = set()
        
    def train(self, tokens):
        """
        Train the Trigram Language Model from a list of words.
        Updates internal frequency dicts and vocabulary.
        """
        # Populate vocabulary
        for word in tokens:
            self.vocab.add(word)
            
        # Pad tokens with start/end markers
        padded_tokens = ["<s>", "<s>"] + tokens + ["</s>"]
        
        self.vocab.add("<s>")
        self.vocab.add("</s>")
        
        for i in range(len(padded_tokens) - 2):
            w1 = padded_tokens[i]
            w2 = padded_tokens[i+1]
            w3 = padded_tokens[i+2]
            
            self.trigram_counts[(w1, w2)][w3] += 1
            self.bigram_counts[(w1, w2)] += 1
            
    def get_probability(self, w1, w2, w3):
        """
        Compute conditional probability P(w3 | w1, w2) defined as:
        Count(w1, w2, w3) / Count(w1, w2) -> smoothed with Add-1 Laplace.
        """
        V = len(self.vocab)
        count_trigram = self.trigram_counts[(w1, w2)][w3]
        count_bigram = self.bigram_counts[(w1, w2)]
        
        # Laplace Smoothing: (count + 1) / (total_count + Vocabulary_Size)
        prob = (count_trigram + 1) / (count_bigram + V)
        return prob
        
    def generate_predictions(self, w1, w2, num_predictions=5):
        """
        Generate num_predictions next-word candidates given a 2-word history (w1, w2).
        """
        V = len(self.vocab)
        count_bigram = self.bigram_counts[(w1, w2)]
        
        candidates = []
        for word in self.vocab:
            # Skip generating the start-of-sequence token as a prediction
            if word == "<s>":
                continue
                
            count_trigram = self.trigram_counts[(w1, w2)][word]
            prob = (count_trigram + 1) / (count_bigram + V)
            
            candidates.append((prob, word))
            
        # Sort candidates descending by probability score
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [(word, prob) for prob, word in candidates[:num_predictions]]
