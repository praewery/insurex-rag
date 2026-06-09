import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

PDF_DIR = "data/pdfs"
VECTORSTORE_DIR = "vectorstore"


def load_and_split_pdfs():
    pdf_files = glob.glob(f"{PDF_DIR}/*.pdf")
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {PDF_DIR}")

    all_docs = []
    for pdf_path in sorted(pdf_files):
        print(f"Loading: {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        all_docs.extend(docs)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(all_docs)
    print(f"Total chunks: {len(chunks)}")
    return chunks


def build_vectorstore(chunks=None):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    if os.path.exists(VECTORSTORE_DIR):
        print("Loading existing vectorstore...")
        return Chroma(
            persist_directory=VECTORSTORE_DIR,
            embedding_function=embeddings
        )

    if chunks is None:
        chunks = load_and_split_pdfs()

    print("Building vectorstore...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_DIR
    )
    print("Vectorstore saved.")
    return vectorstore


if __name__ == "__main__":
    chunks = load_and_split_pdfs()
    build_vectorstore(chunks)
    print("Done!")