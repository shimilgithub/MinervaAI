'''loads documents from various file types in a specified directory into LangChain documents.'''
import json
from pathlib import Path
from typing import List, Any, Callable
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, CSVLoader, Docx2txtLoader
)
from langchain_core.documents import Document
from langchain_community.document_loaders.excel import UnstructuredExcelLoader


def load_github_commits_json(json_path):
    '''function to load GitHub commits from a JSON file and convert them into LangChain documents.'''
    with open(json_path, "r", encoding="utf-8") as f:
        commits = json.load(f)
    documents = []
    for commit in commits:
        sha = commit.get("sha", "")
        msg = commit.get("commit", {}).get("message", "")
        author = commit.get("commit", {}).get("author", {}).get("name", "")
        date = commit.get("commit", {}).get("author", {}).get("date", "")
        doc = Document(
            page_content=msg,
            metadata={"sha": sha, "author": author, "date": date}
        )
        documents.append(doc)
    return documents


def load_github_issues_json(json_path):
    '''function to load GitHub issues from a JSON file and convert them into LangChain documents.'''
    with open(json_path, "r", encoding="utf-8") as f:
        issues = json.load(f)
    documents = []
    for issue in issues:
        title = issue.get("title", "")
        body = issue.get("body", "")
        num = issue.get("number", "")
        author = issue.get("user", {}).get("login", "")
        date = issue.get("created_at", "")
        doc_text = f"{title}\n\n{body}"
        doc = Document(
            page_content=doc_text,
            metadata={
                "issue_number": num,
                "author": author,
                "date": date
            }
        )
        documents.append(doc)
    return documents


def load_all_documents(data_dir: str) -> List[Any]:
    """
    Load all supported files from a directory (recursively) into LangChain documents.
    Supported: PDF, TXT, CSV, Excel(XLSX), DOCX, JSON
    """
    data_path = Path(data_dir).resolve()
    print(f"[DEBUG] Scanning: {data_path}")

    # Mapping of file extensions to loaders
    loaders: dict[str, Callable[[str], Any]] = {
        ".pdf": PyPDFLoader,
        ".txt": lambda fp: TextLoader(fp, encoding="utf-8"),
        ".csv": CSVLoader,
        ".xlsx": UnstructuredExcelLoader,
        ".docx": Docx2txtLoader,
    }

    documents = []

    # Search for all supported files
    supported_extensions = tuple(loaders.keys())
    files = list(data_path.rglob("*"))
    files = [f for f in files if f.suffix.lower() in supported_extensions]

    print(f"[DEBUG] Found {len(files)} files: {[str(f) for f in files]}")

    for file_path in files:
        ext = file_path.suffix.lower()
        loader_class = loaders[ext]

        print(f"[DEBUG] Loading {ext.upper()} File: {file_path}")

        try:
            loader = loader_class(str(file_path))
            loaded_docs = loader.load()
            documents.extend(loaded_docs)

            print(f"[DEBUG] Loaded {len(loaded_docs)} documents from: {file_path}")

        except Exception as e:
            print(f"[ERROR] Could not load {file_path}: {e}")

    print(f"[DEBUG] Total documents loaded: {len(documents)}")

    return documents


if __name__ == "__main__":
    org_docs = load_all_documents("data")
    commit_docs = load_github_commits_json("data/json/git_commits.json")
    issue_docs = load_github_issues_json("data/json/git_issues.json")
    docs = org_docs + commit_docs + issue_docs
    print(f"Loaded {len(docs)} documents.")
    if docs:
        print("Example document:", docs[0])
