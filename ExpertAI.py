import streamlit as st
from expertai.nlapi.cloud.client import ExpertAiClient

from utils import header
from utils import set_credential
from utils import load_corpus
from utils import beutify_html
from utils import load_tooltip
from utils import load_language

from api_1 import enitiy_recognition
from api_2 import important_sentences
from api_2 import important_lemmas_phrses
from api_3 import relation_identification
from api_4 import document_tagging
from api_5 import sentiment_analysis

page = st.sidebar.selectbox("Select a page", ["Overview", "Application", "Try It"])

if page == "Overview":
	header()
	st.write("")
	st.write("")

	a1 = "<p style='text-align: justify;font-size:20px;'><a style='text-decoration:none' target=_blank href=https://www.expert.ai/>Expert.ai</a> Natural Language API is a cloud-based software service providing a comprehensive set of natural language understanding capabilities based on expert.ai technology.</p><br>"
	st.markdown(a1,unsafe_allow_html=True)

	a2 = "<p style='text-align: justify;font-size:20px;'>This Proof-Of-Concept (POC) is developed for the submission of <b>'Natural Language & Text Analytics API'</b> <a style='text-decoration:none' target=_blank href=https://expertai-nlapi-012021.devpost.com/>Hackathon</a>.</p><br>"
	st.markdown(a2,unsafe_allow_html=True)

	a3 ="<p style='text-align: justify;font-size:20px;'>This Application uses APIs provided by expert.ai and generates following analysis for input text."

	a3 += "<ul><li>Entity Recognition</li><li>Important Sentence Identification</li><li>Important Lemmas / Phrases Extraction</li><li>Relation Identification</li><li>Document Tagging / Classification</li><li>Sentiment Analysis</li></ul></p><br>"
	st.markdown(a3,unsafe_allow_html=True)

	a4 = "<p style='text-align: justify;font-size:20px;'>Watch below video to get most out of this application.</p><br>"
	st.markdown(a4,unsafe_allow_html=True)

	st.video("https://www.youtube.com/watch?v=xlu4yVPZ_Uc")

elif page == "Application":

	header()
	set_credential()
	client = ExpertAiClient()
	corpus = load_corpus()
	tooltip = load_tooltip()
	
	st.write(" ")
	st.markdown("""<h3 style='color: black;'><a id="top">Corpus</a></h3>""", unsafe_allow_html=True)
	st.write(" ")

	style = "<style>mark.entity { display: inline-block }</style>"
	page2 = st.sidebar.selectbox("Select Analysis Type", ["Entity Recognition", "Important Sentence", "Important Lemmas / Phrases",
	"Relation Identification", "Document Tagging / Classification", "Sentiment Analysis"])

	if page2 == "Entity Recognition":

		enitiy_recognition(client, corpus[0]['corpus1'], style, "corpus_1", tooltip, language='en')
	
	elif page2 == "Important Sentence":

		important_sentences(client, corpus[0]['corpus1'], style, "corpus_1", tooltip, language='en')

	elif page2 == "Important Lemmas / Phrases":

		important_lemmas_phrses(client, corpus[0]['corpus1'], style, "corpus_1", tooltip, language='en')

	elif page2 == "Relation Identification":

		relation_identification(client, corpus[0]['corpus1'], style, tooltip, language='en')

	elif page2 == "Document Tagging / Classification":

		document_tagging(client, corpus[0]['corpus1'], style, tooltip, "corpus_1", language='en')

	elif page2 == "Sentiment Analysis":

		sentiment_analysis(client, corpus[0]['corpus1'], style, tooltip, "corpus_1", language='en')

	st.write("")
	st.write("")

	href = f"""<a href="#top">Back to top</a>"""
	st.markdown(href,unsafe_allow_html=True)


elif page == "Try It":
	header()
	st.write("")
	languages = load_language()

	st.write("Select Language")
	language_option = st.selectbox("",tuple(languages.keys()))
	language_option = languages[language_option]
	st.markdown("""<h3 style='color: black;'><a id="top">Input Corpus</a></h3>""", unsafe_allow_html=True)

	input_text = st.text_area('',height=150)
	set_credential()
	client = ExpertAiClient()
	tooltip = load_tooltip()
	st.write(" ")
	
	if input_text:
		st.markdown("""<h3 style='color: black;'><a id="top">Corpus</a></h3>""", unsafe_allow_html=True)
		style = "<style>mark.entity { display: inline-block }</style>"
		
		page2 = st.sidebar.selectbox("Select Analysis Type", ["Entity Recognition", "Important Sentence", "Important Lemmas / Phrases",
		"Relation Identification", "Document Tagging / Classification", "Sentiment Analysis"])
		
		if page2 == "Entity Recognition":

			enitiy_recognition(client, input_text, style, "try_it", tooltip, language_option)
		
		elif page2 == "Important Sentence":

			important_sentences(client, input_text, style, "try_it", tooltip, language_option)

		elif page2 == "Important Lemmas / Phrases":

			important_lemmas_phrses(client, input_text, style, "try_it", tooltip, language_option)

		elif page2 == "Relation Identification":

			relation_identification(client, input_text, style, tooltip, language_option)

		elif page2 == "Document Tagging / Classification":

			document_tagging(client, input_text, style, tooltip, "try_it", language_option)
		
		elif page2 == "Sentiment Analysis":

			sentiment_analysis(client, input_text, style, tooltip, "try_it", language_option)

		st.write("")
		st.write("")
		href = f"""<a href="#top">Back to top</a>"""
		st.markdown(href,unsafe_allow_html=True)	
