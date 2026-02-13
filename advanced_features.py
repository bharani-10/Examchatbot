"""
Advanced features for Exam Assistant AI Pro
"""
import json
import os
from datetime import datetime
from typing import List, Dict
import streamlit as st
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, MODEL_NAME


class QuizGenerator:
    """Generate and manage quiz questions"""
    
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=MODEL_NAME, temperature=0.7)
    
    def generate_mcq(self, num_questions: int = 5, difficulty: str = "medium") -> List[Dict]:
        """Generate multiple choice questions"""
        
        difficulty_prompts = {
            "easy": "basic concepts and definitions",
            "medium": "application and understanding",
            "hard": "analysis and critical thinking"
        }
        
        prompt = f"""Generate {num_questions} multiple-choice questions focusing on {difficulty_prompts.get(difficulty, 'medium')}.
        
Format each question EXACTLY as:
Q: [Clear question text]
A) [First option]
B) [Second option]
C) [Third option]
D) [Fourth option]
Correct: [A/B/C/D]
Explanation: [Brief explanation why this is correct]

---

Make questions exam-oriented and challenging."""
        
        try:
            response = self.llm.invoke(prompt)
            content = getattr(response, "content", str(response))
            return self._parse_questions(content)
        except Exception as e:
            st.error(f"Error generating quiz: {e}")
            return []
    
    def _parse_questions(self, content: str) -> List[Dict]:
        """Parse LLM response into structured questions"""
        questions = []
        current_q = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('Q:'):
                if current_q and 'question' in current_q:
                    questions.append(current_q)
                current_q = {'question': line[2:].strip(), 'options': {}}
            
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                option_key = line[0]
                option_text = line[2:].strip()
                current_q['options'][option_key] = option_text
            
            elif line.startswith('Correct:'):
                current_q['correct'] = line.split(':')[1].strip()[0]
            
            elif line.startswith('Explanation:'):
                current_q['explanation'] = line.split(':', 1)[1].strip()
        
        if current_q and 'question' in current_q:
            questions.append(current_q)
        
        return questions
    
    def generate_short_answer(self, num_questions: int = 3) -> List[Dict]:
        """Generate short answer questions"""
        prompt = f"""Generate {num_questions} short answer questions (2-5 marks each).
        
Format:
Q: [Question]
Expected Answer: [Key points that should be covered]
Marks: [2/3/5]

---

Focus on important concepts."""
        
        try:
            response = self.llm.invoke(prompt)
            content = getattr(response, "content", str(response))
            return self._parse_short_answer(content)
        except:
            return []
    
    def _parse_short_answer(self, content: str) -> List[Dict]:
        """Parse short answer questions"""
        questions = []
        current_q = {}
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('Q:'):
                if current_q:
                    questions.append(current_q)
                current_q = {'question': line[2:].strip(), 'type': 'short_answer'}
            
            elif line.startswith('Expected Answer:'):
                current_q['expected_answer'] = line.split(':', 1)[1].strip()
            
            elif line.startswith('Marks:'):
                current_q['marks'] = line.split(':')[1].strip()
        
        if current_q:
            questions.append(current_q)
        
        return questions


class StudyAnalytics:
    """Track and analyze study patterns"""
    
    def __init__(self):
        self.analytics_file = "study_analytics.json"
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load analytics data from file"""
        if os.path.exists(self.analytics_file):
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except:
                return self._default_data()
        return self._default_data()
    
    def _default_data(self) -> Dict:
        """Default analytics structure"""
        return {
            "sessions": [],
            "total_questions": 0,
            "total_time_minutes": 0,
            "topics_studied": [],
            "quiz_scores": [],
            "daily_activity": {}
        }
    
    def save_data(self):
        """Save analytics data to file"""
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            st.error(f"Error saving analytics: {e}")
    
    def log_question(self, question: str, topic: str = "General"):
        """Log a question asked"""
        self.data["total_questions"] += 1
        
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.data["daily_activity"]:
            self.data["daily_activity"][today] = 0
        self.data["daily_activity"][today] += 1
        
        if topic not in self.data["topics_studied"]:
            self.data["topics_studied"].append(topic)
        
        self.save_data()
    
    def log_quiz_score(self, score: int, total: int):
        """Log quiz performance"""
        percentage = (score / total) * 100 if total > 0 else 0
        self.data["quiz_scores"].append({
            "score": score,
            "total": total,
            "percentage": percentage,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        self.save_data()
    
    def get_statistics(self) -> Dict:
        """Get summary statistics"""
        quiz_scores = self.data.get("quiz_scores", [])
        avg_score = sum(q["percentage"] for q in quiz_scores) / len(quiz_scores) if quiz_scores else 0
        
        return {
            "total_questions": self.data["total_questions"],
            "topics_count": len(self.data["topics_studied"]),
            "quiz_count": len(quiz_scores),
            "average_score": round(avg_score, 1),
            "daily_activity": self.data["daily_activity"]
        }


class SmartSuggestions:
    """Generate intelligent question suggestions"""
    
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = ChatGroq(groq_api_key=GROQ_API_KEY, model_name=MODEL_NAME, temperature=0.6)
    
    def get_topic_suggestions(self, num_suggestions: int = 5) -> List[str]:
        """Get suggested questions based on syllabus topics"""
        prompt = f"""Based on the syllabus content, suggest {num_suggestions} important exam questions.
        
