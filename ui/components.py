import streamlit as st

def setup_ui():
    """Setup Streamlit UI with custom CSS"""
    st.set_page_config(
        page_title="aSES - Student Engagement System",
        page_icon="📚",
        layout="wide"
    )
    
    st.markdown("""
        <style>
        .main { 
            background-color: #f8fafc; 
            font-It does not look like there is anything to change in this artifact, please provide more details or a new artifact to edit family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        }
        .stButton>button { 
            background: linear-gradient(90deg, #3b82f6, #1d4ed8);
            color: white; 
            border-radius: 8px; 
            padding: 0.5rem 1rem; 
            font-weight: 600;
            border: none;
            transition: all 0.3s ease;
        }
        .stButton>button:hover { 
            background: linear-gradient(90deg, #1d4ed8, #1e40af);
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        .title { 
            color: #1e40af; 
            font-size: 2.5rem; 
            font-weight: 700; 
            text-align: center; 
            margin-bottom: 1rem;
            background: linear-gradient(90deg, #3b82f6, #1d4ed8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .subtitle { 
            color: #64748b; 
            font-size: 1.1rem; 
            text-align: center;
            margin-bottom: 2rem; 
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-left: 4px solid #3b82f6;
        }
        </style>
    """, unsafe_allow_html=True)