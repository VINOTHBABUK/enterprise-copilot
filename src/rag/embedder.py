import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.ingestion.database import Session, Document
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = "./data/chroma_db"


def get_vectorstore():
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )
    vectorstore = Chroma(
        collection_name="company_docs",
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH
    )
    return vectorstore


def chunk_text(text, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_text(text)


def embed_all_documents():
    session   = Session()
    documents = session.query(Document)\
                       .filter(Document.raw_text != None)\
                       .all()
    session.close()

    if not documents:
        print("No documents found. Run scraper first.")
        return

    print(f"Embedding {len(documents)} documents...")
    vectorstore = get_vectorstore()

    for doc in documents:
        print(f"  Processing: {doc.title}")

        chunks = chunk_text(doc.raw_text)
        print(f"  Chunks: {len(chunks)}")

        metadatas = []
        for i, chunk in enumerate(chunks):
            metadatas.append({
                "source":     doc.url or "",
                "title":      doc.title or "",
                "department": doc.department or "general",
                "doc_id":     str(doc.id),
                "chunk_id":   i
            })

        ids = [
            f"doc_{doc.id}_chunk_{i}"
            for i in range(len(chunks))
        ]

        vectorstore.add_texts(
            texts=chunks,
            metadatas=metadatas,
            ids=ids
        )
        print(f"  ✓ Embedded {len(chunks)} chunks")

    print(f"\n✓ All documents embedded into ChromaDB")


if __name__ == "__main__":
    embed_all_documents()