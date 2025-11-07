'''defines the core vector store and search functionality for your (RAG) workflow.'''
import os
import faiss # Facebook AI Similarity Search
import numpy as np
import pickle
from typing import List, Any
from sentence_transformers import SentenceTransformer
from src.embedding import EmbeddingPipeline

class FaissVectorStore:
    '''This class is the engine for efficient semantic search over your document collection 
    using dense vector embeddings and the FAISS library.'''
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", chunk_size: int = 1000, chunk_overlap: int = 200):
        '''Initializes paths, loads the embedding model, prepares data structures for the FAISS index and metadata.'''
        self.persist_dir = persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.index = None
        self.metadata = []
        self.embedding_model = embedding_model
        self.model = SentenceTransformer(embedding_model)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        print(f"[INFO] Loaded embedding model: {embedding_model}")

    def build_from_documents(self, documents: List[Any]):
        '''Converts documents into embeddings, builds the FAISS index, saves everything for later.
        Splits docs into chunks, generates embeddings, stores both vectors and (associated) metadata.'''

        print(f"[INFO] Building vector store from {len(documents)} raw documents...")
        emb_pipe = EmbeddingPipeline(model_name=self.embedding_model, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        chunks = emb_pipe.chunk_documents(documents)
        embeddings = emb_pipe.embed_chunks(chunks)
        metadatas = [{"text": chunk.page_content} for chunk in chunks]
        self.add_embeddings(np.array(embeddings).astype('float32'), metadatas)
        self.save()
        print(f"[INFO] Vector store built and saved to {self.persist_dir}")

    def add_embeddings(self, embeddings: np.ndarray, metadatas: List[Any] = None):
        '''Adds (or creates then adds) new vectors and their metadata to the FAISS index structure.'''
        dim = embeddings.shape[1]
        if self.index is None:
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        if metadatas:
            self.metadata.extend(metadatas)
        print(f"[INFO] Added {embeddings.shape[0]} vectors to Faiss index.")

    def save(self):
        '''Persists the index and metadata to files for later reuse—fast startup, avoids recomputation.'''
        faiss_path = os.path.join(self.persist_dir, "faiss.index")#All the document vectors, optimized for rapid search.
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")#Human-readable context ("text") tied to each vector for displaying or further LLM processing.
        faiss.write_index(self.index, faiss_path)
        with open(meta_path, "wb") as f:
            pickle.dump(self.metadata, f)
        print(f"[INFO] Saved Faiss index and metadata to {self.persist_dir}")

    def load(self):
        '''Loads the index and metadata from persistent files to RAM—makes your vector database immediately usable.'''
        faiss_path = os.path.join(self.persist_dir, "faiss.index") #stores All document chunk embedding vectors
        meta_path = os.path.join(self.persist_dir, "metadata.pkl")# his file (serialized with Python pickle) stores a list of metadata dictionaries.
        self.index = faiss.read_index(faiss_path)
        with open(meta_path, "rb") as f:
            self.metadata = pickle.load(f)
        print(f"[INFO] Loaded Faiss index and metadata from {self.persist_dir}")

    def search(self, query_embedding: np.ndarray, top_k: int = 5):
        ''' Finds the top_k most similar embeddings in the index to the given query embedding.
        Returns a list with the result index, distance (similarity score), and its metadata (usually text content).'''
        D, I = self.index.search(query_embedding, top_k)
        results = []
        for idx, dist in zip(I[0], D[0]):
            meta = self.metadata[idx] if idx < len(self.metadata) else None
            results.append({"index": idx, "distance": dist, "metadata": meta})
        return results

    def query(self, query_text: str, top_k: int = 5):
        ''' Main semantic search interface. Accepts a natural language query, encodes it, runs vector search,
         returns the best matched text blocks (with metadata).'''

        print(f"[INFO] Querying vector store for: '{query_text}'")
        #query (query_text) is passed to the same embedding model (from sentence_transformers) 
        # as stored documents.This converts it into a dense vector—now it can be compared mathematically.
        query_emb = self.model.encode([query_text]).astype('float32')
        return self.search(query_emb, top_k=top_k)

if __name__ == "__main__":
    from src.data_loader import load_all_documents, load_github_commits_json, load_github_issues_json
    org_docs = load_all_documents("data")
    commit_docs = load_github_commits_json("data/json/git_commits.json")
    issue_docs = load_github_issues_json("data/json/git_issues.json")
    docs = org_docs + commit_docs + issue_docs
    store = FaissVectorStore("faiss_store")
    store.build_from_documents(docs)
    store.load()
    print(store.query("Who created this repository?", top_k=3))