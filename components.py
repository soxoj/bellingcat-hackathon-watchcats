import json
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter
from datetime import datetime

@st.cache_data
def read_data_cached(filename):
    return pd.read_csv(filename)

def process_ndjson_file(f):
    df = pd.DataFrame(columns=[
        'timestamp_utc',
        'collected_via',
        'c_date',
        'text',
        'lang',
        'type',
        'url',
        "author_name",
        "author_alias",
        "author_image",
        "author_url",
    ])
    while True:
        line = f.readline()
        if not line:
            break

        print(line)
        structure = json.loads(line.strip())
        if not 'data' in structure:
            continue

        if not '__typename' in structure['data']:
            continue

        entity_type = structure['data']['__typename']
        if entity_type != 'Tweet':
            continue

        data = structure['data']
        tweet_id = structure["item_id"]
        username = data['core']['user_results']['result']['legacy']['screen_name']
        timestamp = int(structure['timestamp_collected'])/1000
        new_row = {
            'timestamp_utc': timestamp,
            # 'datetime': datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M:%S'),
            'collected_via':'zeeschuimer',
            'c_date': data['legacy']['created_at'],
            'text': data['legacy']['full_text'],
            'lang': data['legacy']['lang'],
            'type': 'Post' if not data['legacy']['retweeted'] else 'retweet',
            'url': f'https://twitter.com/{username}/status/{tweet_id}',
            "author_name": data['core']['user_results']['result']['legacy']['name'],
            "author_alias": username,
            "author_image": data['core']['user_results']['result']['legacy']['profile_image_url_https'],
            "author_url": f"https://twitter.com/{data['core']['user_results']['result']['legacy']['screen_name']}"
        }
        df.loc[len(df)] = new_row
    return df

def input_file_to_dataframe(uploaded_file):
    # zeeschuimer support
    if uploaded_file.name.endswith("ndjson"):
        df = process_ndjson_file(uploaded_file)
        uploaded_file.close()

        return df
    else:
        return read_data_cached(uploaded_file)


def find_out_tweet_type(row):
    if not 'type' in row:
        return 'regulartweet'
    else:
        return row['type']

def extract_topics(df, size=5, topic_field='hashtags_list', flat_list=[]):
    if not flat_list:
        topics = list(chain.from_iterable(df[topic_field].to_list()))
        flat_list = list(sorted(topics))

    counted_topics = Counter(flat_list)

    return counted_topics

# https://github.com/pournaki/twitter-explorer/blob/0b8bc766d174c3854467ea1e7280f71d74ba7276/twitterexplorer/plotting.py#L41
def tweetdf_to_timeseries(df,frequency='1H'):
    dfc = df.copy()
    ## don't plot the referenced tweets, they might go back centuries!
    # if "collected_via" in dfc.columns and dfc['collected_via'].isna().sum() > 0:
    #     dfc = dfc[dfc['collected_via'].isna()]
    dfc['type'] = dfc.apply(lambda row: find_out_tweet_type(row), axis=1)
    dfc['ts_dt'] = pd.to_datetime(dfc['timestamp_utc'], unit= 's')    
    dfc = dfc.set_index("ts_dt")
    group_by = st.session_state["group_by"]

    if group_by == "total":
        return dfc.groupby(pd.Grouper(freq=frequency)).size()

    # if group_by == "hashtags":
    #     dfc = dfc.explode('hashtags_list')
    #     group_by = 'hashtags_list'
    #     # st.write("dfc.columns", dfc.columns)
    #     return dfc.groupby([pd.Grouper(freq=frequency), group_by, "EntityID"]).size().unstack([group_by]).unstack(["EntityID"]).fillna(0)
    #     # grouper = dfc.groupby([pd.Grouper(freq=frequency), group_by, "EntityID"])
    #     # result = grouper[group_by].size()
    #     # return result

    grouper = dfc.groupby([pd.Grouper(freq=frequency), group_by])
    result = grouper[group_by].count().unstack(group_by).fillna(0)
    existing_tweettypes = list(result.columns)
    # result['total'] = 0
    # for tweettype in existing_tweettypes:
    #     result['total'] += result[tweettype]
    return result

