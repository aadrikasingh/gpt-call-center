import os
import requests
from collections import OrderedDict

import streamlit as st

from openai.error import OpenAIError
from langchain.docstore.document import Document

from components.sidebar import sidebar
from utils import embed_docs, get_answer, search_docs

AZURE_SEARCH_API_VERSION = '2021-04-30-Preview'
AZURE_OPENAI_API_VERSION = "2023-03-15-preview"

def clear_submit():
    st.session_state["submit"] = False

# Use type hints to make the function signature clear.
def get_search_results(query: str, indexes: list) -> list:
    headers = {'Content-Type': 'application/json','api-key': os.environ["AZURE_SEARCH_KEY"]}
    agg_search_results = []
    
    for index in indexes:
        url = os.environ["AZURE_SEARCH_ENDPOINT"] + '/indexes/'+ index + '/docs'
        url += '?api-version={}'.format(AZURE_SEARCH_API_VERSION)
        url += '&search={}'.format(query)
        url += '&select=*'
        url += '&$top=5'  # You can change this to anything you need/want
        url += '&queryLanguage=en-us'
        # url += '&queryType=semantic'
        # url += '&semanticConfiguration=content'
        url += '&$count=true'
        url += '&speller=lexicon'
        # url += '&answers=extractive|count-3'
        # url += '&captions=extractive|highlight-false'

        resp = requests.get(url, headers=headers)

        # Print statements are useful for debugging but should be removed in production code.
        print(url)
        print(resp.status_code)

        search_results = resp.json()
        
        agg_search_results.append(search_results)

    return agg_search_results

st.set_page_config(page_title="GPT Call Center Support", page_icon="📖", layout="wide")
st.header("GPT Call Center Support")

with st.sidebar:
    st.markdown("""# Instructions""")
    st.markdown("""
                    Ask a question about your call center data.

                    For example:

                    - What is the customer agent name?
                    - Can you summarize the conversation between Donna and the customer?
                    - What are the customer contact details?

                    This search engine does not look at the open internet to answer these questions. If the context doesn't contain information, the engine will respond: I don't know.
                """)

coli1, coli2 = st.columns([2,1])

with coli1:
    query = st.text_input("Ask a question to your call center data", value= "What is the customer agent name?")

col1, col2, col3 = st.columns([1,1,3])

if (not os.environ.get("AZURE_SEARCH_ENDPOINT")) or (os.environ.get("AZURE_SEARCH_ENDPOINT") == ""):
    st.error("Please set your AZURE_SEARCH_ENDPOINT on your Web App Settings")
elif (not os.environ.get("AZURE_SEARCH_KEY")) or (os.environ.get("AZURE_SEARCH_KEY") == ""):
    st.error("Please set your AZURE_SEARCH_ENDPOINT on your Web App Settings")
elif (not os.environ.get("AZURE_OPENAI_ENDPOINT")) or (os.environ.get("AZURE_OPENAI_ENDPOINT") == ""):
    st.error("Please set your AZURE_OPENAI_ENDPOINT on your Web App Settings")
elif (not os.environ.get("AZURE_OPENAI_API_KEY")) or (os.environ.get("AZURE_OPENAI_API_KEY") == ""):
    st.error("Please set your AZURE_OPENAI_API_KEY on your Web App Settings")
else: 
    # Set environment variables for OpenAI API.
    os.environ["OPENAI_API_BASE"] = os.environ.get("AZURE_OPENAI_ENDPOINT")
    os.environ["OPENAI_API_KEY"] = os.environ.get("AZURE_OPENAI_API_KEY")
    os.environ["OPENAI_API_VERSION"] = os.environ["AZURE_OPENAI_API_VERSION"] = AZURE_OPENAI_API_VERSION
    
    if not query:
         # Use `st.warning` instead of `st.error` for non-critical messages.
         # Also provide more specific error messages when possible.
         st.warning("Please enter a question!")
         
    else:
         # Azure Search
         indexes = ["transcription-index"]
         
         agg_search_results = get_search_results(query=query, indexes=indexes)
         
         file_content = OrderedDict()
         
         try:
             for search_results in agg_search_results:                    
                 for result in search_results['value']:                        
                     file_content[result['content']['transcription_id']]={
                                             "caption": result['content']['conversation'],
                                             "score": result['@search.score'],
                                             "location": result['metadata_storage_path']                  
                                         }
         except Exception as e:  # Catch specific exceptions instead of using a bare except clause.
              # Provide more specific error messages when possible.
              st.markdown(f"No data returned from Azure Search. Error message: {e}")
              
         else:  # Use an else block after a try-except block to handle successful execution.
              st.session_state["submit"] = True
              
              placeholder_container = st.empty()
              
              try:
                  docs_list=[]
                  
                  for key,value in file_content.items():                        
                      docs_list.append(Document(page_content=value['caption'], metadata={"source": value["location"]}))

                      add_text="Reading the source documents to provide the best answer... ⏳"
                      

                  if "add_text" in locals():
                    with st.spinner(add_text):
                        if(len(docs_list)>0):
                            language="en"  # random.choice(list(file_content.items()))[1]["language"]
                            index=embed_docs(docs=docs_list, language=language)
                            sources=search_docs(index=index, query=query)   
                            
                            answer = get_answer(query, context = sources[0].page_content)                   
                        else: 
                            answer="No results found"
                      
                  with placeholder_container.container():
                      st.markdown("#### Answer")                      
                      st.text_area(label='', value=answer, height=250)
                              
              except OpenAIError as e:
                  # Provide more specific error messages when possible.
                  st.error(f"Open AI Error occurred. Error message: {e}")