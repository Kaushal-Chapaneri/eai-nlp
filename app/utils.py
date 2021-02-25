import os
import streamlit as st
import json
import pandas as pd
import base64
import uuid
import re
import lxml.html as LH
from pyquery import PyQuery 
from io import StringIO
import docx2txt
import pdfplumber
import langid

@st.cache
def load_credential():
	'''
	Function to load credential from credential file, of developer account of expert.ai
	'''
	with open('credential.json') as f:
		return json.load(f)

@st.cache
def set_credential():
	'''
	Function to set credential in os environment.
	'''
	cred = load_credential()
	os.environ["EAI_USERNAME"] = cred["EAI_USERNAME"]
	os.environ["EAI_PASSWORD"] = cred["EAI_PASSWORD"]

def header():
	'''
	Header to display in all page.
	'''
	st.markdown("""<h1 style='text-align: center; color: black;'><a id="top">Expert.ai NLP</a></h1>""", unsafe_allow_html=True)

@st.cache
def load_corpus():
	with open('asset/corpus.json') as f:
		return json.load(f)

@st.cache
def load_tooltip():
	'''
	Function load tooltip from json file.
	'''
	with open('asset/analysis_tooltip.json') as f:
		return json.load(f)

@st.cache
def load_colors():
	'''
	Function to load colors from json file, which used in all visualisations.
	'''
	with open('asset/color.json') as f:
		return json.load(f)

@st.cache
def load_language():
	'''
	Function to load languages from json file, this is used in try it page.
	'''
	with open('asset/language.json') as f:
		return json.load(f)


def get_color(ent_type):
	'''
	Function to get particular color based on entity type.
	'''
	colors = load_colors()
	return colors[ent_type]

@st.cache
def fetch_response(client, corpus, resource, language= 'en'):
	'''
	Function to fetch response using expert.api APIs.
	'''
	document = client.specific_resource_analysis(
		body={"document": {"text": corpus}}, 
		params={'language': language, 'resource': resource}
	)
	document = json.dumps(document, default=lambda x: x.__dict__)
	document = json.loads(document)

	return document

@st.cache
def fetch_classification_response(client, corpus, language='en'):
	'''
	Function to fetch classification response using API.
	'''
	taxonomy='iptc'
	document = client.classification(body={"document": {"text": corpus}}, params={'taxonomy': taxonomy,'language': language})
	document = json.dumps(document, default=lambda x: x.__dict__)
	document = json.loads(document)

	return document

@st.cache
def beutify_html(html: str, title=False, title_string=""):
	'''
	Function to display border around corpus and result in visualisations. 
	'''
    
	if title:
		WRAPPER = """<div style="border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem"><header><h3 style="text-decoration: underline;">{}<h3></header>{}</div>"""
		html = html.replace("\n", " ")
		return WRAPPER.format(title_string,html)
	else:
		WRAPPER = """<div style="border: 1px solid #e6e9ef; border-radius: 0.25rem; padding: 1rem; margin-bottom: 2.5rem">{}</div>"""
		html = html.replace("\n", " ")
		return WRAPPER.format(html)

@st.cache(allow_output_mutation=True)
def to_df(resp):
	'''
	Function to prepare dataframe from API response used in entity detection and other type analysis. 
	'''
	if resp['_entities']:
		df = pd.DataFrame.from_records(resp['_entities'])
		df = df.explode('_positions')
		df.dropna(inplace=True)
		df.reset_index(inplace=True,drop=True)
		df[['_start','_end']] = df['_positions'].apply(pd.Series)
		del df['_positions']
		df = df.sort_values(by='_start')
		df.reset_index(inplace=True,drop=True)
	else:
		df = None

	if resp['_knowledge']:
		df2 = pd.DataFrame.from_records(resp['_knowledge'])
		df2 = df2.explode('_properties')
		df2.dropna(inplace=True)
		df2.reset_index(inplace=True,drop=True)
		df2[['_type','_value']] = df2['_properties'].apply(pd.Series)
		df2.reset_index(inplace=True,drop=True)
	else:
		df2 = None

	return df, df2

