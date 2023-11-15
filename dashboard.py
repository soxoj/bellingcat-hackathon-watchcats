import re
from itertools import chain
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from components import *

if __name__ == '__main__':
	st.title("Adana: Analytical DAshboard (for NArratives)")

	st.markdown(body="""Upload a dataset of posts (currently Twitter only supported). Remind you that results of analysis depends on the
		quality of dataset. Read [here](https://docs.google.com/document/d/10xOgmZmvLM-BJeak-KNXzkx7H5oqnbn834-o94WbM50/edit#heading=h.1037l5l116z1)
		how to prepare new datasets.""")

	st.markdown(body="**[Download datasets examples here](https://drive.google.com/drive/u/0/folders/1GtUZkfD0cZ2xBBZ3FiDpH1Cgw_u-m1wh)**")

	uploaded_file = st.file_uploader("Choose a dataset file")
	if uploaded_file is not None:
		df = pd.read_csv(uploaded_file)

		def extract_hashtags(text):
			hashtags_list = []
			hashtags = re.findall( r'#[a-zA-Z_-]+', text)
			for h in hashtags:
				hashtags_list.append(h[1:])
			return hashtags_list

		df["datetime"] = pd.to_datetime(df["c_date"])
		df['timestamp_utc'] = df['c_date'].apply(lambda x: datetime.strptime(x, '%d.%m.%Y %H:%M:%S').timestamp())

		st.header(f"Distribution of tweets by time")
		timeseries = tweetdf_to_timeseries(df,frequency="1H")
		timeseries_plot = plot_timeseries(timeseries)
		st.altair_chart(timeseries_plot, use_container_width=True)

		df['hashtags_list'] = df['text'].apply(extract_hashtags)

		hashtags = list(chain.from_iterable(df['hashtags_list'].to_list()))
		hashtags = list(sorted(hashtags))

		topics = detect_initiator(df, flat_list=hashtags)
		topics_sorted = sorted(topics.items(), key=lambda x: x[1], reverse=True)
		top_topics = topics_sorted[:5]

		# https://github.com/ArnelMalubay/Twitter-WordCloud-Generator-using-Streamlit/blob/main/app.py
		wordcloud = WordCloud(background_color="white", collocations=False).generate(' '.join(hashtags))
		fig = plt.figure()
		plt.imshow(wordcloud)
		plt.axis("off")
		st.header(f"Wordcloud of tweets")
		st.pyplot(fig)

		st.header(f"Top-5 hashtags")
		first_tweets = []
		for topic, _ in top_topics:
			print(topic)
			first_tweet = df[df.apply(lambda x: topic in x['hashtags_list'], axis=1)].sort_values(by="datetime")[:1]
			print(first_tweet)
			first_tweets.append(first_tweet['url'].values[0])

		hashtags_df = pd.DataFrame(topics_sorted[:5])
		hashtags_df['first_url'] = first_tweets
		hashtags_df.columns = ['Hashtag', 'Count', 'First Tweet URL']

		st.dataframe(
			hashtags_df,
			column_config={
				"first_url": st.column_config.LinkColumn("First Tweet URL"),
			}
		)

		st.header(f"Dataframe explorer")
		new_df = df.drop(['EntityID','EntityType', 'id', 'author_id', 'video_duration', 'video_url', 'icon-url'], axis='columns')
		st.dataframe(
			new_df,
			column_config={
				"author_name": st.column_config.Column("Name"),
				"author_alias": st.column_config.Column("Alias"),
				"url": st.column_config.LinkColumn("Tweet URL"),
				"author_image": st.column_config.ImageColumn(
						"Profile Picture", help="Profile picture preview"
				),
				"author_url": st.column_config.LinkColumn("Author URL"),
			},
		)