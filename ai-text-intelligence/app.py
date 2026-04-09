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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    /* Main container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    /* Headers */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #8b5cf6 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    h2 {
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
        text-align: center;
    }
    h3 {
        font-family: 'Inter', sans-serif;
        color: #f1f5f9;
        margin-top: 0;
    }
    /* Stylish Glassmorphism Results Cards */
    .result-card {
        background-color: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #6366f1;
        transition: transform 0.2s, box-shadow 0.2s;
        color: #f8fafc;
    }
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
    }
    /* Keywords badge - Neon touch */
    .keyword-badge {
        display: inline-block;
        padding: 5px 12px;
        margin: 4px;
        background-color: rgba(99, 102, 241, 0.15);
        color: #c7d2fe;
        border: 1px solid rgba(99, 102, 241, 0.3);
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



st.title("AI Text Intelligence Platform")

if feature == "🎵 Song Meaning Interpreter":
    st.markdown("<h3 style='text-align: center;'>Song Meaning Interpreter</h3>", unsafe_allow_html=True)
    st.write("<p style='text-align: center;'>Paste your lyrics below, and the AI will determine the emotional tone, main theme, and provide an interpretation.</p>", unsafe_allow_html=True)
    st.divider()
    
    input_col, result_col = st.columns([1, 1], gap="large")
    
    with input_col:
        lyrics_input = st.text_area("Enter Song Lyrics:", height=300, placeholder="E.g., I'm holding out for a hero 'til the end of the night...")
        analyze_btn = st.button("Interpret Meaning", type="primary", use_container_width=True)
        
    with result_col:
        if analyze_btn:
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
    st.markdown("<h3 style='text-align: center;'>Poetry Meter Checker</h3>", unsafe_allow_html=True)
    st.write("<p style='text-align: center;'>Enter a poem to analyze its phonemes, stress patterns, and rhythmic meter.</p>", unsafe_allow_html=True)
    st.divider()
    
    input_col, result_col = st.columns([1, 1], gap="large")
    
    with input_col:
        poem_input = st.text_area("Enter Poem:", height=300, placeholder="E.g., Shall I compare thee to a summer's day?\nThou art more lovely and more temperate...")
        check_meter_btn = st.button("Check Meter", type="primary", use_container_width=True)
        
    with result_col:
        if check_meter_btn:
            if not poem_input.strip():
                st.error("Please enter a poem.")
            else:
                with st.spinner("Extracting phonemes and checking meter..."):
                    try:
                        result = analyze_meter(poem_input)
                        
                        st.success("Analysis Complete!")
                        st.markdown('<div class="result-card">', unsafe_allow_html=True)
                        tab1, tab2 = st.tabs(["📊 Meter Summary", "🔍 Line-By-Line Breakdown"])
                        
                        with tab1:
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Dominant Meter", result.get("meter_type"))
                            col2.metric("Confidence", result.get("confidence"))
                            col3.metric("Rhyme Scheme", result.get("rhyme_scheme", "N/A"))
                            st.info(result.get("explanation"))
                            
                        with tab2:
                            st.caption("× = Unstressed  |  / = Stressed")
                            for line_data in result.get("line_analysis", []):
                                symbols = " ".join("×" if s == 0 else "/" for s in line_data["stress_pattern"])
                                meter_label = line_data.get("meter", "")
                                score_label = line_data.get("score", "")
                                foot_label = line_data.get("foot_count", "")
                                
                                st.write(f"**Line:** {line_data['line']}")
                                st.write(f"**Stress:** `{symbols}`")
                                st.write(f"**Detected:** {meter_label} ({foot_label} feet) — score: {score_label}")
                                st.divider()
                        st.markdown('</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error checking meter: {str(e)}")

elif feature == "📝 Text Summarization Tool":
    st.markdown("<h3 style='text-align: center;'>Text Summarization Tool</h3>", unsafe_allow_html=True)
    st.write("<p style='text-align: center;'>Provide a long paragraph or article, and our local transformer model will summarize it for you.</p>", unsafe_allow_html=True)
    st.divider()
    
    # Load summarizer with spinner on first run
    with st.spinner("Loading Transformer model... (this may take a moment on first run)"):
        summarizer_model = load_summarizer()
    
    input_col, result_col = st.columns([1, 1], gap="large")
    
    with input_col:
        text_input = st.text_area("Enter Text to Summarize:", height=300, placeholder="Paste a long article or document here...")
        summarize_btn = st.button("Generate Summary", type="primary", use_container_width=True)
        
    with result_col:
        if summarize_btn:
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

