import nltk
import re
from collections import Counter
from utils.preprocessing import clean_text

# ---------------------------------------------------------------------------
# 1. Ensure CMU Pronouncing Dictionary is available
# ---------------------------------------------------------------------------
try:
    nltk.data.find('corpora/cmudict')
except LookupError:
    nltk.download('cmudict', quiet=True)

try:
    cmudict = nltk.corpus.cmudict.dict()
except Exception:
    cmudict = {}

# ---------------------------------------------------------------------------
# 2. Poetic contractions / archaic forms lookup  (Improvement #6)
#    Maps common poetic words that CMU dict may not cover to a hand-crafted
#    list of phonemes (simplified – only stress digits matter here).
# ---------------------------------------------------------------------------
POETIC_FORMS = {
    "'tis":   ["1"],        # stressed (it is)
    "tis":    ["1"],
    "o'er":   ["1"],        # over  → one stressed syllable
    "e'en":   ["1"],        # even  → one stressed syllable
    "ne'er":  ["1"],        # never → one stressed syllable
    "e'er":   ["1"],        # ever
    "'twas":  ["1"],        # it was
    "twas":   ["1"],
    "thee":   ["1"],
    "thou":   ["1"],
    "thy":    ["1"],
    "thine":  ["1"],
    "hath":   ["1"],
    "doth":   ["1"],
    "ere":    ["1"],
    "oft":    ["1"],
    "whence": ["1"],
    "hence":  ["1"],
    "whilst": ["1"],
    "methinks": ["0", "1"],  # me-THINKS
    "betwixt":  ["0", "1"],  # be-TWIXT
    "forsooth":  ["0", "1"],
    "wouldst":  ["1"],
    "canst":    ["1"],
    "dost":     ["1"],
    "shalt":    ["1"],
    "wilt":     ["1"],
    "hast":     ["1"],
    "art":      ["1"],
}

# ---------------------------------------------------------------------------
# 3. Syllable fallback heuristic  (Improvement #3)
#    When a word is not in CMU dict, estimate syllable count from vowel groups
#    and assign an alternating unstressed-stressed pattern.
# ---------------------------------------------------------------------------
def _estimate_syllables(word: str) -> int:
    """Estimate syllable count by counting vowel groups, with adjustments."""
    word = word.lower().strip()
    if not word:
        return 0

    # Count vowel groups
    count = len(re.findall(r'[aeiouy]+', word))

    # Subtract silent-e at end (but not for short words like "the")
    if word.endswith('e') and len(word) > 3 and not word.endswith(('le', 'ee', 'ie', 'ye')):
        count = max(count - 1, 1)

    # Handle common suffixes that add a syllable
    if word.endswith(('tion', 'sion', 'cian')):
        count = max(count, 2)

    return max(count, 1)


def _fallback_stress(word: str) -> list:
    """Generate an estimated alternating stress pattern for an unknown word."""
    n = _estimate_syllables(word)
    # Default to alternating unstressed/stressed (iambic-like)
    return [i % 2 for i in range(n)]

# ---------------------------------------------------------------------------
# 4. Stress extraction – with multi-pronunciation support  (Improvement #5)
# ---------------------------------------------------------------------------
def _pronunciation_to_stress(pronunciation: list) -> list:
    """Convert a CMU phoneme list to a binary stress list."""
    stresses = []
    for phoneme in pronunciation:
        match = re.search(r'\d', phoneme)
        if match:
            stress_level = int(match.group())
            stresses.append(1 if stress_level > 0 else 0)
    return stresses


def get_word_syllables_and_stress(word: str, context_pattern: list | None = None) -> list:
    """
    Returns a list of stresses (0=unstressed, 1=stressed) for *word*.

    Improvements over original:
      - Checks the poetic-forms lookup table first.
      - Tries ALL CMU pronunciations and picks the best fit against the
        emerging `context_pattern` (if supplied).
      - Falls back to a vowel-group heuristic for unknown words.
    """
    word_lower = word.lower().strip()

    # --- Poetic forms lookup ---
    if word_lower in POETIC_FORMS:
        return [int(s) for s in POETIC_FORMS[word_lower]]

    # --- CMU dict lookup ---
    if word_lower in cmudict:
        pronunciations = cmudict[word_lower]

        if len(pronunciations) == 1 or context_pattern is None:
            return _pronunciation_to_stress(pronunciations[0])

        # Pick the pronunciation whose stress best continues the pattern
        best_score = -1
        best_stress = _pronunciation_to_stress(pronunciations[0])

        for pron in pronunciations:
            stress = _pronunciation_to_stress(pron)
            # Score: how well does appending this stress continue an
            # alternating pattern from context_pattern?
            score = 0
            for i, s in enumerate(stress):
                idx = len(context_pattern) + i
                expected = idx % 2  # simple alternating expectation
                if s == expected:
                    score += 1
            if score > best_score:
                best_score = score
                best_stress = stress

        return best_stress

    # --- Fallback heuristic ---
    return _fallback_stress(word_lower)

