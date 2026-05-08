import nltk
try:
    print("Checking NLTK...")
    nltk.download('vader_lexicon', quiet=True)
    print("NLTK OK")
except Exception as e:
    print(f"NLTK Error: {e}")

try:
    print("Checking pyttsx3...")
    import pyttsx3
    engine = pyttsx3.init()
    print("pyttsx3 OK")
except Exception as e:
    print(f"pyttsx3 Error: {e}")

print("Done")
