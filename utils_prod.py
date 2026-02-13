import io
import os
import re
import time
import streamlit as st
from PyPDF2 import PdfReader
from typing import Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_data(show_spinner=False)
def parse_pdf_info(file_bytes: bytes, filename: str) -> Tuple[str, int]:
    """Parse PDF and extract text with caching"""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages = len(reader.pages)
        
        if pages > 100:  # Limit for performance
            st.warning(f"⚠️ Large PDF detected ({pages} pages). Processing first 100 pages only.")
            pages = 100
            
        text = ""
        for i, page in enumerate(reader.pages[:pages]):
            if i >= 100:  # Safety check
                break
            page_text = page.extract_text() or ""
            text += page_text + "\n"
            
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
            
        logger.info(f"Successfully processed PDF: {filename} ({pages} pages)")
        return text.strip(), pages
        
    except Exception as e:
        logger.error(f"Error processing PDF {filename}: {str(e)}")
        raise ValueError(f"Failed to process PDF: {str(e)}")

def detect_marks(question: str) -> Optional[int]:
    """Detect marks from question text"""
    if not question:
        return None
        
    question_lower = question.lower()
    
    # Pattern matching for marks
    patterns = [
        r"(\b1\b|\b2\b|\b10\b|\b12\b)\s*mark",
        r"(\b10\b|\b12\b)\s*marks",
        r"\bfor\s*(1|2|10|12)\s*marks?\b"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, question_lower)
        if match:
            return int(match.group(1))
    
    return None

def format_question(question: str) -> str:
    """Format question with mark-based guidance"""
    if not question or not question.strip():
        return question
        
    marks = detect_marks(question)
    if marks is None:
        return question
    
    guidance = {
        1: "Provide a one-line definition suitable for 1 mark.",
        2: "Provide 2–3 concise bullet points suitable for 2 marks.",
        10: "Provide a structured, detailed explanation suitable for 10 marks.",
        12: "Provide a structured, comprehensive explanation suitable for 12 marks."
    }
    
    guide_text = guidance.get(marks, "Provide an appropriate response.")
    return f"{question}\n\nMarks: {marks}\n{guide_text}"

def validate_file_upload(uploaded_file) -> bool:
    """Validate uploaded file"""
    if not uploaded_file:
        return False
        
    # Check file size (10MB limit)
    if uploaded_file.size > 10 * 1024 * 1024:
        st.error("📄 File too large! Please upload a PDF smaller than 10MB.")
        return False
    
    # Check file type
    if not uploaded_file.name.lower().endswith('.pdf'):
        st.error("📄 Please upload a PDF file only.")
        return False
        
    return True

def sanitize_input(text: str) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Limit length
    if len(text) > 1000:
        text = text[:1000] + "..."
        st.warning("⚠️ Question truncated to 1000 characters.")
    
    return text

@st.cache_data(show_spinner=False)
def is_smalltalk(text: str) -> bool:
    """Check if text is smalltalk with caching"""
    if not text:
        return False
        
    text_lower = text.strip().lower()
    keywords = [
        "hi", "hii", "hiii", "hello", "hey", 
        "good morning", "good evening", "good afternoon",
        "thanks", "thank you", "bye", "goodbye"
    ]
    
    return any(keyword in text_lower for keyword in keywords)

def get_smalltalk_response(text: str) -> Optional[str]:
    """Generate smalltalk response"""
    if not text:
        return None
        
    text_lower = text.strip().lower()
    
    if any(k in text_lower for k in ["hi", "hii", "hiii", "hello", "hey"]):
        return "Hi there! 👋 I'm your Exam Assistant. Upload your syllabus PDF and ask me any questions!"
    
    if "exam" in text_lower and any(k in text_lower for k in ["tomorrow", "today", "help me"]):
        return "Let's get you ready! 📚 Upload your syllabus PDF and I'll help you with quick definitions (1-2 marks) and detailed explanations (10-12 marks). What topic shall we start with?"
    
    if any(k in text_lower for k in ["thanks", "thank you"]):
        return "You're welcome! 😊 Need help with more questions? I'm here to help you ace your exam!"
    
    if any(k in text_lower for k in ["bye", "goodbye"]):
        return "Good luck with your studies! 🍀 Come back anytime you need help!"
    
    return None