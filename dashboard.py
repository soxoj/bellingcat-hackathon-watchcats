import re
from itertools import chain
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from components import *

if __name__ == '__main__':
	st.title(":bar_chart: Adana")

	st.markdown(body="### 1-click analytical dashboard for OSINT researchers")

	df = None
	if st.button('Test example (Bellingcat 2023)', type="primary"):
		df = pd.read_csv('data/Bellingcat.csv')

	if df is None:
		st.markdown(body="""Run test of example dataset analysis OR upload datasets (**you can use several**) of posts. """)

		with st.expander("Read more about Adana"):
			st.markdown("Adana means Analytical DAshboard (for NArratives).")
			st.markdown("Currently Twitter is only supported.")
			st.markdown("Remind you that results of analysis depends on the quality of dataset.")
			st.markdown("Read [here](https://docs.google.com/document/d/10xOgmZmvLM-BJeak-KNXzkx7H5oqnbn834-o94WbM50/edit#heading=h.1037l5l116z1) how to prepare new datasets.")

		uploaded_files = st.file_uploader("Choose a dataset file", accept_multiple_files=True)

		st.markdown(body="*[Download datasets examples here](https://drive.google.com/drive/u/0/folders/1GtUZkfD0cZ2xBBZ3FiDpH1Cgw_u-m1wh)*")
		if not len(uploaded_files):
			st.stop()

		for i in range(len(uploaded_files)):
			if df is None:
				df = input_file_to_dataframe(uploaded_files[i])
			else:
				df = pd.concat([df, input_file_to_dataframe(uploaded_files[i])])

	def extract_hashtags(text):
		hashtags_list = []
		hashtags = re.findall( r'#[a-zA-Z_-]+', text)
		for h in hashtags:
			hashtags_list.append(h[1:])
		return hashtags_list

	st.markdown(body="Refresh page or open new one for another dataset analysis")

	if not 'timestamp_utc' in df:
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
	st.header(f"Wordcloud of hashtags")
	st.pyplot(fig)

	st.header(f"Top-5 hashtags")
	first_tweets = []
	for topic, _ in top_topics:
		first_tweet = df[df.apply(lambda x: topic in x['hashtags_list'], axis=1)].sort_values(by="timestamp_utc")[:1]
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
	new_df = df

	drop_fields = ['EntityID','EntityType', 'id', 'author_id', 'video_duration', 'video_url', 'icon-url']
	for field in drop_fields:
		if field in df:
			new_df = new_df.drop(field, axis='columns')

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