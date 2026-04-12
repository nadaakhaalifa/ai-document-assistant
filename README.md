# AI Document Assistant

This project is a simple AI-powered document assistant built using FastAPI, embeddings, and OpenAI.

The idea is to upload a PDF, find the most relevant part of the document using embeddings, and then use an LLM to generate an answer based on that context.

## How it works

1. Upload a PDF file  
2. Extract and split text into chunks  
3. Convert chunks into embeddings  
4. Compare the question with chunks using cosine similarity  
5. Retrieve the most relevant chunk  
6. Send it to OpenAI to generate the final answer  

## Tech Stack

- Python  
- FastAPI  
- Sentence Transformers  
- OpenAI API  

## How to run

```bash
git clone <your-repo>
cd ai-document-assistant
python3 -m venv ai-venv
source ai-venv/bin/activate
pip install -r requirements.txt
```

## environment file 
create `.env` 
OPENAI_API_KEY=your_api_key_here

## Run server 
```bash
uvicorn main:app --reload
```

## Open docs
http://127.0.0.1:8000/docs

## Example request
json:
{
  "question": "What is this document about?"
}

## Notes
This is a basic RAG implementation
Data is stored in memory (not persistent yet)
.env is not included for security reasons


