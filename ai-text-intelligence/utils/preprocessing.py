import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Make sure resources are available (in a real app, this might be handled during setup)
try:
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)


def clean_text(text: str) -> str:
    """
    Cleans the input text by removing special characters, numbers, and excess whitespace.
    """
    if not isinstance(text, str):
        return ""
    
    # Remove HTML tags if any (basic approach)
    text = re.sub(r'<[^>]+>', '', text)
    # Remove special characters and numbers (keep only letters and spaces)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Convert to lowercase
    text = text.lower()
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def tokenize_text(text: str) -> list:
    """
    Tokenizes the text into individual words.
    """
    if not text.strip():
        return []
    return word_tokenize(text)

def remove_stopwords(tokens: list) -> list:
    """
    Removes standard English stopwords from a list of tokens.
    """
    if not tokens:
        return []
    stop_words = set(stopwords.words('english'))
    # Adding some common lyric fillers to stopwords
    lyric_fillers = {'oh', 'yeah', 'la', 'ooh', 'ah', 'baby', 'na'}
    stop_words.update(lyric_fillers)
    
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    return filtered_tokens

def preprocess(text: str) -> list:
    """
    Applies the full preprocessing pipeline: clean -> tokenize -> remove stopwords.
    """
    cleaned = clean_text(text)
    tokens = tokenize_text(cleaned)
    final_tokens = remove_stopwords(tokens)
    return final_tokens

if __name__ == "__main__":
    sample = "Oh baby, yeah! I love you 3000 times, na na na."
    print("Original:", sample)
    print("Preprocessed:", preprocess(sample))
