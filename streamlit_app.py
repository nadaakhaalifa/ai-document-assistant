import streamlit as st
import requests
import os 

st.set_page_config(page_title="AI Document Assistant", page_icon="📄", layout="centered")

API_URL = os.getenv("API_URL", "https://ai-document-assistant-nv3p.onrender.com")

st.title("AI Document Assistant")
st.write("Upload a PDF and ask questions about its content.")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
    }
    
    try:
        response = requests.post(f"{API_URL}/upload", files=files, timeout=120)

        if response.status_code == 200:
            st.success("PDF uploaded successfully.")
        else:
            st.error("Failed to upload PDF.")
            st.write(response.text)
    except Exception as e:
        st.error(f"Upload failed: {e}")
        
question = st.text_input("Ask a question about the PDF")

if st.button("Ask"):
    if not question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question},
                    timeout=120
                )

                if response.status_code == 200:
                    answer = response.json().get("answer", "")
                    st.subheader("Answer")
                    st.write(answer)
                else:
                    st.error("Failed to get answer. Make sure you uploaded a PDF first.")
            except Exception as e:
                st.error(f"Request failed: {e}")
                
                