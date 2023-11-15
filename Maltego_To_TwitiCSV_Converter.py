#!/usr/bin/python3

import re
import csv
import sys
import json
import time
import datetime

TWITWI_CSV_FIELDS = "id,timestamp_utc,local_time,user_screen_name,text,possibly_sensitive,retweet_count,like_count,reply_count,impression_count,lang,to_username,to_userid,to_tweetid,source_name,source_url,user_location,lat,lng,user_id,user_name,user_verified,user_description,user_url,user_image,user_tweets,user_followers,user_friends,user_likes,user_lists,user_created_at,user_timestamp_utc,collected_via,match_query,retweeted_id,retweeted_user,retweeted_user_id,retweeted_timestamp_utc,quoted_id,quoted_user,quoted_user_id,quoted_timestamp_utc,collection_time,url,place_country_code,place_name,place_type,place_coordinates,links,domains,media_urls,media_files,media_types,media_alt_texts,mentioned_names,mentioned_ids,hashtags".split(',')
MALTEGO_CSV_FIELDS = "EntityID,EntityType,id,author_name,author_alias,type,url,author_image,quotes,c_date,author_url,replies,text,author_id,views,reposts,likes,video_duration,video_url,icon-url,media".split(',')
EMPTY_COLUMNS = ['lang', 'mentioned_ids', 'collected_via', 'quoted_user', 'user_followers', 'to_username', 'to_tweetid', 'quoted_user_id', 'timestamp_utc', 'to_userid', 'user_name', 'retweeted_user_id', 'mentioned_names', 'retweeted_id', 'hashtags', 'retweeted_user', 'user_screen_name', 'quoted_id', 'user_id', 'user_friends', 'hashtags']


if __name__ == '__main__':
	if len(sys.argv) < 3:
		print('Provide names of Twitter Maltego dataset input filename and Twitter Twitwi dataset output filename')
		print('./Maltego_To_TwitiCSV_Converter.py input.csv output.csv')
		sys.exit(-1)

	input_file = sys.argv[1]
	output_file = sys.argv[2]

	mapping = {
		"EntityID": {
			"skip": True
		},
		"EntityType": {
			"skip": True,
		},
		"id": {
			"skip": False,
			"new_field": "id"
		},
		"author_name": {
			"skip": False,
			"new_field": "user_screen_name"
		},
		"author_alias": {
			"skip": False,
			"new_field": "user_name"
		},
		"type": {
			"skip": True,
		},
		"url": {
			"skip": False,
			"new_field": "url"
		},
		"author_image": {
			"skip": False,
			"new_field": "user_image"
		},
		"quotes": {
			"skip": True,
		},
		"c_date": {
			"new_field": "local_time",
			"convert": lambda t: t
		},
		"author_url": {
			"new_field": "user_url"
		},
		"replies": {
			"skip": True,
		},
		"text": {
			"new_field": "text"
		},
		"author_id": {
			"new_field": "user_id"
		},
		"views": {
			"skip": True,
		},
		"reposts": {
			"skip": True,
		},
		"likes": {
			"skip": True,
		},
		"video_duration": {
			"skip": True,
		},
		"icon-url": {
			"new_field": "media_urls"
		},
		"video_url": {
			"new_field": "media_urls"
		},
		"media": {
			"new_field": "media_urls"
		}
	}


	result = []
	with open(input_file, newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			new_tweet = {}
			for k, v in row.items():
				if k not in mapping:
					print(f"Could not find field {k} in mapping, exiting!")
					sys.exit(-1)

				if "skip" in mapping[k] and mapping[k]["skip"]:
					continue

				if not v:
					continue

				if "convert" in mapping[k]:
					new_value = mapping[k]["convert"](v)
				else:
					new_value = v

				new_field = mapping[k]["new_field"]

				if new_field in new_tweet:
					if type(new_tweet[new_field]) is list:
						new_tweet[new_field].append(new_value)
					else:
						new_tweet[new_field] = [new_tweet[new_field], new_value]
				else:
					new_tweet[new_field] = new_value

			for c in EMPTY_COLUMNS:
				if not c in new_tweet:
					new_tweet[c] = ''

			dt = datetime.datetime.strptime(new_tweet['local_time'], '%d.%m.%Y %H:%M:%S')
			new_tweet['timestamp_utc'] = dt.timestamp()
			new_tweet['user_followers'] = 0
			new_tweet['user_friends'] = 0

			hashtags = re.findall( r'#[a-zA-Z_-]+', new_tweet['text'])
			hashtags_list = []
			for h in hashtags:
				hashtags_list.append(h[1:])
			new_tweet['hashtags'] = '|'.join(hashtags_list)
			result.append(new_tweet)

	with open(output_file, 'w', newline='') as csvfile:
	    fieldnames = TWITWI_CSV_FIELDS
	    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	    writer.writeheader()
	    for new_tweet in result:
			writer.writerow(new_tweet)

	print(f'Done, written to {output_file}.')
