import io
import os
import streamlit as st
from dotenv import load_dotenv

from utils.api import upload_pdf, query_backend

load_dotenv()

st.set_page_config(page_title="ResearchRAG UI", page_icon="🔎", layout="wide")

if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False
if "last_stats" not in st.session_state:
    st.session_state.last_stats = None
if "history" not in st.session_state:
    st.session_state.history = []

st.title("ResearchRAG — Streamlit UI")
st.caption("Upload a PDF, then ask questions. Backend: FastAPI + Redis + Vector Search + Summarization + Re-ranking.")

# Sidebar: backend status / config
with st.sidebar:
    st.subheader("Backend")
    st.write("`BACKEND_URL`:", os.getenv("BACKEND_URL", "http://127.0.0.1:8000"))
    st.markdown("---")
    st.write("1) Upload a PDF")
    st.write("2) Ask a question")

# Upload PDF
st.header("1) Upload PDF")
file = st.file_uploader("Choose a PDF", type=["pdf"])

col1, col2 = st.columns([1, 3])
with col1:
    upload_btn = st.button("Process PDF", disabled=(file is None))
with col2:
    clear_btn = st.button("Clear Session")

if clear_btn:
    st.session_state.clear()
    st.experimental_rerun()

if upload_btn and file is not None:
    try:
        with st.spinner("Uploading and indexing…"):
            pdf_bytes = file.read()
            result = upload_pdf(pdf_bytes, file.name)
        st.session_state.pdf_uploaded = True
        st.session_state.last_stats = result.get("stats", result)
        st.success("PDF processed successfully.")
    except Exception as e:
        st.error(f"Upload failed: {e}")

if st.session_state.pdf_uploaded and st.session_state.last_stats:
    st.info(
        f"Indexed — Texts: {st.session_state.last_stats.get('texts', '?')}, "
        f"Tables: {st.session_state.last_stats.get('tables', '?')}, "
        f"Images: {st.session_state.last_stats.get('images', '?')}"
    )

# Ask a question
st.header("2) Ask a Question")
question = st.text_input("Enter your question")
ask_btn = st.button("Ask", disabled=not st.session_state.pdf_uploaded or not question.strip())

if ask_btn:
    try:
        with st.spinner("Retrieving and generating answer…"):
            resp = query_backend(question.strip())
        st.session_state.history.append(
            {
                "question": resp.get("query", question),
                "filter": resp.get("filter", {}),
                "answer": resp.get("answer", ""),
            }
        )
    except Exception as e:
        st.error(f"Query failed: {e}")

# Chat-like history
if st.session_state.history:
    st.header("History")
    for i, turn in enumerate(reversed(st.session_state.history), 1):
        st.markdown(f"**Q:** {turn['question']}")
        filt = turn.get("filter") or {}
        if filt:
            with st.expander("Applied metadata filter"):
                st.json(filt)
        st.markdown("**A:**")
        st.write(turn["answer"])
        st.markdown("---")