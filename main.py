from fastapi import FastAPI, UploadFile, File, HTTPException
from PyPDF2 import PdfReader
# from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import os
import numpy as np
import faiss


# Go read file .env now so the API become available to the code
load_dotenv()

# gets the key from .env , creates a connection to openAI, client => what i use to ask AI Q[PHONE TO CALL OPENAI]
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

stored_chunks = []
faiss_index = None


class QuestionRequest(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message":"API is working"}

# chunking function
def split_text(text: str, chunk_size: int = 500, overlap: int = 100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
        
    return chunks 



def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding



def build_faiss_index(chunks):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=chunks
    )
    embeddings = [get_embedding(chunk) for chunk in chunks]
    embeddings = np.array(embeddings, dtype="float32")

    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    return index


# retrieval function
def get_top_chunks( question: str, k: int = 3):
    global stored_chunks, faiss_index

    if not stored_chunks or faiss_index is None:
        return []

    question_embedding = np.array([get_embedding(question)], dtype="float32")
    faiss.normalize_L2(question_embedding)

    distances, indices = faiss_index.search(question_embedding, k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(stored_chunks):
            results.append(stored_chunks[idx])

    return results


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
    global stored_chunks, faiss_index

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF supported")
    
    content= await file.read()  
    temp_file_path = "temp.pdf"
    
    with open(temp_file_path, "wb") as f:
        f.write(content)
        
    try:
        reader = PdfReader(temp_file_path)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")

        stored_chunks = split_text(text)
        faiss_index = build_faiss_index(stored_chunks)

        return {
            "message": "PDF uploaded and indexed successfully",
            "filename": file.filename,
            "num_chunks": len(stored_chunks),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Question endpoint
@app.post("/ask")
def ask_question(data: QuestionRequest):
    global stored_chunks, faiss_index
        
    if not stored_chunks or faiss_index is None:
       raise HTTPException(status_code=400, detail="Please upload a PDF first")
   
    try:
        top_chunks = get_top_chunks(data.question, k=3)
        context = "\n\n".join(top_chunks)
        answer = ask_llm(data.question, context)
        
        return {
        "question": data.question,
        "answer": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while answering question: {str(e)}")
    
