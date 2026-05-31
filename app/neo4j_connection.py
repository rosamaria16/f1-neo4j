import os
from neo4j import GraphDatabase
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

try:
    URI = st.secrets.get("NEO4J_URI", os.getenv("NEO4J_URI"))
    USER = st.secrets.get("NEO4J_USER", os.getenv("NEO4J_USER"))
    PASSWORD = st.secrets.get("NEO4J_PASSWORD", os.getenv("NEO4J_PASSWORD"))
except:
    URI = os.getenv("NEO4J_URI")
    USER = os.getenv("NEO4J_USER")
    PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def get_session():
    return driver.session()