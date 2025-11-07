'''This is the main application file for the RAG conversational assistant using Tkinter UI.'''
import tkinter as tk
from tkinter import scrolledtext
import threading
from datetime import datetime
import os
from dotenv import load_dotenv
from src.vector_db import FaissVectorStore
from langchain_groq import ChatGroq

load_dotenv()

class ChatUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MinervaAI : Conversational RAG Assistant for Organizational Knowledge")
        self.root.geometry("800x900")
        self.root.configure(bg='#e5ddd5')
        
        # Initialize RAG system
        self.rag_search = None
        self.typing_indicator_id = None
        self.is_typing = False
        
        # icons using emoji or simple shapes
        self.bot_icon = "🤖"  # Robot emoji for bot
        self.user_icon = "👤"  # User emoji for user
        
        self.setup_rag_system()
        self.setup_ui()
        
    def setup_rag_system(self):
        """Initialize RAG system in a separate thread"""
        def init_rag():
            try:
                commit_file = "data/json/git_commits.json"
                issue_file = "data/json/ues.json"

                if not (os.path.exists(commit_file) and os.path.exists(issue_file)):
                    # Silent download - no message to user
                    import src.download_github_data as download_github_data
                    download_github_data.fetch_commits()
                    download_github_data.fetch_issues()

                self.rag_search = RAGSearch()
                self.add_message("system", "Hi there! I'm your RAG Assistant, ready to help you navigate your organization's knowledge. What would you like to find out?")
            except Exception as e:
                # Silent error handling - no message to user
                print(f"Error initializing system: {str(e)}")
        
        threading.Thread(target=init_rag, daemon=True).start()
    
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#634761", height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Bot icon and title in header
        icon_label = tk.Label(header_frame, text="🤖", font=('Arial', 24), bg='#634761', fg='white')
        icon_label.pack(side='left', padx=15, pady=10)
        
        # Main title
        main_title = tk.Label(header_frame, text="MinervaAI", font=('Arial', 20, 'bold'), bg='#634761', fg='white')
        main_title.pack(side='top', anchor='w', padx=5, pady=(8, 0))

        # Subtitle/description
        subtitle = tk.Label(header_frame,
            text="Conversational RAG Assistant for Organizational Knowledge Base",
            font=('Arial', 12, 'italic'),
            bg='#634761', fg='#eed2ff'
        )
        subtitle.pack(side='top', anchor='w', padx=5, pady=(0, 10))
        
        # Chat area - full width without border
        self.chat_area = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD,
            font=('Segoe UI', 12),
            bg='#f8f3fc',
            padx=20,
            pady=15,
            state='disabled',
            borderwidth=0,
            highlightthickness=0
        )
        self.chat_area.pack(fill='both', expand=True, padx=0, pady=0)
        
        # Input area
        input_frame = tk.Frame(self.root, bg='#f0f0f0', height=80)
        input_frame.pack(fill='x', padx=20, pady=15)
        input_frame.pack_propagate(False)
        
        self.input_entry = tk.Entry(
            input_frame, 
            font=('Segoe UI', 14),
            bg='white',
            relief='flat',
            borderwidth=1,
            width=50
        )
        self.input_entry.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        self.input_entry.bind('<Return>', self.send_message)
        self.input_entry.focus()
        
        # Send button with better styling
        send_btn = tk.Button(
            input_frame,
            text="➤",
            font=('Arial', 16, 'bold'),
            bg="#7d5c90", 
            fg='white',
            relief='flat',
            width=3,
            height=1,
            command=self.send_message
        )
        send_btn.pack(side='right', padx=10, pady=10)
        
        # No initial message - chat starts empty
        # The welcome message will appear when RAG system is ready
        
    def add_message(self, sender, message):
        """Add a message to the chat area"""
        self.chat_area.config(state='normal')
        
        timestamp = datetime.now().strftime("%H:%M")
        
        if sender == "user":
            # User message (right side, green background)
            self.chat_area.insert('end', f'\n', 'right_space')
            self.chat_area.insert('end', f' {self.user_icon} ', 'user_icon')
            self.chat_area.insert('end', f' {message}\n', 'user_msg')
            self.chat_area.insert('end', f' {timestamp}\n', 'timestamp_right')
            
        elif sender == "system" or sender == "bot":
            # System/Bot message (left side, white background)
            self.chat_area.insert('end', f'\n', 'left_space')
            self.chat_area.insert('end', f' {self.bot_icon} ', 'bot_icon')
            self.chat_area.insert('end', f' {message}\n', 'system_msg')
            self.chat_area.insert('end', f' {timestamp}\n', 'timestamp_left')
        
        # Configure tags for styling with fancy colors
        self.chat_area.tag_configure('user_msg', 
                                   background="#eedafb",
                                   foreground="#4b3b9d",
                                   relief='raised',
                                   wrap='word',
                                   justify='right',
                                   font=('Segoe UI', 12))
        
        self.chat_area.tag_configure('system_msg', 
                                   background="#f8f3fc",
                                   foreground='#2c2c2c',  
                                   relief='raised',
                                   wrap='word',
                                   justify='left',
                                   font=('Segoe UI', 12))
        
        self.chat_area.tag_configure('user_icon', 
                                   font=('Arial', 12),
                                   foreground='#4b3b9d',
                                   justify='right')
        
        self.chat_area.tag_configure('bot_icon', 
                                   font=('Arial', 12),
                                   foreground="#131212",
                                   justify='left')
        
        self.chat_area.tag_configure('timestamp_right', 
                                   font=('Segoe UI', 9),
                                   foreground="#4b3b9d",
                                   justify='right')
        
        self.chat_area.tag_configure('timestamp_left', 
                                   font=('Segoe UI', 9),
                                   foreground='#4b3b9d',
                                   justify='left')
        
        self.chat_area.tag_configure('right_space', justify='right')
        self.chat_area.tag_configure('left_space', justify='left')
        
        self.chat_area.config(state='disabled')
        self.chat_area.see('end')
    
    def send_message(self, event=None):
        """Handle sending messages"""
        message = self.input_entry.get().strip()
        if not message:
            return
        
        if message.lower() in ['quit', 'exit', 'bye']:
            self.add_message("system", "Goodbye! Feel free to come back if you have more questions.")
            self.root.after(2000, self.root.quit)
            return
        
        # Add user message to chat
        self.add_message("user", message)
        self.input_entry.delete(0, 'end')
        
        # Process message in separate thread
        threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
    
    def process_message(self, message):
        """Process the user message using RAG system"""
        if not self.rag_search:
            self.add_message("system", "System still initializing, please wait...")
            return
        
        # Show typing indicator
        self.show_typing_indicator()
        self.is_typing = True
        
        try:
            # Process the query
            response = self.rag_search.search_and_summarize(message, top_k=3)
            
            # Hide typing indicator and show response
            self.hide_typing_indicator()
            self.add_message("bot", response)
            
        except Exception as e:
            self.hide_typing_indicator()
            # Silent error handling for processing messages t3oo
            print(f"Error processing message: {str(e)}")
    
    def show_typing_indicator(self):
        """Show typing indicator"""
        self.chat_area.config(state='normal')
        
        # Store the position where we'll insert the typing indicator
        self.typing_indicator_id = self.chat_area.index('end')
        
        # Insert typing indicator
        self.chat_area.insert('end', f'\n', 'left_space')
        self.chat_area.insert('end', f' {self.bot_icon} ', 'bot_icon')
        self.chat_area.insert('end', "Assistant is typing...\n", 'typing')
        
        # Configure typing style
        self.chat_area.tag_configure('typing', 
                                   font=('Segoe UI', 10),
                                   foreground='#667781',
                                   background='white',
                                   justify='left')
        
        self.chat_area.config(state='disabled')
        self.chat_area.see('end')
    
    def hide_typing_indicator(self):
        """Remove typing indicator"""
        if self.typing_indicator_id and self.is_typing:
            self.chat_area.config(state='normal')
            
            # Get the start of the typing indicator
            start_line = self.typing_indicator_id
            end_line = self.chat_area.index('end')
            
            # Delete from the typing indicator start to end
            self.chat_area.delete(start_line, end_line)
            
            self.chat_area.config(state='disabled')
            self.typing_indicator_id = None
            self.is_typing = False

class RAGSearch:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = "openai/gpt-oss-120b"):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")

        if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
            from src.data_loader import load_all_documents, load_github_commits_json, load_github_issues_json
            org_docs = load_all_documents("data")
            commit_docs = load_github_commits_json(commit_file)
            issue_docs = load_github_issues_json(issue_file)
            docs = org_docs + commit_docs + issue_docs
            self.vectorstore.build_from_documents(docs)
        else:
            self.vectorstore.load()
            
        groq_api_key = ""
        self.llm = ChatGroq(groq_api_key=groq_api_key, model_name=llm_model)
        print(f"[INFO] Groq LLM initialized: {llm_model}")

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        results = self.vectorstore.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        context = "\n\n".join(texts)
        if not context:
            return "No relevant documents found."
        prompt = f"""Summarize the following context for the query: '{query}'\n\nContext:\n{context}\n\nSummary:"""
        response = self.llm.invoke([prompt])
        return response.content

# Global variables for file paths
commit_file = "data/json/git_commits.json"
issue_file = "data/json/git_issues.json"

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatUI(root)
    root.mainloop()
