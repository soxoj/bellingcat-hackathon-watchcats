# Adana: Analytical DAshboard (for NArratives)

Analytical tool to extract insights (shown on a simple dashboard) from social media posts about narratives, sentiments, initiators, influencers and clusters of accounts.
It should be applicable for studying disinformation campaigns, analysing public opinion, and assessing risks related to some topics.

## The idea

https://docs.google.com/document/d/10xOgmZmvLM-BJeak-KNXzkx7H5oqnbn834-o94WbM50/edit#heading=h.m0d3jrsts18t

# MVP

Available by the link: https://bellingcat-hackathon-watchcats-uearyc7iggn84xznppgq5k.streamlit.app/

<img src="https://github.com/soxoj/bellingcat-hackathon-watchcats/assets/31013580/f1d86b94-f439-427e-81de-b0f8c88465c1" height="800" />

For testing purposes use [these datasets](https://drive.google.com/drive/u/0/folders/1GtUZkfD0cZ2xBBZ3FiDpH1Cgw_u-m1wh) or prepare new by instructions from [this document](https://docs.google.com/document/d/10xOgmZmvLM-BJeak-KNXzkx7H5oqnbn834-o94WbM50/edit#heading=h.1037l5l116z1)

## Participants

@soxoj, @dizvyagintsev

## Datasets

Twitter posts on various topics (1-20K): https://drive.google.com/drive/u/0/folders/1GtUZkfD0cZ2xBBZ3FiDpH1Cgw_u-m1wh

## Dataset converter tool

Maltego export to Twitwi format:

```sh
python3 Maltego_To_TwitiCSV_Converter.py input.csv output.csv
```

## Some other results

An example of a hashtag network built with [Twitter Explorer](https://twitterexplorer.org/) using one of the datasets

<img width="958" alt="HashtagNetwork" src="https://github.com/soxoj/bellingcat-hackathon-watchcats/assets/31013580/6327e7dd-ceb1-4f26-a5b4-6961dae5957b">