# ---------------------------------------------------------------------------
# 5. Meter-pattern definitions
# ---------------------------------------------------------------------------
METER_PATTERNS = {
    "Iambic":    [0, 1],      # da-DUM
    "Trochaic":  [1, 0],      # DUM-da
    "Anapestic": [0, 0, 1],   # da-da-DUM
    "Dactylic":  [1, 0, 0],   # DUM-da-da
    "Spondaic":  [1, 1],      # DUM-DUM
    "Pyrrhic":   [0, 0],      # da-da
}

# Foot-count names
FOOT_COUNT_NAMES = {
    1: "Monometer",
    2: "Dimeter",
    3: "Trimeter",
    4: "Tetrameter",
    5: "Pentameter",
    6: "Hexameter",
    7: "Heptameter",
    8: "Octameter",
}

# ---------------------------------------------------------------------------
# 6. Non-overlapping pattern matching + scoring  (Improvements #1 & #2)
# ---------------------------------------------------------------------------
def _score_meter_for_line(stress: list, meter_name: str, pattern: list) -> float:
    """
    Score how well `stress` matches `pattern` using non-overlapping chunking.
    Returns a ratio 0.0 – 1.0 representing the fraction of feet that match.
    """
    foot_len = len(pattern)
    if len(stress) < foot_len:
        return 0.0

    total_feet = len(stress) // foot_len
    if total_feet == 0:
        return 0.0

    matching_feet = 0
    for i in range(total_feet):
        chunk = stress[i * foot_len : (i + 1) * foot_len]
        if chunk == pattern:
            matching_feet += 1

    return matching_feet / total_feet


def _detect_line_meter(stress: list) -> tuple:
    """
    Detect the best-fitting meter for a single line.
    Returns (meter_name, score, foot_count).
    """
    if not stress:
        return ("Unknown", 0.0, 0)

    best_name = "Unknown"
    best_score = 0.0
    best_foot_count = 0

    for name, pattern in METER_PATTERNS.items():
        score = _score_meter_for_line(stress, name, pattern)
        foot_count = len(stress) // len(pattern)
        if score > best_score:
            best_score = score
            best_name = name
            best_foot_count = foot_count

    return (best_name, best_score, best_foot_count)

# ---------------------------------------------------------------------------
# 7. Rhyme scheme detection  (Improvement #7)
# ---------------------------------------------------------------------------
def _last_phonemes(word: str, n: int = 3) -> tuple | None:
    """Return the last `n` phonemes of a word (from CMU dict) for rhyme comparison."""
    word_lower = word.lower().strip()
    if word_lower in cmudict:
        phonemes = cmudict[word_lower][0]
        return tuple(phonemes[-n:]) if len(phonemes) >= n else tuple(phonemes)
    return None


def _detect_rhyme_scheme(lines: list) -> str:
    """
    Detects a basic rhyme scheme (e.g. ABAB, AABB) by comparing the last
    phonemes of the last word in each line.
    """
    if len(lines) < 2:
        return "N/A"

    endings = []
    for line in lines:
        words = clean_text(line).split()
        if words:
            endings.append(_last_phonemes(words[-1]))
        else:
            endings.append(None)

    # Assign letters
    scheme = []
    phoneme_to_letter: dict = {}
    next_letter = 0

    for ending in endings:
        if ending is None:
            scheme.append("?")
            continue

        # Check if we already have a matching ending
        matched = False
        for known_phoneme, letter in phoneme_to_letter.items():
            if ending == known_phoneme:
                scheme.append(letter)
                matched = True
                break
        if not matched:
            letter = chr(ord("A") + next_letter)
            phoneme_to_letter[ending] = letter
            scheme.append(letter)
            next_letter += 1

    return "".join(scheme)

