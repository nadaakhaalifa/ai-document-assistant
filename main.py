from fastapi import FastAPI, UploadFile, File, HTTPException
from PyPDF2 import PdfReader
from sklearn.metrics.pairwise import cosine_similarity

from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import os

# Go read file .env now so the API become available to the code
load_dotenv()

# gets the key from .env , creates a connection to openAI, client => what i use to ask AI Q[PHONE TO CALL OPENAI]
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
# embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
# embedding_model = None
stored_chunks = []

# def get_model():
#     global embedding_model
#     if embedding_model is None:
#         from sentence_transformers import SentenceTransformer
#         embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
#     return embedding_model

class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message":"API is working"}

# chunking function
def split_text(text, chunk_size=500):
    chunks = []

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)

    return chunks 


# retrieval function
def get_top_chunks(question, chunks, k=3):
    if not chunks:
        return []

    question_words = question.lower().split()

    scored_chunks = []
    for chunk in chunks:
        score = sum(word in chunk.lower() for word in question_words)
        scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:k]]

# def get_top_chunks(question, chunks, k=3):
#     if not chunks:
#         return []
#     return chunks[:k]

# asks OpenAI {send text to AI }
def ask_llm(question: str, context: str):
    # be helpful, don't use outside knowledge[only pdf content], if u don't know just say idk
    prompt= f"""
You are a helpful assistant.
Answer the question only using the context below.
If the answer is not in the context, say: "I could not find that in the document."


Context:
{context}

Question:
{question}
"""
    # asks OpenAI for an answer
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    # gives us the final answer text
    return response.output_text



# upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global stored_chunks

    if file.content_type != "application/pdf":
        return {"error" : "Only PDF supported"}
    content= await file.read()
    
    temp_file_path = "temp.pdf"
    with open("temp.pdf","wb") as f:
        f.write(content)
        
    try:
        reader = PdfReader(temp_file_path)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        stored_chunks = split_text(text)

        return {
            "filename": file.filename,
            "num_chunks": len(stored_chunks),
            "first_chunk": stored_chunks[0] if stored_chunks else ""
        }
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Question endpoint
@app.post("/ask")
def ask_question(data: QuestionRequest):    
    if not stored_chunks:
       raise HTTPException(status_code=400, detail="Please upload a PDF first")
   
    try:
        top_chunks = get_top_chunks(data.question, stored_chunks)
        context = "\n".join(top_chunks)

        answer = ask_llm(data.question, context)
        return {
        "question": data.question,
        "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while answering question: {str(e)}")
    
