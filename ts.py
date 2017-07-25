#!/usr/bin/env python
"""Through twitter data analysis, compares public sentiment to sentiment of
influencial figures about given topics"""

from __future__ import print_function
from scipy import stats
import tweepy
import numpy as np
import matplotlib.pyplot as plt; plt.rcdefaults()
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

handles = open("influencers.txt", "r")
general_sent = []
influ_sent = []
topic_list = []
sent = []

def general_scrape(query):
	q = query
	tweet_struct = {}
	tweet_struct[q] = {}
	tweets = api.search(q=query, per_page=20, pages=50)
	print("[SCRAPING] general users")
	print("...")
	sum_pos = 0
	sum_neg = 0
	sum_neu = 0
	tweet_counter = 0
	for tweet in tweets:
		id = str(tweet.id)
		if id not in tweet_struct[q]:
			tweet_struct[q][id] = {}
		tweet_struct[q][id]['favorites'] = tweet.favorite_count
		tweet_struct[q][id]['retweets'] = tweet.retweet_count
		tweet_struct[q][id]['text'] = tweet.text.encode("utf-8")
		t = tweet.text.encode("utf-8")
		sent_data = [
			('text', t)
		]
		sent_result = requests.post('http://text-processing.com/api/sentiment/', data=sent_data)
		sent_json = sent_result.json()
		sent_dict = {}
		sent_dict['pos'] = int(round(sent_json['probability']['pos'] * 100))
		sum_pos += sent_dict['pos']
		sent_dict['neg'] = int(round(sent_json['probability']['neg'] * 100))
		sum_neg += sent_dict['neg']
		sent_dict['neutral'] = int(round(sent_json['probability']['neutral'] * 100))
		sum_neu += sent_dict['neutral']
		tweet_struct[q][id]['sentiment'] = sent_dict
		tweet_counter += 1
	general_sent.append([sum_pos / tweet_counter, sum_neg / tweet_counter, sum_neu / tweet_counter])
	return tweet_struct


def scrape_user(user_list):
	user_struct = {}
	user_tweets = []
	sum_pos = 0
	sum_neg = 0
	sum_neu = 0
	tweet_counter = 0
	for user in user_list:
		try:
			user_tweets = api.user_timeline(id=user, count=50)
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
			t = tweet.text.encode("utf-8")
			sent_data = [
				('text', t)
			]
			sent_result = requests.post('http://text-processing.com/api/sentiment/', data=sent_data)
			sent_json = sent_result.json()
			sent_dict = {}
			sent_dict['pos'] = int(round(sent_json['probability']['pos'] * 100))
			sum_pos += sent_dict['pos']
			sent_dict['neg'] = int(round(sent_json['probability']['neg'] * 100))
			sum_neg += sent_dict['neg']
			sent_dict['neutral'] = int(round(sent_json['probability']['neutral'] * 100))
			sum_neu += sent_dict['neutral']
			user_struct[u][id]['sentiment'] = sent_dict
			tweet_counter += 1
	influ_sent.append([sum_pos/tweet_counter, sum_neg/tweet_counter, sum_neu/tweet_counter])
	return user_struct


def struct_json(topic):
	t = topic
	topic_dict[t] = {}
	topic_dict[t]['general'] = general_scrape(topic)
	topic_dict[t]['users'] = scrape_user(open('influencers.txt', 'r'))
	return topic_dict

def plot():
	labels = ('Positive', 'Negative', 'Neutral')
	y_pos = np.arange(len(labels))
	count = 0

	for topic in topic_list:
		print("For Topic: " + topic)
		plt.figure()
		plt.subplot(221)
		plt.barh(y_pos, general_sent[count], align='center', alpha=0.6)
		print("General Sentiment: " + str(general_sent[count]))
		plt.yticks(y_pos, labels)
		plt.xlabel('Sentiment Score')
		plt.title('Sentiment Analysis of Given Topic: ' + topic)
		plt.subplot(222)
		plt.barh(y_pos, influ_sent[count], align='center', alpha=0.6)
		print("Influencer(s) Sentiment: " + str(influ_sent[count]))
		plt.yticks(y_pos, labels)
		plt.xlabel('Sentiment Score')
		plt.title('Sentiment Analysis of Given Topic: ' + topic)
		print('T Test Statistic: ' + str(stats.ttest_ind(general_sent[count], influ_sent[count], equal_var=False)[0]))
		print('Two-Tailed P Value : ' + str(stats.ttest_ind(general_sent[count], influ_sent[count], equal_var=False)[1]))
		plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
		                    wspace=0.35)
		print(" ")
		count+=1
	plt.show()


main_dict = {}
query = ''
while query != ' ':
	query = raw_input("Enter your topic (type 'quit' to exit): ")
	if query == 'quit':
		break
	main_dict[query] = {}
	topic_list.append(query)
	main_dict[query]['data'] = struct_json(query)

with open('topic_data.json', 'w') as fo:
	fo.write(json.dumps(main_dict, indent=4, sort_keys=False))
plot()