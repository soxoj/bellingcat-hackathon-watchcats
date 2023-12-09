import pandas as pd
import streamlit as st
import pycountry
from langdetect import detect, LangDetectException


def show_top_tweets_by_len(df: pd.DataFrame):
    top_tweets_by_length = df["text"].iloc[:10].to_list()

    with st.expander("Show top 10 tweets by length"):
        for tweet in top_tweets_by_length:
            st.write(tweet)
            st.write("---")

def detect_no_fail(text):
    try:
        return pycountry.languages.get(alpha_2=detect(text)).name
    except (LangDetectException, AttributeError):
        return "Not detected"


def continue_button():
    placeholder = st.empty()
    if not placeholder.button("Continue"):
        st.stop()
    placeholder.empty()
