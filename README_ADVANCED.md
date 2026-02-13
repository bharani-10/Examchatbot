# 🎓 Exam Assistant AI Pro - Advanced Version

An advanced AI-powered exam preparation assistant with quiz generation, analytics, bookmarks, and multi-document management.

## 🚀 New Advanced Features

### 1. **Multiple Modes**
- 💬 **Chat Mode** - Interactive Q&A with your syllabus
- 📝 **Quiz Mode** - AI-generated MCQ and short answer questions
- 📊 **Analytics** - Track your study progress and performance
- 🔖 **Bookmarks** - Save important answers for quick review
- 📚 **Documents** - Manage multiple PDF documents

### 2. **Quiz Generation**
- Generate multiple-choice questions automatically
- Adjustable difficulty levels (Easy, Medium, Hard)
- Short answer questions with expected answers
- Instant feedback and explanations
- Score tracking and performance analytics

### 3. **Smart Suggestions**
- AI-powered question recommendations
- Topic-based suggestions from your syllabus
- Related questions for deeper understanding
- One-click question insertion

### 4. **Study Analytics**
- Track total questions asked
- Monitor daily study activity
- View quiz performance trends
- Topic coverage analysis
- Session history and time tracking

### 5. **Bookmark System**
- Star important answers during chat
- Organize saved Q&A pairs
- Quick access to bookmarked content
- Export bookmarks separately

### 6. **Document Management**
- Upload multiple PDF documents
- View document metadata (pages, size, upload date)
- Track questions asked per document
- Delete or manage documents easily

### 7. **Export Capabilities**
- Export chat history to TXT
- Export to Markdown format
- Download bookmarks separately
- Include timestamps and metadata

### 8. **Enhanced UI/UX**
- Smooth animations and transitions
- Animated gradient backgrounds
- Hover effects on all interactive elements
- Responsive design for all screen sizes
- Modern glassmorphism design

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
Create a `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key from: https://console.groq.com/

4. **Run the advanced version**
```bash
streamlit run app_advanced.py
```

## 🎯 How to Use

### Chat Mode
1. Upload your syllabus PDF
2. Ask questions naturally
3. Get mark-based responses (1, 2, 5, 10, 12 marks)
4. Star important answers to bookmark them
5. Use suggested questions for quick practice

### Quiz Mode
1. Select number of questions (3-10)
2. Click "Generate Quiz"
3. Answer multiple-choice questions
4. Get instant feedback
5. View your score and explanations

### Analytics Dashboard
- View total questions asked
- Check documents uploaded
- Monitor bookmarked answers
- Track daily activity
- Analyze quiz performance

### Bookmarks
- Access all starred answers
- Review important Q&A pairs
- Remove bookmarks you no longer need
- Export bookmarks for offline study

### Document Manager
- View all uploaded documents
- See document details (pages, size, date)
- Track usage per document
- Delete documents when done

## 🎨 Features Comparison

| Feature | Basic Version | Advanced Version |
|---------|--------------|------------------|
| Chat with AI | ✅ | ✅ |
| PDF Upload | ✅ | ✅ |
| Mark-based Responses | ✅ | ✅ |
| Quiz Generation | ❌ | ✅ |
| Analytics Dashboard | ❌ | ✅ |
| Bookmarks | ❌ | ✅ |
| Multi-document | ❌ | ✅ |
| Export Chat | ❌ | ✅ |
| Smart Suggestions | ❌ | ✅ |
| Study Tracking | ❌ | ✅ |

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **LLM**: Groq (Llama 3.1)
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Vector Store**: FAISS
- **PDF Processing**: PyPDF2
- **Framework**: LangChain

## 📊 Advanced Configuration

### Customize Quiz Settings
Edit `advanced_features.py`:
```python
# Adjust difficulty levels
difficulty_prompts = {
    "easy": "basic concepts",
    "medium": "application questions",
    "hard": "critical thinking"
}
```

### Modify Analytics Tracking
Edit `advanced_features.py`:
```python
# Add custom metrics
def log_custom_metric(self, metric_name, value):
    self.data[metric_name] = value
    self.save_data()
```

## 🎓 Study Tips

1. **Use Quiz Mode regularly** - Test yourself with AI-generated questions
2. **Bookmark key answers** - Save important explanations for quick review
3. **Check Analytics** - Monitor your progress and identify weak areas
4. **Try Suggestions** - Use AI-recommended questions for comprehensive coverage
5. **Export your notes** - Download chat history for offline study

## 🔧 Troubleshooting

### Quiz not generating?
- Ensure you've uploaded a syllabus PDF
- Check your internet connection
- Verify Groq API key is valid

### Bookmarks not saving?
- Check file permissions in the project directory
- Ensure sufficient disk space

### Analytics not updating?
- Restart the application
- Check `study_analytics.json` file exists

## 🚀 Future Enhancements

- [ ] Voice input for questions
- [ ] Multi-language support
- [ ] Flashcard generation
- [ ] Spaced repetition system
- [ ] Collaborative study rooms
- [ ] Mobile app version
- [ ] Integration with calendar
- [ ] Custom quiz templates

## 📝 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check the documentation
- Review troubleshooting guide

---

**Happy Studying! 🎓✨**

Made with ❤️ for students preparing for exams
