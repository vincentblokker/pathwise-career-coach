import os
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI

load_dotenv()

st.title("LangChain Playground")

llm = ChatOpenAI(model="gpt-4o-mini")

prompt = st.text_input("Vraag", "Leg quantumfysica uit alsof ik 10 ben")

if st.button("Run"):
    res = llm.invoke(prompt)
    st.write(res.content)