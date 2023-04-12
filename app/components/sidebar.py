import streamlit as st
import os


def sidebar():
    with st.sidebar:
        st.image("https://fossbytes.com/wp-content/uploads/2019/07/open-AI-microsoft.jpg")

        st.markdown("---")
        st.markdown("# About")
        st.markdown("""
            Ask a question about your call center data.

            For example:
            - What is the customer agent name?
            - Can you summarize the conversation between Donna and the customer?
            - What are the customer contact details?

            This search engine does not look at the open internet to answer these questions. If the context doesn't contain information, the engine will respond: I don't know.
        """
        )
        st.markdown("---")
