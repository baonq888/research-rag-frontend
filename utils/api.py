import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

def upload_pdf(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Calls FastAPI POST /upload with the PDF file.
    """
    url = f"{BACKEND_URL}/upload"
    files = {"file": (filename, file_bytes, "application/pdf")}
    resp = requests.post(url, files=files, timeout=300)
    resp.raise_for_status()
    return resp.json()

def query_backend(question: str) -> Dict[str, Any]:
    """
    Calls FastAPI GET /query?question=...
    """
    url = f"{BACKEND_URL}/query"
    params = {"question": question}
    resp = requests.get(url, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()