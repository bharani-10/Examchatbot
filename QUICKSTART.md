# 🚀 Quick Start Guide

## Step 1: Setup (First Time Only)

1. **Get your Groq API Key**
   - Visit: https://console.groq.com/
   - Sign up for free
   - Copy your API key

2. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Paste your API key in the `.env` file:
   ```
   GROQ_API_KEY=your_actual_key_here
   ```

## Step 2: Run the App

### Option A: Using the Batch File (Easiest)
Just double-click `run.bat` - it handles everything automatically!

### Option B: Manual Setup
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Step 3: Use the App

1. **Upload PDF**: Click sidebar → Browse files → Select your study material
2. **Wait**: The app will process your PDF (takes 10-30 seconds)
3. **Ask Questions**: Type in the chat box at the bottom
4. **Get Answers**: Receive AI-powered responses instantly!

## 💡 Pro Tips

- **Specify marks** for better answers: "Explain X for 2 marks"
- **Be specific** in your questions
- **Use clear language** from your syllabus
- **Clear chat** using the sidebar button when starting a new topic

## 🎯 Example Questions

```
What is an algorithm? 1 mark
Explain binary search for 2 marks
Describe database normalization for 12 marks
What are the OSI model layers? 10 marks
```

## ⚡ Troubleshooting

**App won't start?**
- Check if Python is installed: `python --version`
- Make sure .env file exists with valid API key

**No answers?**
- Ensure PDF uploaded successfully
- Check if question relates to PDF content
- Try rephrasing your question

**Slow responses?**
- First query is slower (loading models)
- Subsequent queries are faster
- Large PDFs take longer to process

---

Need help? Check README.md for detailed documentation!
