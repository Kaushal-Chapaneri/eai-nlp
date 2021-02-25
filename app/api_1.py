import streamlit as st
from weasyprint import HTML

from app.utils import to_df
from app.utils import to_html
from app.utils import mask_tag
from app.utils import download_file
from app.utils import beutify_html
from app.utils import fetch_response
from app.utils import show_corpus
from app.utils import tooltip


def enitiy_recognition(client, corpus, style, filename, tooltip_dict, language):
    '''
	Function for entity detection and entity masking.
	'''

    try:

        show_corpus(corpus, style)
        
        document = fetch_response(client, corpus, 'entities', language)
        entity_df, knowledge_df = to_df(document)
 
        html = to_html(entity_df, knowledge_df, document['_content'])

        types = entity_df['_type'].unique().tolist()
        st.write("")
        tooltip_resp = tooltip("Entity Recognition & Masking", tooltip_dict["Entity Recognition and Masking"])
        st.markdown(tooltip_resp, unsafe_allow_html=True) #Title rendering
        
        selectednames=st.multiselect('Select enitiy to mask',types)

        if selectednames:
            html = mask_tag(html, selectednames, entity_df, document['_content'])
        
        st.write(f"{style}{beutify_html(html)}", unsafe_allow_html=True)

        pdfile = HTML(string=beutify_html(html, True, "Entity Recognition & Masking:")).write_pdf()

        download_button_str = download_file(pdfile, filename+'_entity.pdf')

        st.markdown(download_button_str, unsafe_allow_html=True)
        st.write(" ")
        st.write("API used to get these results [docs](https://docs.expert.ai/nlapi/latest/guide/entity-recognition/)")
    
    except Exception as e:

        if e.args[0].split(':')[-1] == ' 413':
                st.warning("Free tier does not support processing large corpus.")
        else:
                st.warning("There's no entity in input sentence.")