Focus on:
- Key concepts and definitions
- Important theories and principles
- Common exam patterns
- Application-based questions

Format as a numbered list:
1. [Question]
2. [Question]
etc.

Keep questions clear and exam-oriented."""
        
        try:
            response = self.llm.invoke(prompt)
            content = getattr(response, "content", str(response))
            
            questions = []
            for line in content.split('\n'):
                line = line.strip()
                if line and line[0].isdigit() and '.' in line:
                    question = line.split('.', 1)[1].strip()
                    questions.append(question)
            
            return questions[:num_suggestions]
        except:
            return []
    
    def get_related_questions(self, current_question: str, num_related: int = 3) -> List[str]:
        """Get questions related to current topic"""
        prompt = f"""Given this question: "{current_question}"
        
Suggest {num_related} related questions that explore:
- Different aspects of the same topic
- Prerequisites or foundational concepts
- Advanced applications

Format as:
1. [Question]
2. [Question]
etc."""
        
        try:
            response = self.llm.invoke(prompt)
            content = getattr(response, "content", str(response))
            
            questions = []
            for line in content.split('\n'):
                line = line.strip()
                if line and line[0].isdigit():
                    question = line.split('.', 1)[1].strip() if '.' in line else line
                    questions.append(question)
            
            return questions[:num_related]
        except:
            return []


class DocumentManager:
    """Manage multiple documents and their metadata"""
    
    def __init__(self):
        self.docs_file = "documents_metadata.json"
        self.documents = self._load_documents()
    
    def _load_documents(self) -> List[Dict]:
        """Load document metadata"""
        if os.path.exists(self.docs_file):
            try:
                with open(self.docs_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_documents(self):
        """Save document metadata"""
        try:
            with open(self.docs_file, 'w') as f:
                json.dump(self.documents, f, indent=2)
        except Exception as e:
            st.error(f"Error saving documents: {e}")
    
    def add_document(self, name: str, pages: int, size: int, content_preview: str = ""):
        """Add a new document"""
        doc = {
            "id": len(self.documents) + 1,
            "name": name,
            "pages": pages,
            "size": size,
            "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content_preview": content_preview[:200],
            "questions_asked": 0
        }
        self.documents.append(doc)
        self.save_documents()
        return doc
    
    def remove_document(self, doc_id: int):
        """Remove a document"""
        self.documents = [d for d in self.documents if d.get("id") != doc_id]
        self.save_documents()
    
    def get_document(self, doc_id: int) -> Dict:
        """Get document by ID"""
        for doc in self.documents:
            if doc.get("id") == doc_id:
                return doc
        return None
    
    def increment_questions(self, doc_id: int):
        """Increment question count for a document"""
        for doc in self.documents:
            if doc.get("id") == doc_id:
                doc["questions_asked"] = doc.get("questions_asked", 0) + 1
                self.save_documents()
                break


def export_to_markdown(messages: List[Dict], bookmarks: List[Dict]) -> str:
    """Export chat and bookmarks to markdown format"""
    md_content = f"""# Exam Assistant AI - Study Notes
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## Chat History

"""
    
    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"]
        md_content += f"### {role}\n\n{content}\n\n---\n\n"
    
    if bookmarks:
        md_content += "\n## 📌 Bookmarked Q&A\n\n"
        for idx, bookmark in enumerate(bookmarks, 1):
            md_content += f"### Bookmark {idx}\n\n"
            md_content += f"**Question:** {bookmark['question']}\n\n"
            md_content += f"**Answer:** {bookmark['answer']}\n\n---\n\n"
    
    return md_content
