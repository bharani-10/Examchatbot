# 🎓 Exam Assistant AI

A beautiful, intelligent exam preparation chatbot powered by RAG (Retrieval-Augmented Generation) technology.

## ✨ Features

- 📚 **PDF Upload**: Upload your syllabus or study notes
- 🤖 **AI-Powered Answers**: Get intelligent, context-aware answers
- 🎯 **Mark-Based Responses**: Specify marks (1, 2, 10, 12) for appropriate answer length
- 💬 **Chat Interface**: Modern, ChatGPT-style conversation interface
- 🎨 **Beautiful UI**: Gradient design with smooth animations
- 📊 **Session Stats**: Track your study progress

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free API key from: https://console.groq.com/

### 3. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 How to Use

1. **Upload PDF**: Click "Browse files" in the sidebar and upload your study material
2. **Ask Questions**: Type your exam question in the chat input
3. **Specify Marks**: Include marks in your question for appropriate detail:
   - "What is bit depth? 1 mark"
   - "Explain data compression for 2 marks"
   - "Describe the OSI model for 12 marks"

## 🎨 UI Features

- **Gradient Background**: Beautiful purple gradient design
- **Smooth Animations**: Hover effects and transitions
- **Responsive Layout**: Works on all screen sizes
- **Chat Bubbles**: Distinct user and bot message styling
- **Loading Indicators**: Visual feedback during processing
- **Session Management**: Clear chat and track statistics

## 🛠️ Technology Stack

- **Streamlit**: Web interface
- **LangChain**: RAG framework
- **Groq**: Fast LLM inference (Llama 3.1)
- **FAISS**: Vector similarity search
- **Sentence Transformers**: Text embeddings
- **PyPDF2**: PDF processing

## 📝 Example Questions

- What is an algorithm? Give 1 mark answer
- Explain binary search for 2 marks
- Describe database normalization in detail for 12 marks
- What are the layers of OSI model? 10 marks

## 🔧 Configuration

Edit `config.py` to customize:
- Model name
- Embedding model
- Vectorstore directory
- Other settings

## 🧷Test the app here
   https://examchatbot-01.streamlit.app/

## 🤝 Support

For issues or questions, please check the documentation or create an issue.

---

Made with ❤️ for students preparing for exams
