# AI Text Intelligence Platform

A complete, AI-powered web application built using Python and Streamlit. This application is modular, well-documented, and production-ready. It demonstrates practical NLP applications using rules, dictionaries, and modern transformer models.

## Features

1. **Song Meaning Interpreter**
   - Natural language processing for text cleaning and tokenization.
   - VADER Sentiment analysis to determine the song's emotional tone.
   - Keyword-based theme extraction to identify concepts like Love, Heartbreak, or Motivation.
   
2. **Poetry Meter Checker**
   - Integrates the CMU Pronouncing Dictionary to extract phonemes.
   - Identifies stress patterns (unstressed/stressed syllables).
   - Algorithmically guesses the dominant meter pattern (e.g., Iambic, Trochaic).

3. **Text Summarization Tool**
   - Leverages Hugging Face Transformers (`facebook/bart` or `distilbart`).
   - Dynamically processes long-form text.
   - Performs abstractive summarization to return a concise version of the original string.

## Tech Stack

- **Frontend**: Streamlit
- **Core Languages**: Python 3.9+
- **NLP Libraries**: `nltk`, `transformers`, `torch`
- **Machine Learning**: HuggingFace Pipelines

## Installation Steps

1. **Clone the repository** (if applicable) or navigate to the project directory:
   ```bash
   cd ai-text-intelligence
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize NLTK Data**:
   The app will automatically attempt to download required NLTK corpora (`punkt`, `stopwords`, `vader_lexicon`, `cmudict`) on first launch.

## How to Run the App

Execute the following command in your terminal from within the project directory:
```bash
streamlit run app.py
```

## Example Inputs and Outputs

### Song Interpretation
**Input**: _"I will always love you, my heart will go on forever. Even when we say goodbye, I won't cry."_
**Output**: 
- **Emotion:** Highly Positive / Joyful
- **Theme:** Love & Romance
- **Keywords:** love, heart, forever, goodbye, cry.

### Poetry Meter Checker
**Input**: _"Shall I compare thee to a summer's day?"_
**Output**: 
- **Pattern:** `0 1 0 1 0 0 0 1 0 1`
- **Meter Type:** Iambic

### Text Summarization
**Input**: A 500-word paragraph describing Natural Language Processing.
**Output**: A clean, 2-3 sentence summary extracting the key definition and goals of NLP.
