#import os
import re
#import pickle
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

def load_text_file(file_path):
    """Reads a text file and extracts document content which matches along with associated file names."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    file_pattern = re.compile(r"--- File: (.+?) ---")
    documents = []
    current_file = None
    current_text = []

    for line in lines:
        match = file_pattern.match(line)
        if match:
            if current_text and current_file:
                documents.append(Document(page_content=" ".join(current_text), metadata={"source": current_file}))
                current_text = []
            current_file = match.group(1)
        else:
            current_text.append(line.strip())

    if current_text and current_file:
        documents.append(Document(page_content=" ".join(current_text), metadata={"source": current_file}))

    return documents

def split_documents(documents, chunk_size=500, chunk_overlap=100):
    """Splits documents into smaller chunks while retaining metadata."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(documents)

def create_faiss_index(documents, embedding_function):
    """Creates a FAISS index from a list of documents using the specified embedding function."""
    return FAISS.from_documents(documents, embedding_function)

def save_faiss_index(vector_store, index_path="faiss_index"):
    """Saves the FAISS index locally."""
    vector_store.save_local(index_path)

def main():
    """Main function to process documents, create FAISS index, and save it."""
    text_file_path = "processed_texts.txt"

    print("Loading text file...")
    documents = load_text_file(text_file_path)

    print("Splitting documents...")
    split_documents_list = split_documents(documents)

    print("Initializing embedding function...")
    embedding_function = OpenAIEmbeddings()

    print("Creating FAISS index...")
    vector_store = create_faiss_index(split_documents_list, embedding_function)

    print("Saving FAISS index...")
    save_faiss_index(vector_store)

    print(f"Processed {len(split_documents_list)} document chunks and saved FAISS index successfully!")

if __name__ == "__main__":
    main()