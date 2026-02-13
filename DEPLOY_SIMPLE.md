# 🚀 Simple Deployment Guide

## For Streamlit Cloud:

### Files to use:
- **Main app**: `app_deploy.py` 
- **Requirements**: `requirements_minimal.txt`

### Steps:
1. In Streamlit Cloud, set main file to: `app_deploy.py`
2. Rename `requirements_minimal.txt` to `requirements.txt` 
3. Add secret: `GROQ_API_KEY = "your_key_here"`
4. Deploy!

### What this version includes:
✅ Beautiful animated UI  
✅ PDF upload and processing  
✅ AI chat with GROQ  
✅ Mark-based responses (1, 2, 10, 12 marks)  
✅ Mobile responsive  
✅ Error handling  

### Minimal dependencies:
- streamlit (UI framework)
- PyPDF2 (PDF processing)  
- langchain-groq (AI model)
- python-dotenv (environment variables)

This simplified version removes complex vector store dependencies that cause deployment issues while keeping all the core functionality and beautiful animations.