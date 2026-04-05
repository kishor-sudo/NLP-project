from utils.preprocessing import preprocess, clean_text
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from collections import Counter

# Ensure VADER lexicon is available
try:
    nltk.data.find('sentiment/vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)


THEME_KEYWORDS = {
    "Love & Romance": ["love", "heart", "kiss", "forever", "baby", "darling", "romance", "sweet"],
    "Heartbreak & Sadness": ["cry", "tears", "broken", "lonely", "goodbye", "hurt", "pain", "sad"],
    "Motivation & Resilience": ["strong", "fight", "survive", "power", "rise", "champion", "believe"],
    "Happiness & Celebration": ["happy", "dance", "party", "smile", "joy", "celebrate", "tonight", "fun"],
    "Nostalgia & Memories": ["remember", "yesterday", "past", "memory", "time", "back", "young"],
}

def analyze_vader_emotion(text: str) -> str:
    """
    Uses VADER sentiment analysis to determine the general emotion.
    """
    sia = SentimentIntensityAnalyzer()
    score = sia.polarity_scores(text)
    
    compound = score['compound']
    if compound >= 0.5:
        return "Highly Positive / Joyful"
    elif 0.05 <= compound < 0.5:
        return "Positive / Uplifting"
    elif -0.05 < compound < 0.05:
        return "Neutral / Reflective"
    elif -0.5 < compound <= -0.05:
        return "Negative / Melancholic"
    else:
        return "Highly Negative / Angsty"

def detect_theme(tokens: list) -> str:
    """
    Detects the primary theme of the lyrics based on keyword overlaps.
    """
    theme_scores = Counter()
    
    for token in tokens:
        for theme, keywords in THEME_KEYWORDS.items():
            if token in keywords:
                theme_scores[theme] += 1
                
    if not theme_scores:
        return "General / Ambiguous"
    
    # Return the theme with highest score
    primary_theme = theme_scores.most_common(1)[0][0]
    return primary_theme

def interpret_song(lyrics: str) -> dict:
    """
    Main function to interpret song lyrics. Pipeline:
    1. Preprocess
    2. Sentiment Analysis (Emotion)
    3. Keyword Theme Detection
    4. Meaning generation
    """
    if not lyrics or not lyrics.strip():
        raise ValueError("Lyrics cannot be empty.")
        
    cleaned_full_text = clean_text(lyrics)
    tokens = preprocess(lyrics)
    
    if not tokens:
        return {
            "emotion": "Unknown",
            "theme": "Unknown",
            "meaning_explanation": "The lyrics provided are too short or contain mostly filler words to interpret."
        }
    
    emotion = analyze_vader_emotion(lyrics)
    theme = detect_theme(tokens)
    
    # Extract top 5 words for explanation
    word_counts = Counter(tokens)
    top_words = [word for word, count in word_counts.most_common(5)]
    
    explanation = (
        f"This song carries a **{emotion.lower()}** vibe. "
        f"Based on the lyrical content, its primary theme seems to be **{theme}**. "
        f"The recurring use of words like {', '.join([f'*{w}*' for w in top_words])} "
        f"suggests that the artist is focusing heavily on these concepts to convey their message."
    )
    
    return {
        "emotion": emotion,
        "theme": theme,
        "meaning_explanation": explanation,
        "top_keywords": top_words
    }

if __name__ == "__main__":
    sample_lyrics = "I will always love you, my heart will go on forever. Even when we say goodbye, I won't cry."
    print(interpret_song(sample_lyrics))
