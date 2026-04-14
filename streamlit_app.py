import streamlit as st
import requests
import os 
import hashlib

# Page setup (title, icon, layout)
st.set_page_config(page_title="AI Document Assistant", page_icon="📄", layout="centered")

# Backend API URL (from env or fallback to deployed backend)
API_URL = os.getenv("API_URL", "https://fastapi-backend-ekgg.onrender.com")

# UI Title
st.title("AI Document Assistant")
st.write("Upload a PDF and ask questions about its content.")

# use session_state to persist values across Streamlit reruns

# Store hash of uploaded file → used to detect if user uploaded a NEW file
if "uploaded_file_hash" not in st.session_state:
    st.session_state.uploaded_file_hash = None
    
# Flag to know if PDF is already uploaded to backend
# Prevents re-uploading on every rerun
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False


# FILE UPLOADER
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# If user removes the file → reset session state
# This keeps frontend and backend in sync
if uploaded_file is None:
    st.session_state.pdf_uploaded = False
    st.session_state.uploaded_file_hash = None

# HANDLE PDF UPLOAD
if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    current_file_hash = hashlib.md5(file_bytes).hexdigest()

    if st.session_state.uploaded_file_hash != current_file_hash:
        st.session_state.uploaded_file_hash = current_file_hash
        st.session_state.pdf_uploaded = False
        
    # # This prevents multiple API calls due to Streamlit reruns
    if not st.session_state.pdf_uploaded:
        files = {
            "file": (uploaded_file.name, file_bytes, "application/pdf")
        }
    
        try:
            with st.spinner("Uploading and processing PDF..."):
                response = requests.post(f"{API_URL}/upload", files=files, timeout=120)

            if response.status_code == 200:
                st.success("PDF uploaded successfully.")
                st.session_state.pdf_uploaded = True
            else:
                error_message = response.text
                try:
                    error_message = response.json().get("detail", response.text)
                except Exception:
                    pass
                st.error(f"Failed to upload PDF.\n\n{error_message}")

        except Exception as e:
            st.error(f"Error while uploading PDF: {str(e)}")

    else:
        st.success("PDF uploaded successfully.")
        
# QUESTION INPUT        
question = st.text_input("Ask a question about the PDF")

#  ASK BUTTON LOGIC
if st.button("Ask"):
    if not st.session_state.pdf_uploaded:
        st.warning("Please upload a PDF first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            with st.spinner("Generating answer..."):
                response = requests.post(
                    f"{API_URL}/ask",
                    json={"question": question},
                    timeout=120
                )

            if response.status_code == 200:
                data = response.json()
                st.subheader("Answer")
                st.write(data["answer"])
            else:
                error_message = response.text
                try:
                    error_message = response.json().get("detail", response.text)
                except Exception:
                    pass
                st.error(f"Failed to get answer.\n\n{error_message}")

        except Exception as e:
            st.error(f"Error while asking question: {str(e)}")
                
                