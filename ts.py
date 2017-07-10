#!/usr/bin/env python
"""Through twitter data analysis, compares public sentiment to sentiment of
influencial figures about given topics"""

from __future__ import print_function
import tweepy
import numpy as np
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import requests
import json



consumer_key = 'oZNDqncnvc9hFDwYocRGukS0V'
consumer_key_secret = 'wh4kSf3Xa11HWdShuW3Wdqkgdq67wOAeW7FCeTklUltshF6eZA'

access_token = '2324074514-GThBujMPCXhg6Xjjt9xBH4AueTovPEQTet2j5Kn'
access_token_secret = 'diYMPbqq0sh8fqpP6rHKp2dMENdvkMBlWwkvYD45Y0ImH'

auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

topic_dict = json.loads(open("topic_data.json", "r").read())
sent_dict = {}

handles = open("influencers.txt", "r")


def general_scrape(query):
	q = query
	tweet_struct = {}
	tweet_struct[q] = {}
	tweets = api.search(q=query)
	for tweet in tweets:
		id = str(tweet.id)
		if id not in tweet_struct[q]:
			tweet_struct[q][id] = {}
		tweet_struct[q][id]['favorites'] = tweet.favorite_count
		tweet_struct[q][id]['retweets'] = tweet.retweet_count
		tweet_struct[q][id]['text'] = tweet.text.encode("utf-8")
	return tweet_struct


def scrape_user(user_list):
	user_struct = {}
	user_tweets = []
	for user in user_list:
		try:
			user_tweets = api.user_timeline(id=user, count=20)
			print("[SCRAPING] " + str(user) + "...")
		except tweepy.TweepError as e:
			print("*** Encountered exception: " + str(e))
		u = user
		user_struct[u] = {}
		for tweet in user_tweets:
			id = str(tweet.id)
			if id not in user_struct[u]:
				user_struct[u][id] = {}
			user_struct[u][id]['text'] = tweet.text.encode("utf-8")
			user_struct[u][id]['favorites'] = tweet.favorite_count
			user_struct[u][id]['retweets'] = tweet.retweet_count
			user_struct[u][id]['followers'] = tweet.user.followers_count
			user_struct[u][id]['sentiment'] = calc_sent(tweet)

	return user_struct


def calc_sent(tweet):
	tweet_text = tweet.text.encode("utf-8")
	sent_data = [
		('text', tweet_text)
	]
	sent_result = requests.post('http://text-processing.com/api/sentiment/', data=sent_data)
	sent_json = sent_result.json()
	sent_dict['pos'] = int(round(sent_json['probability']['pos'] * 100))
	sent_dict['neg'] = int(round(sent_json['probability']['neg'] * 100))
	sent_dict['neutral'] = int(round(sent_json['probability']['neutral'] * 100))
	return sent_dict

def struct_json(topic):
	t = topic
	topic_dict[t] = {}
	topic_dict[t]['general'] = general_scrape(topic)
	topic_dict[t]['users'] = scrape_user(open('influencers.txt', 'r'))
	return topic_dict

def plot():
	mu_pos = np.mean(sent_dict['pos'])
	mu_neg = np.mean(sent_dict['neg'])
	mu_neu = np.mean(sent_dict['neutral'])
	labels = ('Positive', 'Negative', 'Neutral')
	y_pos = np.arange(len(labels))
	performance = [mu_pos, mu_neg, mu_neu]

	plt.barh(y_pos, performance, align='center', alpha=0.6)
	plt.yticks(y_pos, labels)
	plt.xlabel('Sentiment Score')
	plt.title('Sentiment Analysis of Given Topic: ' + query)
	plt.show()


query = raw_input("Enter your topic: ")
with open('topic_data.json', 'w') as fo:
	fo.write(json.dumps(struct_json(query), indent=4, sort_keys=False))
plot()