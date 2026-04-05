import streamlit as st

# Set page config at the very top
st.set_page_config(
    page_title="AI Text Intelligence Platform",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dynamic UI
st.markdown("""
<style>
    /* Main container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    /* Headers */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        color: #2e3b4e;
        text-align: center;
        margin-bottom: 1rem;
    }
    h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #4a5568;
    }
    /* Stylish results cards */
    .result-card {
        background-color: #f8fafc;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-left: 5px solid #3b82f6;
        transition: transform 0.2s;
    }
    .result-card:hover {
        transform: translateY(-2px);
    }
    /* Keywords badge */
    .keyword-badge {
        display: inline-block;
        padding: 5px 12px;
        margin: 4px;
        background-color: #e2e8f0;
        color: #1e293b;
        border-radius: 9999px;
        font-size: 0.85em;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Import our custom modules
from modules.song_interpreter import interpret_song
from modules.poetry_meter import analyze_meter
from modules.summarizer import load_summarizer, summarize_text

# Sidebar setup
st.sidebar.title("🧠 AI Functions")
st.sidebar.markdown("Select a feature to explore:")
feature = st.sidebar.radio(
    "Available Features",
    ["🎵 Song Meaning Interpreter", "✍️ Poetry Meter Checker", "📝 Text Summarization Tool"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**About**")
st.sidebar.info(
    "The AI Text Intelligence Platform is a suite of advanced natural language "
    "processing tools designed to help you analyze, interpret, and summarize text."
)

st.title("AI Text Intelligence Platform")

if feature == "🎵 Song Meaning Interpreter":
    st.markdown("### Song Meaning Interpreter")
    st.write("Paste your lyrics below, and the AI will determine the emotional tone, main theme, and provide an interpretation.")
    
    lyrics_input = st.text_area("Enter Song Lyrics:", height=250, placeholder="E.g., I'm holding out for a hero 'til the end of the night...")
    
    if st.button("Interpret Meaning", type="primary"):
        if not lyrics_input.strip():
            st.error("Please enter some lyrics first!")
        else:
            with st.spinner("Analyzing lyrics..."):
                try:
                    result = interpret_song(lyrics_input)
                    
                    st.success("Analysis Complete!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Detected Emotion", result.get("emotion"))
                    with col2:
                        st.metric("Primary Theme", result.get("theme"))
                        
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown("#### Meaning Summary")
                    st.write(result.get("meaning_explanation"))
                    
                    st.markdown("#### Top Keywords")
                    keywords_html = "".join([f'<span class="keyword-badge">{kw}</span>' for kw in result.get("top_keywords", [])])
                    st.markdown(keywords_html, unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error analyzing lyrics: {str(e)}")

elif feature == "✍️ Poetry Meter Checker":
    st.markdown("### Poetry Meter Checker")
    st.write("Enter a poem to analyze its phonemes, stress patterns, and rhythmic meter.")
    
    poem_input = st.text_area("Enter Poem:", height=200, placeholder="E.g., Shall I compare thee to a summer's day?\nThou art more lovely and more temperate...")
    
    if st.button("Check Meter", type="primary"):
        if not poem_input.strip():
            st.error("Please enter a poem.")
        else:
            with st.spinner("Extracting phonemes and checking meter..."):
                try:
                    result = analyze_meter(poem_input)
                    
                    st.success("Analysis Complete!")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Dominant Meter", result.get("meter_type"))
                    with col2:
                        st.metric("Confidence", result.get("confidence"))
                        
                    st.info(result.get("explanation"))
                    
                    st.markdown("#### Line-by-Line Stress Analysis")
                    st.caption("0 = Unstressed | 1 = Stressed")
                    for line_data in result.get("line_analysis", []):
                        st.write(f"**Line:** {line_data['line']}")
                        st.write(f"**Pattern:** `{' '.join(map(str, line_data['stress_pattern']))}`")
                        st.divider()
                except Exception as e:
                    st.error(f"Error checking meter: {str(e)}")

elif feature == "📝 Text Summarization Tool":
    st.markdown("### Text Summarization Tool")
    st.write("Provide a long paragraph or article, and our local transformer model will summarize it for you.")
    
    # Load summarizer with spinner on first run
    with st.spinner("Loading Transformer model... (this may take a moment on first run)"):
        summarizer_model = load_summarizer()
    
    text_input = st.text_area("Enter Text to Summarize:", height=300, placeholder="Paste a long article or document here...")
    
    if st.button("Generate Summary", type="primary"):
        if not text_input.strip():
            st.error("Please enter text to summarize.")
        else:
            with st.spinner("Generating summary..."):
                try:
                    summary = summarize_text(text_input, summarizer_model)
                    st.success("Summary Generated!")
                    
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown("#### Summary Output")
                    st.write(summary)
                    st.markdown('</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error generating summary: {str(e)}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>Built with ❤️ using Python & Streamlit</p>", unsafe_allow_html=True)
