import os
import streamlit as st
from retrieval import get_rag_response  # Import the function from your existing script

# Streamlit UI Configuration
st.set_page_config(page_title="Knowledge Assistant", layout="wide")

st.title("Knowledge Assistant")
st.write("Enter a query below to retrieve relevant information from your documents.")

# User input for query
query = st.text_input("Ask a question:")

# Placeholder for search status
status_placeholder = st.empty()

#placeholder for response
response_placeholder = st.empty()

if query:
    #Clear the previous response, if any
    #response_placeholder.empty()

    # Show "Searching..." message
    status_placeholder.write("🔎 Searching for relevant information...")

    try:
        response = get_rag_response(query)  # Call the RAG function
        
        # Clear the "Searching..." message
        status_placeholder.empty()
        
        # Display AI-generated response
        #st.subheader("💡 AI Response")
        response_placeholder.write(response)
    
    except Exception as e:
        # Clear the "Searching..." message in case of an error
        status_placeholder.empty()
        st.error(f"An error occurred: {e}")

# Manual Stop Button
st.button("End Session", on_click=lambda: os._exit(0))  # Manual Stop Button
