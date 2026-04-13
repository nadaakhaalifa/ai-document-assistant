# AI Document Assistant

An AI-powered document assistant built with FastAPI and OpenAI that uses Retrieval-Augmented Generation (RAG) to answer questions from uploaded PDFs.

## Features
- Upload PDF documents
- Intelligent chunking & embedding
- Semantic search using cosine similarity
- LLM-powered answer generation
- Clean and simple API

## Architecture
1. PDF → text extraction
2. Text → chunks
3. Chunks → embeddings
4. Question → embedding
5. Similarity search (top-k)
6. LLM generates answer using context

## Tech Stack

- Python  
- FastAPI  
- Sentence Transformers  
- OpenAI API  

## API Endpoints

### Upload PDF
POST /upload

### Ask Question
POST /ask

## How to run

```bash
git clone <your-repo>
cd ai-document-assistant
python3 -m venv ai-venv
source ai-venv/bin/activate
pip install -r requirements.txt
```

## Environment
Create a `.env` file:
```env
OPENAI_API_KEY=your_api_key_here
```

## Run server 
```bash
uvicorn main:app --reload
```

## Open docs
http://127.0.0.1:8000/docs

## Example request

```json
{
  "question": "What is this document about?"
}
```

## Notes
This is a basic RAG implementation
Data is stored in memory (not persistent yet)
.env is not included for security reasons