@st.cache
def to_html(df, df2, sentence):
	'''
	Function to generate html code for entity detection visualisations.
	'''

	div1 = '<div class="entities" style="line-height: 2.5; direction: ltr">'
	mark1 = '\n<mark class="entity" style="background:' 
	mark2 = '; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">'
	sp1 = '\n<span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; text-transform: uppercase; vertical-align: middle; margin-left: 0.5rem">'
	e1 = '</span>\n</mark>'
	a1 = '<a style="color:'
	a11 = '; text-decoration:none" target="_blank" href=https://'
	a2 = '</a>'
	
	html = ""

	for i in range(len(df)):

		if df2 is None:
			match = []
		
		else:
			match = df2.loc[(df2['_syncon'] == df['_syncon'][i]) & (df2['_type'] == "DBpediaId"),['_syncon','_value']]

		if len(match) != 0:
			anchor_value = sentence[df['_start'][i]:df['_end'][i]] + "_" +  df['_type'][i]
			if i == 0:
				if df['_start'][i] != 0:
					html += div1 + sentence[0:df['_start'][i]] + mark1 + str(get_color(df['_type'][i])) + mark2 + a1 + anchor_value + a11 + match['_value'].values[0] + '>' + sentence[df['_start'][i]:df['_end'][i]] + a2  + sp1 + df['_type'][i] + e1
				else:
					html += div1 + mark1 + get_color(df['_type'][i]) + mark2 + a1 + anchor_value + a11 + match['_value'].values[0] + '>' + sentence[df['_start'][i]:df['_end'][i]] + a2 + sp1 + df['_type'][i] + e1
			else:
				if df['_start'][i] != df['_end'][i-1]:
					html += sentence[df['_end'][i-1]:df['_start'][i]] + mark1 + get_color(df['_type'][i]) + mark2 + a1 + anchor_value + a11 + match['_value'].values[0] + '>' + sentence[df['_start'][i]:df['_end'][i]]+ a2  + sp1 + df['_type'][i] + e1
				else:
					html += mark1 + get_color(df['_type'][i]) + mark2 + a1 + anchor_value + a11 + match['_value'].values[0] + '>' + sentence[df['_start'][i]:df['_end'][i]] +a2 + sp1 + df['_type'][i] + e1
		else:
			if i == 0:
				if df['_start'][i] != 0:
					html += div1 + sentence[0:df['_start'][i]] + mark1 + str(get_color(df['_type'][i])) + mark2 + sentence[df['_start'][i]:df['_end'][i]] + sp1 + df['_type'][i] + e1
				else:
					html += div1 + mark1 + get_color(df['_type'][i]) + mark2 + sentence[df['_start'][i]:df['_end'][i]] + sp1 + df['_type'][i] + e1
			else:
				if df['_start'][i] != df['_end'][i-1]:
					html += sentence[df['_end'][i-1]:df['_start'][i]] + mark1 + get_color(df['_type'][i]) + mark2 + sentence[df['_start'][i]:df['_end'][i]] + sp1 + df['_type'][i] + e1
				else:
					html += mark1 + get_color(df['_type'][i]) + mark2 + sentence[df['_start'][i]:df['_end'][i]] + sp1 + df['_type'][i] + e1

	if len(sentence) != df.iloc[-1]['_end']:
			html += sentence[df.iloc[-1]['_end'] : len(sentence)]
	html += '</div>'

	return html

