import streamlit as st

st.set_page_config(page_title="GPT Call Center Support", page_icon="📖", layout="wide")


image_path = './img/header.jpg'
st.image(image_path,  use_column_width=True)


#st.image("https://thumbs.dreamstime.com/b/customer-service-operators-headsets-computers-consulting-clients-call-center-handling-system-virtual-concept-header-134627879.jpg")

st.header("GPT Call Center Support")


st.markdown("---")
st.markdown("""
    GPT Call Center Support allows you to ask questions about your
    call center data and get accurate answers with instant citations.
    
    **👈 Select a demo from the sidebar** to see some examples
    of what Azure Cognitive Search and Azure OpenAI Service can do!    


    
"""
)
st.markdown("---")


st.sidebar.success("Select a demo above.")
