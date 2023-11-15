import re
from itertools import chain
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from components import *

if __name__ == '__main__':
	st.title("Adana: Analytical DAshboard for NArratives")

	uploaded_file = st.file_uploader("Choose a dataset file")
	if uploaded_file is not None:
		df = pd.read_csv(uploaded_file)

		def extract_hashtags(text):
			hashtags_list = []
			hashtags = re.findall( r'#[a-zA-Z_-]+', text)
			for h in hashtags:
				hashtags_list.append(h[1:])
			return hashtags_list

		df['timestamp_utc'] = df['c_date'].apply(lambda x: datetime.strptime(x, '%d.%m.%Y %H:%M:%S').timestamp())

		st.header(f"Distribution of tweets by time")
		timeseries = tweetdf_to_timeseries(df,frequency="1H")
		timeseries_plot = plot_timeseries(timeseries)
		st.altair_chart(timeseries_plot, use_container_width=True)

		df['hashtags_list'] = df['text'].apply(extract_hashtags)

		hashtags = list(chain.from_iterable(df['hashtags_list'].to_list()))
		hashtags = list(sorted(hashtags))

		# https://github.com/ArnelMalubay/Twitter-WordCloud-Generator-using-Streamlit/blob/main/app.py
		wordcloud = WordCloud(background_color="white", collocations=False).generate(' '.join(hashtags))
		fig = plt.figure()
		plt.imshow(wordcloud)
		plt.axis("off")
		st.header(f"Wordcloud of tweets")
		st.pyplot(fig)
