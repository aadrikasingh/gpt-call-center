import re
from typing import Any, Dict, List

import streamlit as st

from embeddings import OpenAIEmbeddings
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.docstore.document import Document
from langchain.vectorstores.faiss import FAISS
from langchain.vectorstores import VectorStore

import os
import openai

def get_answer(query, context):
    openai.api_type = "azure"
    openai.api_base = os.environ.get("AZURE_OPENAI_ENDPOINT")
    openai.api_version = "2023-03-15-preview"
    openai.api_key = os.environ.get("AZURE_OPENAI_API_KEY")

    content = "You are an enterprise Call Center chatbot whose primary goal is to help users extract insights from calls bewteen agents and customers. \n•\tProvide concise replies that are polite and professional. \n•\tAnswer questions truthfully based on provided below context. \n•\tDo not answer questions that are not related to conversations and respond with \"I can only help with any call center questions you may have.\". \n•\tIf you do not know the answer to a question, respond by saying “I do not know the answer to your question in the prodvided context”\n•\t"

    response = openai.ChatCompletion.create(
                engine="gpt-4-32k",
                messages = [{"role":"system","content":content+context}
                            ,{"role":"user","content": query}],
                temperature=0.7,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)
                
    return response.choices[0].message.content

def embed_docs(docs: List[Document], language: str) -> VectorStore:
    """Embeds a list of Documents and returns a FAISS index"""

    embeddings = OpenAIEmbeddings(
        document_model_name="text-embedding-ada-002",
        query_model_name="text-embedding-ada-002",
    )
    
    index = FAISS.from_documents(docs, embeddings)

    return index


def search_docs(index: VectorStore, query: str) -> List[Document]:
    """Searches a FAISS index for similar chunks to the query and returns a list of Documents."""

    # Search for similar chunks
    documents = index.similarity_search(query, k=4)

    return documents