def download_file(object_to_download,name):
	'''
	Function to download visualized result to as a .pdf file.
	'''
	try:
		b64 = base64.b64encode(object_to_download.encode()).decode()

	except AttributeError as e:
		b64 = base64.b64encode(object_to_download).decode()

	button_text = 'Save Result'
	button_uuid = str(uuid.uuid4()).replace('-', '')
	button_id = re.sub('\d+', '', button_uuid)

	custom_css = f""" 
		<style>
			#{button_id} {{
				background-color: rgb(255, 255, 255);
				color: rgb(38, 39, 48);
				padding: 0.25em 0.38em;
				position: relative;
				text-decoration: none;
				border-radius: 4px;
				border-width: 1px;
				border-style: solid;
				border-color: rgb(230, 234, 241);
				border-image: initial;
			}} 
			#{button_id}:hover {{
				border-color: rgb(246, 51, 102);
				color: rgb(246, 51, 102);
			}}
			#{button_id}:active {{
				box-shadow: none;
				background-color: rgb(246, 51, 102);
				color: white;
				}}
		</style> """

	dl_link = custom_css + f'<a download="{name}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

	return dl_link


def mask_tag(html, tags, df, sentence):
	'''
	Function to mask selected entities type. 
	'''

	root = LH.fromstring(html)
	for tag in tags:
		elements = root.xpath('//{}'.format('mark'))
		for e in elements:
			pq = PyQuery(e)
			tag2 = pq('span')
			if tag2.text() == tag:
				e.attrib['color'] = get_color(tag)
	for tag in tags: 
		match = df[df['_type'] == tag]
		match.reset_index(inplace=True,drop=True)
		for i in range(len(match)):
			replace_with = sentence[match['_start'][i]:match['_end'][i]]+"_"+match['_type'][i]
			try:
				root = LH.tostring(root).decode("utf-8").replace(replace_with,get_color(tag)+'"')
			except:
				root = root.replace(replace_with,get_color(tag)+'"')

		try:
			root = LH.tostring(root).decode("utf-8").replace(';" color='+'"'+get_color(tag)+'"','; color:'+get_color(tag)+'"')
		except:
			root = root.replace(';" color='+'"'+get_color(tag)+'"','; color:'+get_color(tag)+'"')
	return root


@st.cache
def get_important_sentence(main_sentences, sentence):
	'''
	Function to generate html code for visualisation of important sentence highlighting.
	'''

	html = ''
	div1 = '<div class="entities" style="line-height: 2.5; direction: ltr">'
	mark1 = '\n<mark class="entities" style="background:#92ffaf; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1.3; border-radius: 0.35em;">' 
	e1 = '\n</mark>'

	df = pd.DataFrame.from_records(main_sentences)
	
	df = df.sort_values(by='_start')
	df.reset_index(inplace=True,drop=True)
	for i in range(len(df)):
		
		if i == 0:
			if df['_start'][i] != 0:
				html += div1 + sentence[0:df['_start'][i]] + mark1 + sentence[df['_start'][i]:df['_end'][i]] + e1
			else:
				html = div1 + mark1 + sentence[df['_start'][i]:df['_end'][i]] + e1
		else:
			if df['_start'][i] != df['_end'][i-1]:
				html += sentence[df['_end'][i-1]:df['_start'][i]] + mark1 + sentence[df['_start'][i]:df['_end'][i]] + e1
			else:
				html += mark1 + sentence[df['_start'][i]:df['_end'][i]] + e1

	if len(sentence) != df.iloc[-1]['_end']:
			html += sentence[df.iloc[-1]['_end'] : len(sentence)]

	html += '</div>'
	return html


@st.cache
def get_important_words(main_words, sentence, color):
	'''
	Function to generate visualisation of important lemmas and phrases.
	'''

	df = pd.DataFrame.from_records(main_words)
	df = df.explode('_positions')
	df.dropna(inplace=True)
	df.reset_index(inplace=True,drop=True)
	df[['_start','_end']] = df['_positions'].apply(pd.Series)
	del df['_positions']
	df = df.sort_values(by='_start')
	df.reset_index(inplace=True,drop=True)

	html = ''
	div1 = '<div class="entities" style="line-height: 2.5; direction: ltr">'
	mark1 = '\n<mark class="entities" style="background:'+color+'; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1.3; border-radius: 0.35em;">' 
	e1 = '\n</mark>'

	for i in range(len(df)):
		
		if i == 0:
			if df['_start'][i] != 0:
				html += div1 + sentence[0:df['_start'][i]] + mark1 + sentence[df['_start'][i]:df['_end'][i]] + e1
			else:
				html = div1 + mark1 + sentence[df['_start'][i]:df['_end'][i]] + e1
		else:
			if df['_start'][i] < df['_end'][i-1]:
				pass
			else:
				if df['_start'][i] != df['_end'][i-1]:
					html += sentence[df['_end'][i-1]:df['_start'][i]] + mark1 + sentence[df['_start'][i]:df['_end'][i]] + e1
				else:
					html += mark1 + sentence[df['_start'][i]:df['_end'][i]] + e1

	if len(sentence) != df.iloc[-1]['_end']:
			html += sentence[int(df.iloc[-1]['_end']) : len(sentence)]

	html += '</div>'
	return html


