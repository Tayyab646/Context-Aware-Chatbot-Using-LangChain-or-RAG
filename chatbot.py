# 1. INSTALL NECESSARY PACKAGES
!pip install -q -U langchain-groq langchain-community langchain-huggingface langchain-text-splitters faiss-cpu beautifulsoup4 gradio

import os
import gradio as gr
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

# 2. CONFIGURATION
# ---------------------------------------------------------
os.environ["GROQ_API_KEY"] = "Your-API-Key" # <--- PASTE YOUR KEY HERE
# ---------------------------------------------------------

# 3. SETUP KNOWLEDGE BASE (Using Local Embeddings for stability)
print("Step 1: Fetching Wikipedia Data...")
loader = WebBaseLoader("https://en.wikipedia.org/wiki/Artificial_intelligence")
docs = loader.load()

print("Step 2: Splitting text...")
text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=50)
chunks = text_splitter.split_documents(docs)

print("Step 3: Creating Local Search Index...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 4. UPDATED GROQ LOGIC (Using the new Llama 3.3 model)
# We changed the model_name to llama-3.3-70b-versatile
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.1)

def chatbot_response(message, history):
    try:
        # Search the local Wikipedia index
        relevant_docs = retriever.invoke(message)
        context = "\n\n".join([d.page_content for d in relevant_docs])

        prompt = f"""You are a helpful assistant. Use the following context to answer the question.

        CONTEXT:
        {context}

        QUESTION:
        {message}

        ANSWER:"""

        response = llm.invoke(prompt)
        return response.content
    except Exception as e:
        if "decommissioned" in str(e).lower():
            return "The model was recently updated by Groq. Please use 'llama-3.3-70b-versatile'."
        return f"Error: {str(e)}"

# 5. GRADIO UI
print("Step 4: Launching Interface...")
demo = gr.ChatInterface(
    fn=chatbot_response,
    title="RAG + LangChain Context Aware Chatbot",
    description="I am powered by Groq's newest Llama 3.3 model and Wikipedia!"
)

demo.launch(share=True)
