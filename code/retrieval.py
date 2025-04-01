import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts.chat import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory
from memory import get_full_chat_history, get_memory

os.environ["LANGCHAIN_TRACING_V2"] = "false"

def load_faiss_index(index_path="faiss_index"):
    """Loads the FAISS index from local storage."""
    embedding_function = OpenAIEmbeddings()
    return FAISS.load_local(index_path, embedding_function, allow_dangerous_deserialization=True)

def get_user_query():
    """Gets a query from the user."""
    return input("Enter your search query: ")

def search_faiss_index(vector_store, query_embedding, top_k=3):
    """Searches FAISS for the most relevant documents based on the query."""
    results = vector_store.similarity_search_by_vector(query_embedding, k=top_k)
    return results

def summarize_history(messages) -> str:
    """Summarizes recent chat history using LLM call"""

    summary_prompt = PromptTemplate.from_template("""
    Given the following chat history, generate a concise summary of what the user is trying to understand or achieve.

    Chat history:
    {history}

    Summary:
    """)
    
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    chain = summary_prompt | llm 

    msg_to_str = "\n".join(f"{msg.type.capitalize()}: {msg.content}" for msg in messages)
    return str(chain.invoke({"history": msg_to_str}))

def query_llm_with_history(query, context, model="gpt-3.5-turbo"):
    # --- Prompt template ---
    system_prompt = (
        "You are an AI assistant that answers user queries based on retrieved context from a document database. "
        "If the context is relevant, provide a detailed answer. If unsure, say you don't have enough information."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Context: {context}\n\nQuestion: {query}")
    ])

    # --- LLM and parser ---
    llm = ChatOpenAI(model=model, temperature=0)
    parser = StrOutputParser()

    # --- LCEL-style chain ---
    rag_chain = prompt | llm | parser
    
    # --- Wrap chain with memory ---
    chain_with_memory = RunnableWithMessageHistory(
        rag_chain,
        get_memory,
        input_messages_key="query",
        history_messages_key="history"
    )

    # --- Run a conversation loop ---
    session_id = "user-01-session-001"  # Can be user ID or chat ID

    response = chain_with_memory.invoke(
        {"query": query, "context": context},
        config={"configurable": {"session_id": session_id}}
    )
    return response 

def query_llm(query, context, model="gpt-4"):
    """Queries OpenAI's LLM using the retrieved context."""
    llm = ChatOpenAI(temperature=0, model_name=model)

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

def get_rag_response(query: str, history=True):
    #print("1. Loading FAISS index...")
    vector_store = load_faiss_index()

    #print("\n2. Summarizing conversation history (if applicable)...")
    session_id = "user-01-session-001"
    chat_history = get_full_chat_history(session_id) if history else []
    summary = summarize_history(chat_history) if chat_history else ""
    print(f"\n Summary: {summary}")
    print("-" * 50)

    #print("\n3. Creating embedding for user query...")
    embedding_model = OpenAIEmbeddings()
    full_query = summary + "\n" + query if summary else query
    query_embedding = embedding_model.embed_query(full_query)

    #print("\n4. Searching for relevant documents for the query...")
    results = search_faiss_index(vector_store, query_embedding, top_k=5)
    
    if not results:
        print("\nNo relevant documents found. Unable to generate an answer.")
    else:
        print(f"\nList of relevant documents - ")
        unique_sources = set()
        for doc in results:
            source = doc.metadata.get('source', 'Unknown Source')
            if source not in unique_sources:
                print(f"Document: {source}\n")
                unique_sources.add(source)
    
    print("-" * 50)

    # Concatenate retrieved document chunks
    context = "\n\n".join([doc.page_content for doc in results])

    if history:
        #print("\n6. Querying LLM with history...")
        answer = query_llm_with_history(query, context)
    else:
        #print("\n5. Querying LLM without history...")
        answer = query_llm(query, context)

    return str(answer)

def main():
    """Main function to load FAISS, take user input, perform search, and display results."""
    history = True

    while True:
        query = get_user_query()
        if query.lower() in ["exit", "quit"]:
            print("Exiting search.")
            break
   
        answer = get_rag_response(query, history)

        print("\nAI Generated Answer:")
        print(answer)
        print("-" * 50)
        '''print("\nHistory:")
        for msg in get_full_chat_history("user-01-session-001"):
            print(f"{msg.type.capitalize()}: {msg.content}")
        print("-" * 50)'''

if __name__ == "__main__":
    main()
