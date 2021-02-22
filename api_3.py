import streamlit as st
from streamlit_agraph import agraph, TripleStore, Node, Edge, Config
import json

from utils import fetch_response
from utils import show_corpus
from utils import tooltip

def relation_identification(client, corpus, style, tooltip_dict, language):
    '''
	Function for relation identification visualisation.
	'''

    show_corpus(corpus, style)
    st.write("")
    tooltip_resp = tooltip("Relation Analysis", tooltip_dict["Relation Analysis"])
    st.markdown(tooltip_resp, unsafe_allow_html=True)

    document = fetch_response(client, corpus, 'relations', language)
    
    try:

        data = document['_relations']
        
        main = TripleStore()
        pic = "http://www.clker.com/cliparts/s/3/o/c/8/M/glossy-black-icon-angle-hi.png"
        
        for rel in data:
            node1 = rel["_verb"]["_text"]
            related = rel["_related"]
            for rel2 in related:
                link = rel2["_relation"]
                node2 = rel2["_text"]
                main.add_triple(node1, link, node2, picture=pic)

        config = Config(width=800, 
                    height=800, 
                    directed=True,
                    nodeHighlightBehavior=True, 
                    highlightColor="#F7A7A6",
                    collapsible=True,
                    node={'labelProperty':'label'},
                    link={'labelProperty': 'label', 'renderLabel': True}
                    ) 

        agraph(list(main.getNodes()), (main.getEdges()), config=config)

        st.write(" ")
        st.write("API used to get these results [docs](https://docs.expert.ai/nlapi/latest/guide/relation-extraction/)")

    except Exception as e:
        st.warning("There's no relation in input sentence.")
