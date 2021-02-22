import streamlit as st
from weasyprint import HTML
import json

from utils import fetch_response
from utils import show_corpus
from utils import tooltip
from utils import category_df
from utils import generate_sentiment_df
from utils import generate_sentiment_results
from utils import download_file
from utils import beutify_html

def sentiment_analysis(client, corpus, style, tooltip_dict, filename, language):
    '''
	Function for sentiment analysis.
	'''

    try:
    
        document_syncon = fetch_response(client, corpus, 'relevants', language)

        syncon_df = category_df(document_syncon, "_main_syncons")

        h1 = show_corpus(corpus, style)

        document = fetch_response(client, corpus, 'sentiment')

        overall_score = document['_sentiment']['_overall']

        positive_score = document['_sentiment']['_positivity']

        negative_score = document['_sentiment']['_negativity']

        df = generate_sentiment_df(document["_sentiment"]["_items"], syncon_df)

        tooltip_resp = tooltip("Sentiment Analysis", tooltip_dict["Sentiment Analysis"])
        st.markdown(tooltip_resp, unsafe_allow_html=True)

        html, html2 = generate_sentiment_results(df, syncon_df, corpus, overall_score, positive_score, negative_score)

        if html2:

            st.write(html, unsafe_allow_html=True)
            st.write(" ")

            st.write(f"{style}{beutify_html(html2)}", unsafe_allow_html=True)

            h1 = beutify_html(h1, True, "Corpus:")

            h2 = beutify_html(html2, True, "Sentiment Analysis:")

            pdfile = HTML(string=h1 + html +h2).write_pdf()

            download_button_str = download_file(pdfile, filename+'_sentiment_analysis.pdf')

            st.markdown(download_button_str, unsafe_allow_html=True)

        else:
            st.write(html, unsafe_allow_html=True)
            st.write(" ")

            h1 = beutify_html(h1, True, "Corpus:")

            pdfile = HTML(string=h1 + html).write_pdf()

            download_button_str = download_file(pdfile, filename+'_sentiment_analysis.pdf')

            st.markdown(download_button_str, unsafe_allow_html=True)

        st.write(" ")
        st.write("API used to get these results [docs](https://docs.expert.ai/nlapi/latest/guide/sentiment-analysis/) and [docs](https://docs.expert.ai/nlapi/latest/guide/keyphrase-extraction/)")

    except Exception as e:
        st.warning("No sentiment found in input sentence.")