# ---------------------------------------------------------------------------
# 8. Main analysis function
# ---------------------------------------------------------------------------
def analyze_meter(poem_text: str) -> dict:
    """
    Analyzes the meter of a poem.

    Returns a dict with:
      - meter_type       : dominant meter name (e.g. "Iambic Pentameter")
      - confidence       : "High" / "Medium" / "Low"
      - line_analysis    : per-line stress + detected meter
      - explanation      : human-readable summary
      - rhyme_scheme     : detected rhyme scheme string
      - foot_count_name  : e.g. "Pentameter"
    """
    lines = [line.strip() for line in poem_text.split('\n') if line.strip()]
    if not lines:
        raise ValueError("Poem text cannot be empty.")

    line_results = []
    line_meter_votes: list[str] = []
    line_foot_counts: list[int] = []

    for line in lines:
        words = clean_text(line).split()
        current_line_stress: list[int] = []

        for word in words:
            word_stress = get_word_syllables_and_stress(word, context_pattern=current_line_stress)
            current_line_stress.extend(word_stress)

        # Detect meter for THIS line independently (Improvement #2)
        line_meter, line_score, foot_count = _detect_line_meter(current_line_stress)

        line_results.append({
            "line": line,
            "stress_pattern": current_line_stress,
            "meter": line_meter,
            "score": round(line_score, 2),
            "foot_count": foot_count,
        })

        if line_meter != "Unknown":
            line_meter_votes.append(line_meter)
            line_foot_counts.append(foot_count)

    # --- Per-line voting to decide overall meter (Improvement #2) ---
    if line_meter_votes:
        vote_counter = Counter(line_meter_votes)
        dominating_meter, top_votes = vote_counter.most_common(1)[0]
        vote_ratio = top_votes / len(line_meter_votes)
    else:
        dominating_meter = "Unknown"
        vote_ratio = 0.0

    # --- Foot count (Improvement #4) ---
    if line_foot_counts:
        foot_counter = Counter(line_foot_counts)
        common_foot_count = foot_counter.most_common(1)[0][0]
        foot_count_name = FOOT_COUNT_NAMES.get(common_foot_count, f"{common_foot_count}-foot")
    else:
        common_foot_count = 0
        foot_count_name = "Unknown"

    # --- Confidence ---
    if vote_ratio > 0.7:
        confidence = "High"
    elif vote_ratio > 0.45:
        confidence = "Medium"
    else:
        confidence = "Low"
        if dominating_meter != "Unknown":
            dominating_meter = "Free Verse / Irregular"

    # --- Build full meter name (e.g. "Iambic Pentameter") ---
    if dominating_meter not in ("Unknown", "Free Verse / Irregular"):
        full_meter_name = f"{dominating_meter} {foot_count_name}"
    else:
        full_meter_name = dominating_meter

    # --- Rhyme scheme (Improvement #7) ---
    rhyme_scheme = _detect_rhyme_scheme(lines)

    # --- Explanation ---
    explanation = (
        f"The dominant stress pattern is **{full_meter_name}** "
        f"({confidence.lower()} confidence, {vote_ratio:.0%} of lines agree). "
        f"Rhyme scheme: **{rhyme_scheme}**."
    )

    return {
        "meter_type": full_meter_name,
        "confidence": confidence,
        "line_analysis": line_results,
        "explanation": explanation,
        "rhyme_scheme": rhyme_scheme,
        "foot_count_name": foot_count_name,
    }


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample = (
        "Shall I compare thee to a summer's day?\n"
        "Thou art more lovely and more temperate:\n"
        "Rough winds do shake the darling buds of May,\n"
        "And summer's lease hath all too short a date."
    )
    result = analyze_meter(sample)
    print(f"Meter : {result['meter_type']}")
    print(f"Confidence : {result['confidence']}")
    print(f"Rhyme Scheme: {result['rhyme_scheme']}")
    print(f"Explanation : {result['explanation']}")
    print()
    for ld in result["line_analysis"]:
        symbols = " ".join("×" if s == 0 else "/" for s in ld["stress_pattern"])
        print(f"  {ld['line']}")
        print(f"  {symbols}  →  {ld['meter']} ({ld['score']}) | {ld['foot_count']} feet")
        print()
