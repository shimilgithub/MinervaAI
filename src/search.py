import os
from dotenv import load_dotenv
from src.vector_db import FaissVectorStore
from langchain_groq import ChatGroq

load_dotenv()

class RAGSearch:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = "openai/gpt-oss-120b"):
        '''Initializes the semantic search vector database.
        * If persistent files don’t exist, rebuilds the index from documents.
        * If already exists, loads the index for immediate use.
        * Initializes the Groq LLM client for text generation.'''
        #otheroption for llm_model : "llama-3.3-70b-versatile"
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
       
        # Load or build vectorstore
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            from src.data_loader import load_all_documents, load_github_commits_json, load_github_issues_json
            org_docs = load_all_documents("data")
            commit_docs = load_github_commits_json("data/json/git_commits.json")
            issue_docs = load_github_issues_json("data/json/git_issues.json")
            docs = org_docs + commit_docs + issue_docs
            
            self.vectorstore.build_from_documents(docs)
        else:
            self.vectorstore.load()
        groq_api_key = ""
        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name=llm_model)
        print(f"[INFO] Groq LLM initialized: {llm_model}")

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        '''Performs semantic search for the user’s query, finds best-matching document chunks.
        * Extracts the text content from each chunk’s metadata and concatenates it as the summary context.
        * Crafts a prompt instructing the LLM to summarize the retrieved context.
        * Sends the prompt to Groq’s LLM and returns the summary.'''
        results = self.vectorstore.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        context = "\n\n".join(texts)
        if not context:
            return "No relevant documents found."
        #asking the llm to summarize the context
        prompt = f"""Summarize the following context for the query: '{query}'\n\nContext:\n{context}\n\nSummary:"""
        response = self.llm.invoke([prompt])
        return response.content

if __name__ == "__main__":
    rag_search = RAGSearch()
    query = "Who created this repository?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)
