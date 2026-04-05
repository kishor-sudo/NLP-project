import streamlit as st
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

@st.cache_resource
def load_summarizer():
    """
    Loads the Hugging Face summarization tokenizer and model explicitly.
    We are using a smaller DistilBART model to save resources.
    By loading the model directly instead of using `pipeline`, we bypass issues with missing pipeline tasks.
    """
    model_name = "sshleifer/distilbart-cnn-12-6"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

def summarize_text(long_text: str, summarizer) -> str:
    """
    Generates a concise summary for the input text.
    """
    if not long_text or not long_text.strip():
        raise ValueError("Text to summarize cannot be empty.")
    
    input_length = len(long_text.split())
    if input_length < 20:
        return "Text is too short to summarize properly. Please provide a longer paragraph."
        
    max_len = min(130, max(20, input_length // 2))
    min_len = min(30, max(10, input_length // 4))

    tokenizer, model = summarizer
    
    # Tokenize input
    inputs = tokenizer([long_text], max_length=1024, return_tensors="pt", truncation=True)
    
    # Generate summary tokens
    summary_ids = model.generate(
        inputs["input_ids"], 
        num_beams=4, 
        max_length=max_len, 
        min_length=min_len, 
        early_stopping=True
    )
    
    # Decode to text
    summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True, clean_up_tokenization_spaces=False)
    return summary_text.strip()

if __name__ == "__main__":
    # Test block
    simulated_text = "Natural language processing (NLP) is an interdisciplinary subfield of computer science and linguistics. It is primarily concerned with giving computers the ability to support and manipulate human language. It involves processing natural language datasets, such as text corpora or speech corpora, using either rule-based or probabilistic (i.e. statistical and, most recently, neural network-based) machine learning approaches."
    try:
        model_pack = load_summarizer()
        print(summarize_text(simulated_text, model_pack))
    except Exception as e:
        print(f"Error loading local model: {e}")
