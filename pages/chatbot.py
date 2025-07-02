import streamlit as st
import ollama
import os

# Initialize session state for conversation history
if "interaction" not in st.session_state:
    st.session_state.interaction = [
        {
            "role": "system",
            "content": "You are a helpful assistant for students, providing guidance on lectures and engagement tips.",
        }
    ]
    st.session_state.messages = []

# Function to interact with Ollama model
def get_response(input_message, image_paths=None):
    interaction = st.session_state.interaction
    if image_paths:
        interaction.append({
            "role": "user",
            "content": f"{input_message} (Images uploaded: {', '.join(image_paths)})",
        })
    else:
        interaction.append({
            "role": "user",
            "content": input_message,
        })
    try:
        response = ollama.chat(model="gemma3:4b", messages=interaction)
        interaction.append({
            "role": "assistant",
            "content": response['message']['content'],
        })
        return response['message']['content']
    except Exception as e:
        return f"Error: Could not connect to Ollama model. Ensure it is running. ({str(e)})"

# Streamlit app layout
st.title("Local Chat Assistant")
st.write("Powered by Google Deepmind's Gemma 3")

# Display initial message
if not st.session_state.messages:
    initial_message = "Hello, I'm your local assistant powered by Gemma 3. I can help with lecture questions or engagement tips. How can I assist you?"
    st.session_state.messages.append({"role": "assistant", "content": initial_message})

# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input section
with st.container():
    user_input = st.chat_input("Type your message here...")
    uploaded_files = st.file_uploader("Upload images (optional)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        image_paths = []
        if uploaded_files:
            image_paths = [file.name for file in uploaded_files]
            st.write(f"Uploaded images: {', '.join(image_paths)}")

        with st.chat_message("assistant"):
            response = get_response(user_input, image_paths)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown('<div style="text-align: center; color: #6b7280; font-size: 0.9em; margin-top: 20px;">Local Chat Assistant v1.0 | Powered by Gemma 3</div>', unsafe_allow_html=True)