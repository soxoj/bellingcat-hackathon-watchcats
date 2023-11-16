import json
import altair as alt
import numpy as np
import pandas as pd
from wordcloud import WordCloud
from collections import Counter

def input_file_to_dataframe(uploaded_file):
    # zeeschuimer support
    if uploaded_file.name.endswith("ndjson"):
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
        f = uploaded_file

        while True:
            line = f.readline()
            if not line:
                break

            structure = json.loads(line)
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
            new_row = {
                'timestamp_utc': int(structure['timestamp_collected'])/1000,
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

        f.close()

        return df
    else:
        return pd.read_csv(uploaded_file)


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
    if "collected_via" in dfc.columns and dfc['collected_via'].isna().sum() > 0:
        dfc = dfc[dfc['collected_via'].isna()]
    dfc['type'] = dfc.apply(lambda row: find_out_tweet_type(row), axis=1)
    dfc['ts_dt'] = pd.to_datetime(dfc['timestamp_utc'], unit= 's')    
    dfc = dfc.set_index("ts_dt")
    grouper = dfc.groupby([pd.Grouper(freq=frequency), 'type'])
    result = grouper['type'].count().unstack('type').fillna(0)
    existing_tweettypes = list(result.columns)
    result['total'] = 0
    for tweettype in existing_tweettypes:
        result['total'] += result[tweettype]
    return result

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
