
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# Project directories
BASE_DIR = Path(__file__).resolve().parents[2]
DATABASE_DIR = BASE_DIR / "data" / "chroma_db"

# Embedding configuration
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "medical_knowledge"

# Load embedding model
print("Loading embedding model...")

model = SentenceTransformer(MODEL_NAME)

# Connect to ChromaDB
client = chromadb.PersistentClient(
    path=str(DATABASE_DIR)
)

collection = client.get_collection(
    name=COLLECTION_NAME
)


def retrieve_documents(question, top_k=3):
    """Retrieve relevant medical document chunks."""

    if collection.count() == 0:
        print("Medical knowledge database is empty.")
        return []

    # Convert question into an embedding
    question_embedding = model.encode(
        question
    ).tolist()

    # Search ChromaDB
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=min(top_k, collection.count()),
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_documents = []

    if not results["documents"] or not results["documents"][0]:
        return retrieved_documents

    for i, document in enumerate(results["documents"][0]):

        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]

        retrieved_documents.append({
            "text": document,
            "source": metadata.get("source", "Unknown"),
            "section": metadata.get("section", "Unknown"),
            "page": metadata.get("page", 0),
            "distance": round(distance, 4)
        })

    return retrieved_documents


if __name__ == "__main__":

    question = input("Ask a medical question: ")

    results = retrieve_documents(question)

    print("\nRetrieved medical information:\n")

    if not results:
        print("No relevant information found.")

    for result in results:

        print("Source:", result["source"])
        print("Section:", result["section"])
        print("Page:", result["page"])
        print("Distance:", result["distance"])
        print("Content:", result["text"])
        print("-" * 60)