@st.cache
def highlight_tags(tag, df, sentence, color):
	'''
	Function used in tags / classification, which highlights words as per selected tag. 
	'''

	match = df[df['_label'] == tag]
	match.reset_index(inplace=True,drop=True)

	html = ''
	div1 = '<div class="entities" style="line-height: 2.5; direction: ltr">'
	mark1 = '\n<mark class="entities" style="background:'+color+'; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1.3; border-radius: 0.35em;">' 
	e1 = '\n</mark>'

	for i in range(len(match)):
		
		if i == 0:
			if match['_start'][i] != 0:
				html += div1 + sentence[0:match['_start'][i]] + mark1 + sentence[match['_start'][i]:match['_end'][i]] + e1
			else:
				html = div1 + mark1 + sentence[match['_start'][i]:match['_end'][i]] + e1
		else:
			if match['_start'][i] != match['_end'][i-1]:
				html += sentence[match['_end'][i-1]:match['_start'][i]] + mark1 + sentence[match['_start'][i]:match['_end'][i]] + e1
			else:
				html += mark1 + sentence[match['_start'][i]:match['_end'][i]] + e1

	if len(sentence) != match.iloc[-1]['_end']:
			html += sentence[int(match.iloc[-1]['_end']) : len(sentence)]

	html += '</div>'
	return html

def show_corpus(corpus, style):
	'''
	Function to display corpus in every page.
	'''

	tp = '<div class="entities" style="line-height: 2.5; font-weight: bold; direction: ltr">'+corpus+'</div>'
	style = "<style>mark.entity { display: inline-block }</style>"
	st.write(f"{style}{beutify_html(tp)}", unsafe_allow_html=True)

	return tp


def tooltip(value, tip):
	'''
	Function to show toolotip on hover of title.
	'''

	html = """
	<style>
	.tooltip {{
	position: relative;
	display: inline-block;
	
	}}
	.tooltip .tooltiptext {{
	visibility: hidden;
	width: 230%;
	background-color: black;
	color: #fff;
	text-align: center;
	padding: 5px 0;
	border-radius: 6px;
	position: absolute;
	z-index: 1;
	bottom: 100%;
	left: 50%;
	margin-left: -80px;
	font-size: 13px;
	font-weight: bold;
	}}
	.tooltip:hover .tooltiptext {{
	visibility: visible;
	}}
	
	</style>

	<div class="tooltip"><h3>{}</h3>
	<span class="tooltiptext">{}</span>
	</div> """
	return html.format(value, tip)

@st.cache
def category_df(resp, name):
	'''
	Function to preppare dataframe from response for document tagging.
	'''

	df = pd.DataFrame.from_records(resp[name])
	df = df.explode('_positions')
	df.dropna(inplace=True)
	df.reset_index(inplace=True,drop=True)
	df[['_start','_end']] = df['_positions'].apply(pd.Series)
	del df['_positions']
	df = df.sort_values(by='_start')
	df.reset_index(inplace=True,drop=True)
	return df

