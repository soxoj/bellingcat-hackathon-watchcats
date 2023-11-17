# Adana: Analytical DAshboard (for NArratives)

📊 1-click analytical dashboard for OSINT researchers

####  👉 [Try Adana online](https://bellingcat-hackathon-watchcats-uearyc7iggn84xznppgq5k.streamlit.app/)

## The idea

Analytical tool to extract insights (shown on a simple dashboard) from social media posts about narratives, sentiments, initiators, influencers and clusters of accounts.
It should be applicable for studying disinformation campaigns, analysing public opinion, and assessing risks related to some topics.

It's a project created by team Watch Cats during participation in [Bellingcat's First In-person Hackathon](https://www.bellingcat.com/bellingcats-first-in-person-hackathon/). 

Inspired by [4CAT](https://4cat.nl/) and [twitter explorer](https://twitterexplorer.org/).
The development process is documented in [this Google document](https://docs.google.com/document/d/10xOgmZmvLM-BJeak-KNXzkx7H5oqnbn834-o94WbM50/edit#heading=h.m0d3jrsts18t).

# MVP

Available by the link: https://bellingcat-hackathon-watchcats-uearyc7iggn84xznppgq5k.streamlit.app/

<p align="center">
  <img src="https://github.com/soxoj/bellingcat-hackathon-watchcats/assets/31013580/f1d86b94-f439-427e-81de-b0f8c88465c1" height="800" />
</p>

## Team members

**[@soxoj](https://soxoj.com/)**, **[@dizvyagintsev](https://github.com/dizvyagintsev)**

## Datasets

[Twitter posts on various topics (1-20K)](https://drive.google.com/drive/u/0/folders/1GtUZkfD0cZ2xBBZ3FiDpH1Cgw_u-m1wh)

Instructions:
- [How to prepare dataset with Zeeschuimer](https://docs.google.com/document/d/19MAiqX7Vx1FcNJ44K-vSdnKDVC5gcFwtrSQiewnwW8A/edit)
- [How to prepare CSV dataset](https://docs.google.com/document/d/1TTulgfIhSEZRQODRem9ufJWXZ7tGJdHEVYSVk8Teit4/edit)
- Check utils/cluster_n_sentiments.ipynb for instructions on how to enrich datasets with sentiments and topics

## Installation

For local installation you need Python and pip installed.
```sh
pip install -r requirements.txt
streamlit run dashboard.py
```

For private cloud installation, you need:
1. Login (register) to GitHub
2. Fork [this repository](https://github.com/soxoj/bellingcat-hackathon-watchcats/fork)
3. Login (register) in [Streamlit](https://streamlit.io/) by GitHub account
4. Create a new project in Streamlit from a forked repository
5. Deploy (*no payment method required!*)
6. Voila!

## Utils

`utils` folder contains:
- CSV tweet datasets formatter (to Twitwi)
- `cluster_n_sentiments.ipynb`: ML stuff (enrichment of datasets with sentiments and topics)

## Some other results

An example of a hashtag network built with [Twitter Explorer](https://twitterexplorer.org/) using one of the datasets

<img width="958" alt="HashtagNetwork" src="https://github.com/soxoj/bellingcat-hackathon-watchcats/assets/31013580/6327e7dd-ceb1-4f26-a5b4-6961dae5957b">

