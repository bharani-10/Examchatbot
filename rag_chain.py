import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def get_groq_api_key():
    """Get GROQ API key from Streamlit secrets or environment"""
    try:
        return st.secrets["GROQ_API_KEY"]
    except (KeyError, FileNotFoundError):
        import os
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            st.error("🔑 GROQ API Key not found!")
            st.stop()
        return api_key

@st.cache_resource(show_spinner=False)
def get_llm():
    """Get LLM with caching"""
    api_key = get_groq_api_key()
    return ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.1-8b-instant",
        temperature=0.2,
        max_retries=3
    )

def get_rag_chain(vectorstore):
    """Creates and returns a Retrieval-Augmented Generation (RAG) chain"""
    try:
        # Initialize Groq LLM
        llm = get_llm()
        
        # Create retriever
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Create prompt template
        template = """You are an expert exam assistant. Use the following context to answer the question accurately and concisely.
        
        Context: {context}
        
        Question: {question}
        
        Instructions:
        - Provide accurate, well-structured answers
        - If the question mentions marks (1, 2, 10, 12), format your response accordingly
        - For 1-2 marks: Give concise, direct answers
        - For 10-12 marks: Provide detailed, structured explanations
        - If information is not in the context, say so clearly
        
        Answer:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # Create chain
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return chain
        
    except Exception as e:
        st.error(f"Error creating RAG chain: {str(e)}")
        return None

    # Custom prompt template
    template = """You are an intelligent Exam Assistant Chatbot.
Answer strictly based on the uploaded PDF syllabus context below. If the answer is not in the context, say: "I don't know based on the given syllabus."

Rules:
- Answer any question naturally and clearly using the syllabus context.
- If marks are specified (1, 2, 5, 10, 12 etc.), structure the answer for exam format:
  • 1 Mark → very short definition (2–3 lines)
  • 2 Marks → short explanation (4–6 lines)
  • 5 Marks → medium explanation with key points
  • 10/12 Marks → detailed explanation with headings, points, examples
- If marks are not mentioned, give a clear detailed explanation (exam-oriented).
- Do not ask the user to specify marks; infer from the question if present.
- Keep formatting clean and structured.

Context:
{context}

Question:
{question}

Answer:"""

    prompt = ChatPromptTemplate.from_template(template)

    # Format documents function
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Create RAG chain
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
