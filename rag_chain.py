import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# API key will be checked when creating the chain


def get_rag_chain(vectorstore):
    """
    Creates and returns a Retrieval-Augmented Generation (RAG) chain
    """

    # Initialize Groq LLM
    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.2
    )

    # Create retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

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
