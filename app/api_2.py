import streamlit as st
from weasyprint import HTML

from app.utils import download_file
from app.utils import beutify_html
from app.utils import get_important_sentence
from app.utils import get_important_words
from app.utils import fetch_response
from app.utils import show_corpus
from app.utils import tooltip

def important_sentences(client, corpus, style, filename, tooltip_dict, language):
    '''
	Function for generating visualisation for important sentence.
	'''

    document = fetch_response(client, corpus, 'relevants', language)

    if document['_main_sentences']:

        try:

            h1 = show_corpus(corpus, style)

            tooltip_resp = tooltip("Important Sentence", tooltip_dict["Important Sentence"])
            st.markdown(tooltip_resp, unsafe_allow_html=True)
            st.write("")

            html  = get_important_sentence(document['_main_sentences'], corpus)

            st.write(f"{style}{beutify_html(html)}", unsafe_allow_html=True)

            h1 = beutify_html(h1, True, "Corpus:")

            h2 = beutify_html(html, True, "Important Sentences:")

            pdfile = HTML(string=h1 + h2).write_pdf()

            download_button_str = download_file(pdfile, filename+'_important_sentence.pdf')

            st.markdown(download_button_str, unsafe_allow_html=True)
            st.write(" ")
            st.write("API used to get these results [docs](https://docs.expert.ai/nlapi/latest/guide/keyphrase-extraction/)")
        
        except Exception as e:
            st.warning("There's no important sentence in input text.")


def important_lemmas_phrses(client, corpus, style, filename, tooltip_dict, language):
    '''
	Function for generating visualisations of important phrases and leammas.
	'''

    document = fetch_response(client, corpus, 'relevants', language)

    if document['_main_lemmas']:
        ppl = get_important_words(document['_main_syncons'], corpus, '#aaaaaa')

        try:

            h1 = show_corpus(corpus, style)

            tooltip_resp = tooltip("Important Lemmas", tooltip_dict["Important Lemmas"])
            st.markdown(tooltip_resp, unsafe_allow_html=True)

            html = get_important_words(document['_main_lemmas'], corpus, '#ffd8d8')

            st.write(f"{style}{beutify_html(html)}", unsafe_allow_html=True)

            h1 = beutify_html(h1, True, "Corpus:")

            h2 = beutify_html(html, True, "Important Lemmas:")

            pdfile = HTML(string=h1 + h2).write_pdf()

            download_button_str = download_file(pdfile, filename+'_important_lemmas.pdf')

            st.markdown(download_button_str, unsafe_allow_html=True)
            st.write(" ")
        
        except Exception as e:
            if e.args[0].split(':')[-1] == ' 413':
                st.warning("Free tier does not support processing large corpus.")
            else:
                st.warning("There's no important lemmas in input sentence.")

    if document['_main_phrases']:

        st.write("")

        try:

            tooltip_resp = tooltip("Important Phrases", tooltip_dict["Important Phrases"])
            st.markdown(tooltip_resp, unsafe_allow_html=True)

            html = get_important_words(document['_main_phrases'], corpus, '#9ed9d9')

            st.write(f"{style}{beutify_html(html)}", unsafe_allow_html=True)

            h2 = beutify_html(html, True, "Important Phrases:")

            pdfile = HTML(string=h1 + h2).write_pdf()

            download_button_str = download_file(pdfile, filename+'_important_phrases.pdf')

            st.markdown(download_button_str, unsafe_allow_html=True)

            st.write(" ")
            st.write("API used to get these results [docs](https://docs.expert.ai/nlapi/latest/guide/keyphrase-extraction/)")
        
        except Exception as e:
            if e.args[0].split(':')[-1] == ' 413':
                st.warning("Free tier does not support processing large corpus.")
            else:
                st.warning("There's no important Phrases in input sentence.")