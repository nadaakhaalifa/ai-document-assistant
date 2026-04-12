from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

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
    chunks = split_text(text)
    return {
        "filename" : file.filename,
        "num_chunks": len(chunks),
        "first_chunk": chunks[0] if chunks else ""
    }

# Question endpoint
@app.get("/ask")
def ask_question(question: str):
    # fake data => Test the retrieval logic ONLY
    sample_chunks=[
        "Machine learning is a field of artificial intelligence.",
        "FastAPI is a Python framework for building APIs.",
        "RAG combines retrieval with generation."
    ]
    best_chunk = get_best_chunk(question, sample_chunks)
    return {
        "question": question,
        "best_chunk": best_chunk
    }