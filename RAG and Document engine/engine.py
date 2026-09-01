import os
import json
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import chromadb

# Storage Configurations
DOCS_DIR = "./documents"
DB_DIR = "./chroma_db"
COLLECTION_NAME = "financial_intelligence"
MODEL_NAME = "all-MiniLM-L6-v2"

# Initialize Local Embedding Model & ChromaDB Client
print("Initializing embedding model and local database...")
embedding_model = SentenceTransformer(MODEL_NAME)
chroma_client = chromadb.PersistentClient(path=DB_DIR)
collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)


def extract_and_chunk_pdf(pdf_path, chunk_size=500, overlap=50):
    """Extracts text from a PDF and splits it into overlapping character chunks."""
    reader = PdfReader(pdf_path)
    full_text = ""
    
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    chunks = []
    start = 0
    text_length = len(full_text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = full_text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def index_documents():
    """Scans ./documents, chunks PDFs, generates embeddings, and saves to ChromaDB."""
    if not os.path.exists(DOCS_DIR):
        os.makedirs(DOCS_DIR)
        print(f"Created '{DOCS_DIR}'. Add PDFs here and rerun.")
        return

    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".pdf")]
    
    if not pdf_files:
        print(f"No PDFs found inside '{DOCS_DIR}'. Please add PDFs from your teammate.")
        return

    print(f"Found {len(pdf_files)} PDF file(s). Processing...")

    documents_to_add = []
    ids_to_add = []
    metadatas_to_add = []

    for filename in pdf_files:
        pdf_path = os.path.join(DOCS_DIR, filename)
        chunks = extract_and_chunk_pdf(pdf_path)

        for idx, chunk in enumerate(chunks):
            chunk_id = f"{filename}_chunk_{idx}"
            documents_to_add.append(chunk)
            ids_to_add.append(chunk_id)
            metadatas_to_add.append({"source": filename, "chunk_index": idx})

    if documents_to_add:
        # Generate numerical vector embeddings locally
        embeddings = embedding_model.encode(documents_to_add).tolist()

        # Write vectors and raw text to local storage
        collection.add(
            documents=documents_to_add,
            embeddings=embeddings,
            metadatas=metadatas_to_add,
            ids=ids_to_add
        )
        print(f"Successfully indexed {len(documents_to_add)} text chunks into ChromaDB.")


def query_rag(query_text, top_k=3):
    """Executes a semantic vector search and returns matching snippets as JSON."""
    query_embedding = embedding_model.encode([query_text]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    formatted_results = []
    if results and results["documents"]:
        for i in range(len(results["documents"][0])):
            snippet = {
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results and results["distances"] else None
            }
            formatted_results.append(snippet)

    return json.dumps({"query": query_text, "retrieved_facts": formatted_results}, indent=2)


if __name__ == "__main__":
    # Index PDFs into vector store
    index_documents()

    # Test retrieval output
    sample_query = "What are the regulatory guidelines or market risks?"
    print(f"\n--- Running Test Search: '{sample_query}' ---")
    print(query_rag(sample_query, top_k=2))
