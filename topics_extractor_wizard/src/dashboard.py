import os
import time
from multiprocessing import Pool

import pandas as pd
import streamlit as st

st.set_page_config(layout="wide", page_title="Topic Modeling Wizard")
from stqdm import stqdm  # noqa
import plotly.express as px

from utils import show_top_tweets_by_len, detect_no_fail, continue_button # noqa

if __name__ == "__main__":
    with st.sidebar:
        st.number_input("Number of processes used for parallelization: ", value=(os.cpu_count() - 1), key="processes")
        st.write(st.session_state)

    st.markdown("## Wizard for extracting topics from social media captions")

    st.markdown("### 1. Upload your data")

    csv = st.file_uploader("Upload your data as a CSV file with text column", type="csv", key="csv")
    if not csv:
        st.stop()

    old_file_id, new_file_id = st.session_state.get("file_id", None), csv.file_id
    if old_file_id != new_file_id:
        print("New file uploaded")
        st.session_state.file_id = new_file_id
        df = pd.read_csv(csv)
        st.session_state.df = df

    # st.write(st.session_state.df.columns)

    st.write(f"Number of social media captions to process: {st.session_state.df.shape[0]}")

    st.session_state.df["text_length"] = st.session_state.df["text"].str.len()
    st.session_state.df = st.session_state.df.sort_values(by="text_length", ascending=False)

    show_top_tweets_by_len(st.session_state.df)

    if not st.session_state.get("step2", False):
        continue_button()

    st.write("---")

    st.session_state.step2 = True
    st.markdown("### 2. Filter data")

    st.write("---")

    st.session_state.step2 = True
    st.markdown("### 2. Filter data by language")
    stqdm.pandas()

    # st.write(st.session_state.df.columns)

    if "language" not in st.session_state.df.columns:
        with st.spinner("Detecting languages..."):
            t = time.monotonic_ns()
            with Pool(st.session_state.processes) as pool:
                languages = list(
                    stqdm( # noqa
                        pool.imap(detect_no_fail, st.session_state.df["text"].to_list()),
                        total=st.session_state.df.shape[0]
                    )
                )
            st.session_state.df["language"] = languages
        st.write(
            f"Languages detected in {int((time.monotonic_ns() - t) / 1e9)} seconds. "
            f"{st.session_state.df['language'].unique().shape[0]} language(s) detected"
        )

    languages = sorted(st.session_state.df["language"].unique())
    selected_languages = st.multiselect(
        "Select languages to keep",
        options=languages,
        default=languages,
    )

    st.session_state.df_languages_filtered = st.session_state.df[
        st.session_state.df["language"].isin(selected_languages)
    ]
    st.write(f"Number of social media captions to process: {st.session_state.df_languages_filtered.shape[0]}")
    language_counts = st.session_state.df_languages_filtered['language'].value_counts().reset_index()
    language_counts.columns = ['language', 'count']
    fig = px.bar(language_counts, x='count', y='language', orientation='h')
    st.plotly_chart(fig)

    if not st.session_state.get("step3", False):
        continue_button()

    st.write("---")

    st.session_state.step3 = True
    st.markdown("### 3. Clustering social media captions")
    st.warning("Not implemented yet")

