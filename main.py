from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
stored_chunks = []

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
def get_best_chunk(question, chunks):
    if not chunks:
        return""
    
    # convert all chunks and the question into vectors
    chunk_embeddings = embedding_model.encode(chunks)
    question_embeddings = embedding_model.encode([question])
    
    # compare the question with all chunks {highest score means the most relevant chunk}
    scores = cosine_similarity (question_embeddings, chunk_embeddings)[0]
    
    # get the index of highest score and return it 
    best_index = scores.argmax()
    return chunks [best_index]

# upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content= await file.read()
    
    if file.content_type != "application/pdf":
        return {"error" : "Only PDF supported"}
    
    with open("temp.pdf","wb") as f:
        f.write(content)
        
    reader = PdfReader("temp.pdf")
    text=""
    
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
           text += page_text
           
    global stored_chunks
    stored_chunks = split_text(text)
    
    return {
        "filename" : file.filename,
        "num_chunks": len(stored_chunks),
        "first_chunk": stored_chunks[0] if stored_chunks else ""
    }

# Question endpoint
@app.get("/ask")
def ask_question(question: str):
    global stored_chunks
    
    if not stored_chunks:
       return {"error": "No document uploaded yet"}
   
    best_chunk = get_best_chunk(question, stored_chunks)
    
    return {
        "question": question,
        "best_chunk": best_chunk
    }