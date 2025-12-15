from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

# Singleton to hold the vectorstore
_vectorstore = None

def reset_vectorstore():
    """Reset vectorstore to force rebuild with new documents"""
    global _vectorstore
    _vectorstore = None

def build_vectorstore(pdf_path: str, response_md_path: str = None):
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    print(f"Loading PDF from {pdf_path}...")
    pdf_loader = PyPDFLoader(pdf_path)
    pdf_docs = pdf_loader.load()

    all_docs = pdf_docs

    # Load response.md if provided
    if response_md_path and os.path.exists(response_md_path):
        print(f"Loading response format from {response_md_path}...")
        md_loader = TextLoader(response_md_path)
        md_docs = md_loader.load()
        # Add metadata to distinguish source
        for doc in md_docs:
            doc.metadata['source'] = 'response_format'
            doc.metadata['type'] = 'response_template'
        all_docs.extend(md_docs)

    print(f"Splitting {len(all_docs)} documents...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(all_docs)
    print(f"Created {len(chunks)} chunks.")

    print("Initializing embeddings...")
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables.")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/text-embedding-004",
        google_api_key=api_key,
    )

    print("Building FAISS vectorstore...")
    _vectorstore = FAISS.from_documents(chunks, embeddings)
    return _vectorstore

def get_vectorstore():
    global _vectorstore
    if _vectorstore is None:
        # Default paths
        base_dir = os.path.dirname(os.path.dirname(__file__))
        pdf_path = os.path.join(base_dir, "data", "sabermetrics.pdf")
        response_md_path = os.path.join(base_dir, "docs", "response.md")

        if os.path.exists(pdf_path):
            build_vectorstore(pdf_path, response_md_path)
        else:
            raise FileNotFoundError(f"PDF not found at {pdf_path}")
    return _vectorstore

def search(query: str, k: int = 3):
    vs = get_vectorstore()
    results = vs.similarity_search(query, k=k)
    return results

if __name__ == "__main__":
    # Test the pipeline
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        pdf_path = os.path.join(base_dir, "data", "sabermetrics.pdf")
        response_md_path = os.path.join(base_dir, "docs", "response.md")

        if not os.path.exists(pdf_path):
            print(f"Error: {pdf_path} does not exist. Please generate it first.")
        else:
            print(f"Testing with PDF: {pdf_path}")
            print(f"Testing with response.md: {response_md_path}")
            vs = build_vectorstore(pdf_path, response_md_path)
            query = "OPS가 뭐야?"
            print(f"\nQuery: {query}")
            results = search(query)
            for i, doc in enumerate(results):
                print(f"\nResult {i+1}:")
                print(f"Content: {doc.page_content}")
                print(f"Metadata: {doc.metadata}")
    except Exception as e:
        print(f"An error occurred: {e}")
