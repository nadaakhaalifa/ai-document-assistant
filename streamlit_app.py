import streamlit as st
import requests


st.set_page_config(page_title="AI Document Assistant", page_icon="📄", layout="centered")

st.title("AI Document Assistant")
st.write("Upload a PDF and ask questions about its content.")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")
    }
    # sends the PDF to your existing backend endpoint:
    response = requests.post("http://127.0.0.1:8000/upload", files=files)

    if response.status_code == 200:
        st.success("PDF uploaded successfully.")
    else:
        st.error("Failed to upload PDF.")
        
question = st.text_input("Ask a question about the PDF")
if st.button("Ask"):
    if not question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            response = requests.post(
                "http://127.0.0.1:8000/ask",
                json={"question": question}
            )

            if response.status_code == 200:
                answer = response.json().get("answer", "")
                st.subheader("Answer")
                st.write(answer)
            else:
                st.error("Failed to get answer. Make sure you uploaded a PDF first.")