# zhttps://github.com/pournaki/twitter-explorer/blob/0b8bc766d174c3854467ea1e7280f71d74ba7276/twitterexplorer/plotting.py#L25
def plot_timeseries(grouped_tweetdf):
    
    grouped_tweetdf["datetime"] = grouped_tweetdf.index

    # get the right order for color plotting
    types = list(grouped_tweetdf.columns)[:-2]
    counts = []
    for t in types:
        counts.append(grouped_tweetdf[t].sum())
    order_idx = np.array(counts).argsort()[::-1]
    order = [types[i] for i in order_idx]

    # set color range
    domain = order.copy()
    domain.append('total')
    range_ = ['#005AB5','#DC3220','#009E73','#ff7f0e','grey']
    
    # plot 
    C1 = alt.Chart(grouped_tweetdf).mark_area(opacity=0.6).transform_fold(
        fold=order,
        as_=['variable', 'value']
    ).encode(
        alt.X('datetime:T', timeUnit='yearmonthdatehours', title="date"),
        alt.Y('value:Q', stack=None, title="tweet count (hourly)"),
        color=alt.Color("variable:N",
                        legend=alt.Legend(title="tweet type"),
                        scale=alt.Scale(domain=domain, range=range_),
                         )
    )

    # plot total in background    
    C2 = alt.Chart(grouped_tweetdf).mark_area(opacity=0.15).encode(
        alt.X(f'datetime:T', timeUnit='yearmonthdatehours', title='date'),
        alt.Y('total:Q'),
        color=alt.value("black"))

    return (C1+C2).configure_axis(
    labelFontSize=12,
    titleFontSize=12,
).configure_legend(titleFontSize=12,labelFontSize=12)

def colored_sentiment_plot(df):
    topic_count = {}
    topic_sentiment = {}
    for _, tweet in df.iterrows():
        topic = tweet['topic']
        sentiment = tweet['sentiment']
        topic_count[topic] = topic_count.get(topic, 0) + 1
        topic_sentiment[topic] = topic_sentiment.get(topic, 0) + sentiment

    # Identify topics with only one tweet
    single_tweet_topics = [topic for topic, count in topic_count.items() if count == 1]

    # Reassign these topics to 'Other'
    for topic in single_tweet_topics:
        topic_sentiment['Other'] = topic_sentiment.get('Other', 0) + topic_sentiment.pop(topic)
        topic_count['Other'] = topic_count.get('Other', 0) + topic_count.pop(topic)

    # Calculate average sentiment for each topic
    for topic in topic_sentiment:
        topic_sentiment[topic] /= topic_count[topic]

    # Preparing data for plotting
    topics = sorted(list(topic_count.keys()), key=lambda x: topic_count[x], reverse=True)
    counts = [topic_count[topic] for topic in topics]
    avg_sentiments = [topic_sentiment[topic] for topic in topics]

    # Normalize sentiment values for coloring (from -10..10 to 0..1)
    normalized_sentiments = [(sent + 10) / 20 for sent in avg_sentiments]

    # Color mapping: red (-10) to yellow (0) to green (10)
    colors = [(1 - sentiment, sentiment, 0) for sentiment in normalized_sentiments]

    # Creating the horizontal bar plot
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(topics, counts, color=colors)

    # Rotate y-axis labels (if needed)
    plt.yticks(rotation=0)

    # Adding color gradient bar for reference
    sm = plt.cm.ScalarMappable(cmap=plt.cm.RdYlGn, norm=plt.Normalize(vmin=-10, vmax=10))
    sm.set_array([])
    # cbar = plt.colorbar(sm, ax=ax, orientation='vertical')
    # cbar.set_label('Average Sentiment')

    plt.ylabel('Topics')
    plt.xlabel('Number of Tweets')
    plt.title('Number of Tweets per Topic with Average Sentiment')
    #plt.show()
    return fig
