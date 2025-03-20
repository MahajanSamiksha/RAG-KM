import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

os.environ["LANGCHAIN_TRACING_V2"] = "false"

def load_faiss_index(index_path="faiss_index"):
    """Loads the FAISS index from local storage."""
    embedding_function = OpenAIEmbeddings()
    return FAISS.load_local(index_path, embedding_function, allow_dangerous_deserialization=True)

def get_user_query():
    """Gets a query from the user."""
    return input("Enter your search query: ")

def search_faiss_index(vector_store, query, top_k=3):
    """Searches FAISS for the most relevant documents based on the query."""
    results = vector_store.similarity_search(query, k=top_k)
    return results

def query_llm(query, context, model="gpt-4"):
    """Queries OpenAI's LLM using the retrieved context."""
    llm = ChatOpenAI(model_name=model)

    system_prompt = (
        "You are an AI assistant that answers user queries based on retrieved context from a document database. "
        "If the context is relevant, provide a detailed answer. If unsure, say you don't have enough information."
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Context:\n{context}\n\nUser Query: {query}")
    ]

    response = llm.invoke(messages)
    return response.content

def get_rag_response(query: str):
    print("1. Loading FAISS index...")
    vector_store = load_faiss_index()

    print("\n 2. Searching for relevant documents for the query...")
    results = search_faiss_index(vector_store, query)
    
    if not results:
        print("\nNo relevant documents found. Unable to generate an answer.")
    else:
        print(f"\n3. Found {len(results)} relevant documents for the query.")
    
    # Concatenate retrieved document chunks
    context = "\n\n".join([doc.page_content for doc in results])

    print("\n4. Context created.Generating answer from LLM...")
    answer = query_llm(query, context)

    return str(answer)

def main():
    """Main function to load FAISS, take user input, perform search, and display results."""
    print("1. Loading FAISS index...")
    vector_store = load_faiss_index()

    while True:
        query = get_user_query()
        if query.lower() in ["exit", "quit"]:
            print("Exiting search.")
            break

        print("\n 2. Searching for relevant documents for the query...")
        results = search_faiss_index(vector_store, query)

        if not results:
            print("\nNo relevant documents found. Unable to generate an answer.")
            continue
        else:
            print(f"\n3. Found {len(results)} relevant documents for the query.")

        # Concatenate retrieved document chunks
        context = "\n\n".join([doc.page_content for doc in results])

        print("\n4. Context created.Generating answer from LLM...")
        answer = query_llm(query, context)

        print("\n5. AI Generated Answer:")
        print(answer)
        print("-" * 50)

if __name__ == "__main__":
    main()
