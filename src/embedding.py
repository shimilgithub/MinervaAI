
'''Performs text chunking and embedding generation using transformer models.'''
from typing import List, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer 
import numpy as np
from src.data_loader import load_all_documents, load_github_commits_json, load_github_issues_json

class EmbeddingPipeline:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", chunk_size: int = 1000, chunk_overlap: int = 200):
        '''Initializes the embedding pipeline.
        * model_name: Chooses which transformer model to use (default: MiniLM).
        * chunk_size, chunk_overlap: Parameters that set how documents are divided for embeddings.
        * self.model: Loads the embedding model into memory for future use.
        * Prints which model is loaded for debugging.'''

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.model = SentenceTransformer(model_name)
        print(f"[INFO] Loaded embedding model: {model_name}")

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        '''Splits input documents into manageable, possibly overlapping chunks.
        * Uses RecursiveCharacterTextSplitter to divide documents into blocks not exceeding chunk_size,
             with chunk_overlap to maintain context between chunks.
        * Separators used to split content on paragraphs, newlines, spaces or any text.
        * Returns a list of chunked document objects.'''
    
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(documents)
        print(f"[INFO] Split {len(documents)} documents into {len(chunks)} chunks.")
        return chunks

    def embed_chunks(self, chunks: List[Any]) -> np.ndarray:
        '''Generates embeddings from input text chunks.
        * Extracts only the text content from each chunk.
        * Encodes all chunk texts in batches using the loaded model, producing a matrix of high-dimensional vectors.
        * Shows progress bar and print statements for status.
        * Returns the numpy array of embeddings (each row corresponds to one text chunk).'''

        texts = [chunk.page_content for chunk in chunks]
        print(f"[INFO] Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(texts, show_progress_bar=True)
        print(f"[INFO] Embeddings shape: {embeddings.shape}")
        return embeddings

if __name__ == "__main__":
    org_docs = load_all_documents("data")
    commit_docs = load_github_commits_json("data/json/git_commits.json")
    issue_docs = load_github_issues_json("data/json/git_issues.json")
    docs = org_docs + commit_docs + issue_docs
    emb_pipe = EmbeddingPipeline()
    chunks = emb_pipe.chunk_documents(docs)
    embeddings = emb_pipe.embed_chunks(chunks)
    print("[INFO] Example embedding:", embeddings[0] if len(embeddings) > 0 else None)
