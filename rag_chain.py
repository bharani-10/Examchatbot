import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def get_groq_api_key() -> str:
    """Read GROQ API key from Streamlit secrets or environment."""
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        key = os.getenv("GROQ_API_KEY", "")
        if not key:
            st.error("🔑 GROQ_API_KEY not found in secrets or environment.")
            st.stop()
        return key


@st.cache_resource(show_spinner=False)
def get_llm():
    """Cached LLM instance."""
    return ChatGroq(
        groq_api_key=get_groq_api_key(),
        model_name="llama-3.1-8b-instant",
        temperature=0.2,
        max_retries=3,
    )


def get_rag_chain(vectorstore):
    """Creates and returns a RAG chain using the vectorstore."""
    try:
        llm       = get_llm()
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        template = """You are an expert exam assistant. Use the following context to answer accurately.

Context: {context}

Question: {question}

Instructions:
- Provide accurate, well-structured answers
- For 1-2 marks: concise, direct answers
- For 10-12 marks: detailed, structured explanations with headings
- If information is not in the context, say so clearly

Answer:"""

        prompt = ChatPromptTemplate.from_template(template)

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
