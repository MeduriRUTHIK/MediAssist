
import re
import hashlib
from pathlib import Path

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer


# Project directories
BASE_DIR = Path(__file__).resolve().parents[2]

DOCUMENT_DIR = BASE_DIR / "data" / "medical_documents"
DATABASE_DIR = BASE_DIR / "data" / "chroma_db"

# Embedding configuration
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "medical_knowledge"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


# WHO webpage section headings
SECTION_HEADINGS = [
    "Key facts",
    "Overview",
    "Symptoms",
    "Type 1 diabetes",
    "Type 2 diabetes",
    "Gestational diabetes",
    "Impaired glucose tolerance and impaired fasting glycaemia",
    "Prevention",
    "Diagnosis and treatment",
    "WHO response",
    "References"
]


def load_documents():
    """Load text from PDF and TXT documents."""

    documents = []

    # Read PDF files
    for pdf_path in DOCUMENT_DIR.glob("*.pdf"):
        print(f"Reading PDF: {pdf_path.name}")

        try:
            reader = PdfReader(str(pdf_path))

            for page_number, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""

                if text.strip():
                    documents.append({
                        "text": text,
                        "source": pdf_path.name,
                        "section": f"PDF Page {page_number}",
                        "page": page_number
                    })

        except Exception as error:
            print(f"Could not read PDF: {error}")

    # Read TXT files
    for txt_path in DOCUMENT_DIR.glob("*.txt"):
        print(f"Reading TXT: {txt_path.name}")

        try:
            text = txt_path.read_text(encoding="utf-8")
            sections = split_into_sections(text)

            for section_name, section_text in sections:
                if section_text.strip():
                    documents.append({
                        "text": section_text,
                        "source": txt_path.name,
                        "section": section_name,
                        "page": 0
                    })

        except Exception as error:
            print(f"Could not read TXT: {error}")

    print(f"Total document sections loaded: {len(documents)}")

    return documents


def split_into_sections(text):
    """Split WHO text using its actual section headings."""

    headings_pattern = "|".join(
        re.escape(heading)
        for heading in sorted(
            SECTION_HEADINGS,
            key=len,
            reverse=True
        )
    )

    pattern = re.compile(
        rf"(?im)^\s*({headings_pattern})\s*$"
    )

    matches = list(pattern.finditer(text))

    if not matches:
        return [("General information", text.strip())]

    sections = []

    # Preserve introductory text before the first heading
    intro = text[:matches[0].start()].strip()

    if intro:
        sections.append(("Introduction", intro))

    for index, match in enumerate(matches):
        section_name = match.group(1).strip()

        start = match.end()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        section_text = text[start:end].strip()

        if section_text:
            sections.append((section_name, section_text))

    return sections


def split_into_chunks(text):
    """Split long sections into overlapping chunks."""

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end == len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def process_documents():

    if not DOCUMENT_DIR.exists():
        print("Medical documents folder not found.")
        return

    print("Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("Loading medical documents...")

    documents = load_documents()

    if not documents:
        print("No text available for processing.")
        return

    all_chunks = []
    all_metadata = []
    all_ids = []

    for document in documents:

        chunks = split_into_chunks(document["text"])

        for index, chunk in enumerate(chunks):

            unique_text = (
                f'{document["source"]}_'
                f'{document["section"]}_'
                f'{index}_'
                f'{chunk}'
            )

            chunk_hash = hashlib.md5(
                unique_text.encode("utf-8")
            ).hexdigest()

            all_chunks.append(chunk)

            all_metadata.append({
                "source": document["source"],
                "section": document["section"],
                "page": document["page"]
            })

            all_ids.append(chunk_hash)

    if not all_chunks:
        print("No valid chunks generated.")
        return

    print(f"Generated {len(all_chunks)} chunks.")

    print("Generating embeddings...")

    embeddings = model.encode(
        all_chunks,
        show_progress_bar=True,
        convert_to_numpy=True
    ).tolist()

    print("Connecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path=str(DATABASE_DIR)
    )

    # Rebuild the collection to remove old chunks
    # and avoid mixing old and new metadata.
    try:
        client.delete_collection(COLLECTION_NAME)
        print("Previous collection removed.")
    except Exception:
        print("No previous collection found.")

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    print("Storing medical knowledge...")

    collection.add(
        ids=all_ids,
        documents=all_chunks,
        metadatas=all_metadata,
        embeddings=embeddings
    )

    print("\nMedical knowledge ingestion completed!")

    print(f"Total chunks: {len(all_chunks)}")
    print(f"Stored records: {collection.count()}")
    print(f"Database location: {DATABASE_DIR}")


if __name__ == "__main__":
    process_documents()