@st.cache
def generate_sentiment_df(items, df2):
	'''
	Function to prepare dataframe from response of sentiment analysis.
	'''
	
	syncon = []
	sentiment = []

	for item in items:
		if len(df2[df2["_syncon"]==item["_syncon"]]) >0:
			syncon.append(item["_syncon"])
			sentiment.append(item["_sentiment"])
			sub_item = item["_items"]
			for s_item in sub_item:
				if len(df2[df2["_syncon"]==s_item["_syncon"]]) >0:
					syncon.append(s_item["_syncon"])
					sentiment.append(s_item["_sentiment"])
		else:
			sub_item = item["_items"]
			for s_item in sub_item:
				if len(df2[df2["_syncon"]==s_item["_syncon"]]) >0:
					syncon.append(s_item["_syncon"])
					sentiment.append(s_item["_sentiment"])

	df = pd.DataFrame()
	df['_syncon'] = pd.Series(syncon)
	df['_sentiment'] = pd.Series(sentiment)
	df['temp'] = df['_sentiment'].abs()
	df = df.sort_values('temp', ascending=False).drop_duplicates('_syncon').sort_index()
	del df['temp']
	df['color'] = ["#00FF00" if x > 0 else "#FF0000" for x in df['_sentiment']]
	 
	return df

@st.cache
def generate_sentiment_results(df, df2, sentence, overall_score, positive_score, negative_score):
	'''
	Function to generate visualisation for sentiment analysis.
	'''

	div = '<div class="entities" style="line-height: 2.5; direction: ltr">'
	mark = '\n<mark class="entity" style="background:{}; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">{}\n<span style="font-size: 0.8em; font-weight: bold; line-height: 1; border-radius: 0.35em; text-transform: uppercase; vertical-align: middle; margin-left: 0.5rem">{}</span>\n</mark>'
	
	html = ""

	html += div + mark.format("#ffbf00", "Overall Score", overall_score)
	html += mark.format("#00FF00", "Positive Score", positive_score)
	html += mark.format("#FF0000", "Negative Score", negative_score)
	html += '</div>'
	div1 = '<div class="entities" style="line-height: 2.5; direction: ltr">'
	mark1 = '\n<mark class="entity" style="background:{}; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1; border-radius: 0.35em;">{}\n</mark>'
	html2 = ""
	df3 = df.merge(df2, on='_syncon', how='inner', suffixes=('_1', '_2'))
	df3 = df3.sort_values(by='_start')
	df3.reset_index(inplace=True,drop=True)
	if len(df3) > 0:
		for i in range(len(df3)):

			if i == 0:
				if df3['_start'][i] != 0:
					html2 += div1 + sentence[0:df3['_start'][i]]+ mark1.format(df3['color'][i], sentence[df3['_start'][i]:df3['_end'][i]])
				else:
					html2 += div1 + mark1.format(df3['color'][i], sentence[df3['_start'][i]:df3['_end'][i]])
			else:
				if df3['_start'][i] != df3['_end'][i-1]:
					html2 += sentence[df3['_end'][i-1]:df3['_start'][i]] + mark1.format(df3['color'][i], sentence[df3['_start'][i]:df3['_end'][i]])
				else:
					html2 += mark1.format(df3['color'][i], sentence[df3['_start'][i]:df3['_end'][i]])

		if len(sentence) != df3.iloc[-1]['_end']:
				html2 += sentence[int(df3.iloc[-1]['_end']) : len(sentence)]

		html2 += '</div>'
	return html, html2	

@st.cache
def read_text_flie(doc_obj):

	bytes_data = doc_obj.read()

	encoding='utf-8'
	s=str(bytes_data,encoding)

	all_line = ""

	data = StringIO(s)
	for line in data:
        	all_line+= line

	return all_line

@st.cache
def read_pdf(doc_obj):
	try:
		with pdfplumber.open(doc_obj) as pdf:
			all_pages = pdf.pages

		page_count = len(pdf.pages)
		print('len of pdf ',page_count)
		all_page_text = ""
		for i in range(page_count):
			page = pdf.pages[i]
			all_page_text+=page.extract_text()
		
		return all_page_text
		
	except:
		st.write("None")

@st.cache
def check_language(text):
	return langid.classify(text)[0]
