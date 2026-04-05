import nltk
import re
from utils.preprocessing import clean_text

# Ensure CMU dict is available
try:
    nltk.data.find('corpora/cmudict')
except LookupError:
    nltk.download('cmudict', quiet=True)

try:
    cmudict = nltk.corpus.cmudict.dict()
except Exception:
    cmudict = {}

def get_word_syllables_and_stress(word: str) -> list:
    """
    Returns a list of stresses (0 for unstressed, 1 for primary/secondary stress)
    for a given word. Returns empty list if word not found.
    """
    word = word.lower()
    if word not in cmudict:
        return []
    
    # Take the first pronunciation variant
    pronunciation = cmudict[word][0]
    stresses = []
    
    for phoneme in pronunciation:
        # Check if phoneme has a digit (which indicates stress on vowels)
        match = re.search(r'\d', phoneme)
        if match:
            stress_level = int(match.group())
            # simplify primary (1) and secondary (2) to stressed (1)
            stresses.append(1 if stress_level > 0 else 0)
            
    return stresses

def analyze_meter(poem_text: str) -> dict:
    """
    Analyzes the meter of a poem. Extracts syllable stresses and attempts
    to guess the meter pattern.
    """
    lines = [line.strip() for line in poem_text.split('\n') if line.strip()]
    if not lines:
        raise ValueError("Poem text cannot be empty.")
        
    line_stresses = []
    all_stresses = []
    
    for line in lines:
        words = clean_text(line).split()
        current_line_stress = []
        for word in words:
            word_stress = get_word_syllables_and_stress(word)
            current_line_stress.extend(word_stress)
            all_stresses.extend(word_stress)
            
        line_stresses.append({
            "line": line,
            "stress_pattern": current_line_stress
        })
        
    # Analyze global pattern
    pattern_string = "".join(map(str, all_stresses))
    
    # Basic Heuristic to guess meter based on substrings
    meter_counts = {
        "Iambic (01)": pattern_string.count("01"),
        "Trochaic (10)": pattern_string.count("10"),
        "Anapestic (001)": pattern_string.count("001"),
        "Dactylic (100)": pattern_string.count("100"),
    }
    
    if not pattern_string:
         return {
            "meter_type": "Unknown",
            "confidence": "Low",
            "line_analysis": line_stresses,
            "explanation": "Could not identify phonetic structure. Words may not be in dictionary."
        }
    
    # A crude way to guess the dominating meter type
    # Normalize by the length of the string to find density
    dominating_meter = max(meter_counts, key=meter_counts.get)
    max_count = meter_counts[dominating_meter]
    
    # Calculate covered syllables
    pattern_len = 3 if ("Anapestic" in dominating_meter or "Dactylic" in dominating_meter) else 2
    coverage = (max_count * pattern_len) / len(pattern_string) if len(pattern_string) > 0 else 0
    
    if coverage > 0.6:
        confidence = "High"
    elif coverage > 0.4:
        confidence = "Medium"
    else:
        confidence = "Low"
        dominating_meter = "Free Verse / Irregular"
        
    explanation = f"The dominating stress pattern is {dominating_meter} with a {confidence.lower()} confidence based on a coverage ratio of {coverage:.2f}."
    
    return {
        "meter_type": dominating_meter,
        "confidence": confidence,
        "line_analysis": line_stresses,
        "explanation": explanation
    }

if __name__ == "__main__":
    sample = "Shall I compare thee to a summer's day?\nThou art more lovely and more temperate"
    print(analyze_meter(sample))
