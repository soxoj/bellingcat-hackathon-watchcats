import re
import random
from itertools import chain
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from components import *

DISPLAY_DATE_SLIDER = False


if __name__ == '__main__':
	st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-fork-ribbon-css/0.2.3/gh-fork-ribbon.min.css" />', unsafe_allow_html=True)
	st.markdown('<style>.github-fork-ribbon{ position:fixed; z-index:1000000 }; .github-fork-ribbon:before{ background-color: #090; }</style>', unsafe_allow_html=True)
	st.markdown('<a class="github-fork-ribbon left-top" href="https://github.com/soxoj/bellingcat-hackathon-watchcats" data-ribbon="Fork me on GitHub" title="Fork me on GitHub">Fork me on GitHub</a>', unsafe_allow_html=True)

	st.title(":bar_chart: Adana")

	st.markdown(body="### 1-click analytical dashboard for OSINT researchers")

	df = None
	datasets_count = 1
	if st.button('Test example (Bellingcat 2023)', type="primary"):
		df = pd.read_csv('data/Bellingcat.csv')

	if df is None:
		st.markdown(body="""Run test of example dataset analysis OR upload datasets (**you can use several**) of posts. """)

		with st.expander("Read more about Adana"):
			st.markdown("Adana means 'Analytical DAshboard (for NArratives)'.")
			st.markdown("Currently Twitter is only supported: Zeeschuimer (Twitter API ndjson) and CSV format")
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
				datasets_count += 1
				df = df.reset_index()

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

	start_datetime = datetime.fromtimestamp(df['timestamp_utc'].min())
	end_datetime = datetime.fromtimestamp(df['timestamp_utc'].max())

	status = [
		f"Uploaded {datasets_count} dataset{'s' if datasets_count > 1 else ''}, {len(df.index)} rows.",
		f"Start date is {start_datetime}, end date is {end_datetime}"
	]
	st.markdown('\n'.join(status))

	if DISPLAY_DATE_SLIDER:
		cols1, _ = st.columns((1,1))
		max_days = end_datetime - start_datetime
		slider = cols1.slider('Select date', min_value=start_datetime, value=(start_datetime, end_datetime), max_value=end_datetime)

	st.header(f"Distribution of tweets by time")
	timeseries = tweetdf_to_timeseries(df,frequency="1H")
	timeseries_plot = plot_timeseries(timeseries)
	st.altair_chart(timeseries_plot, use_container_width=True)

	df['hashtags_list'] = df['text'].apply(extract_hashtags)

	hashtags = list(chain.from_iterable(df['hashtags_list'].to_list()))
	hashtags = list(sorted(hashtags))

	topics = extract_topics(df, flat_list=hashtags)
	topics_sorted = sorted(topics.items(), key=lambda x: x[1], reverse=True)
	top_topics = topics_sorted[:5]

	# https://github.com/ArnelMalubay/Twitter-WordCloud-Generator-using-Streamlit/blob/main/app.py
	wordcloud = WordCloud(background_color="white", collocations=False).generate(' '.join(hashtags))
	fig = plt.figure()
	plt.imshow(wordcloud)
	plt.axis("off")
	st.header(f"Wordcloud of hashtags")
	st.markdown("Detect the most used hashtag in a dataset.")
	st.pyplot(fig)

	st.header(f"Top-5 hashtags")
	st.markdown(f"""`First Tweet URL` means first appearance of a hashtag in a dataset. `Most Active User URL` means a
		link to username of account wrote the biggest amounts of tweet with a hashtag.""")

	@st.cache_data
	def get_first_tweets_most_active_users(df, top_topics):
		first_tweets = []
		most_active_users = []
		for topic, _ in top_topics:
			with_hashtags = df[df.apply(lambda x: topic in x['hashtags_list'], axis=1)]
			first_tweet = with_hashtags.sort_values(by="timestamp_utc")[:1]
			most_active = with_hashtags.groupby(with_hashtags['author_url']).size().sort_values(ascending=False)[:1]
			first_tweets.append(first_tweet['url'].values[0])
			most_active_users.append(most_active.index.values[0])

		return first_tweets, most_active_users

	first_tweets, most_active_users = get_first_tweets_most_active_users(df, top_topics)
	hashtags_df = pd.DataFrame(topics_sorted[:5])
	hashtags_df['first_url'] = first_tweets
	hashtags_df['most_active_user_url'] = most_active_users
	# TODO: most active accounts?
	hashtags_df.columns = ['Hashtag', 'Count', 'First Tweet URL', 'Most Active User URL']

	st.dataframe(
		hashtags_df,
		column_config={
			"hashtag": st.column_config.Column("Hashtag"),
			"count": st.column_config.Column("Count"),
			"first_url": st.column_config.LinkColumn(),
			"most_active_user_url": st.column_config.LinkColumn(),
		},
		hide_index=True
	)

	st.header(f"Dataframe explorer")
	st.markdown("You can search in dataset and download it (buttons in the top right corner of the table).")
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

	st.header(f"Topics and sentiments experimental stuff")
	st.markdown(f"**Warning!** This is random data for testing purposes.")
	s_df = pd.DataFrame(columns=['sentiment', 'topic'])

	s_df['sentiment'] = np.random.randint(-10, 20, df.shape[0])
	topics = ['putin', 'ukraine', 'russia', 'israel']
	s_df['topic'] = np.random.choice(topics, df.shape[0])

	topics = s_df['topic'].unique()
	s_df['datetime'] = df['datetime']

	topics_df = pd.DataFrame(columns=['sentiment', 'topic', 'datetime'])
	for topic in topics:
		new_df = s_df[s_df['topic'] == topic].groupby(s_df['datetime'].dt.month).agg({'sentiment': 'mean', 'datetime': 'min'})
		new_df['topic'] = topic
		# st.dataframe(new_df)

		topics_df = pd.concat([topics_df, new_df])

	topics_df = topics_df.reset_index()
	st.dataframe(topics_df)
	st.line_chart(topics_df, x="datetime", y="sentiment", color='topic')
