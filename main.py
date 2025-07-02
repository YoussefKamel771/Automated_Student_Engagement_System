import streamlit as st
import os
from config.settings import EngagementConfig
from core.data_models import SessionData
from ui.components import setup_ui
from ui.session_ui import run_engagement_session
from services.chatbot_service import ChatbotManager
from config.logging_config import setup_logging

logger = setup_logging()

def main():
    """Main application function"""
    setup_ui()
    
    # Check for required model file
    model_path = os.path.join(os.getcwd(), "artifacts", "shape_predictor_68_face_landmarks.dat")
    if not os.path.exists(model_path):
        st.error("❌ Required model file 'shape_predictor_68_face_landmarks.dat' not found!", icon="❌")
        st.info("📥 Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
        st.stop()
    
    # Initialize chatbot manager
    chatbot = ChatbotManager()
    chatbot.start()
    
    # Header
    st.markdown('<div class="title">📚 aSES: Automated Student Engagement System</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Monitor and analyze student engagement with AI-powered detection</div>', 
                unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### 🔧 Session Configuration")
        
        with st.form("session_form", clear_on_submit=False):
            name = st.text_input("👤 Student Name", placeholder="Enter full name")
            matric_id = st.text_input("🆔 Matric Number", placeholder="e.g., A123456")
            course = st.text_input("📖 Course", placeholder="e.g., CS101")
            group = st.text_input("👥 Group", placeholder="e.g., Group 1")
            module = st.text_input("📋 Module", placeholder="e.g., Lecture 1")
            duration = st.slider("⏱️ Duration (minutes)", 1, 120, 10)
            
            col1, col2 = st.columns(2)
            with col1:
                start_button = st.form_submit_button("▶️ Start", use_container_width=True)
            with col2:
                reset_button = st.form_submit_button("🔄 Reset", use_container_width=True)
        
        if reset_button:
            st.session_state.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 🤖 Assistant")
        st.markdown(f"[💬 Open Chatbot](http://localhost:{chatbot.port})")
        
        st.markdown("---")
        st.markdown("### ℹ️ System Info")
        st.info("Ensure good lighting and face the camera directly for optimal detection.")
    
    # Main content area
    if start_button:
        # Validate inputs
        required_fields = [name, matric_id, course, group, module]
        if not all(required_fields):
            st.error("⚠️ Please fill in all required fields.", icon="❌")
        else:
            session = SessionData(name, matric_id, course, group, module, duration)
            
            with st.spinner("🚀 Initializing engagement monitoring..."):
                run_engagement_session(session, model_path)
    else:
        # Welcome screen
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                ### 🎯 Welcome to aSES
                
                **Key Features:**
                - 👁️ Real-time eye tracking and engagement detection
                - 🎯 Adaptive calibration for individual users  
                - 📊 Comprehensive engagement analytics
                - 🔊 Voice alerts for disengagement
                - 💾 Automatic data logging and backup
                
                **Get Started:**
                1. Fill in your session details in the sidebar
                2. Click "Start" to begin monitoring
                3. Look directly at the camera during calibration
                4. Review your engagement summary at the end
            """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #64748b; font-size: 0.9rem;">'
        'aSES v2.0 | Optimized for Performance & Reliability | Educational Use</div>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()