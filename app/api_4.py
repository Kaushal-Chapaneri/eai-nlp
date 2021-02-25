import streamlit as st
from weasyprint import HTML

from app.utils import fetch_classification_response
from app.utils import category_df
from app.utils import show_corpus
from app.utils import load_colors
from app.utils import highlight_tags
from app.utils import beutify_html
from app.utils import download_file


def document_tagging(client, corpus, style, tooltip_dict, filename, language):
    '''
	Function for document tagging / classification.
	'''

    h1 = show_corpus(corpus, style)
    st.markdown("""<h3 style='color: black;'><a id="top">Document Tagging / Classification</a></h3>""", unsafe_allow_html=True)
    st.write("")
    st.write("")
    
    document = fetch_classification_response(client, corpus, language)
    
    if document['_categories']:
        df = category_df(document, "_categories")
        st.write("select tag to view related phrases.")
        st.write("")
        unique_tags = df['_label'].unique().tolist()
        colors = list(load_colors().values())
        i = 0
        for col in st.beta_columns(len(unique_tags)):
            if col.button(unique_tags[i]):
                html = highlight_tags(unique_tags[i], df, corpus, colors[i])
                st.write(f"{style}{beutify_html(html)}", unsafe_allow_html=True)
                h1 = beutify_html(h1, True, "Corpus:")
                h2 = beutify_html(html, True, "Document Tagging / Classification :: Tag :: "+str(unique_tags[i]))
                pdfile = HTML(string=h1 + h2).write_pdf()
                download_button_str = download_file(pdfile, filename+'_tagging.pdf')
                st.markdown(download_button_str, unsafe_allow_html=True)
            i += 1

        st.write(" ")
        st.write("API used to get these results [docs](https://docs.expert.ai/nlapi/latest/guide/classification/)")
        
    else:
        st.write("No Category / tag found for this corpus..")
