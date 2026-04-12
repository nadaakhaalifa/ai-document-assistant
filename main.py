from fastapi import FastAPI, UploadFile, File
from PyPDF2 import PdfReader

app = FastAPI()

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
