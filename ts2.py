#!/usr/bin/env python
"""Through twitter data analysis, compares public sentiment to sentiment of
influencial figures about given topics"""

from __future__ import print_function
from scipy import stats
from google.cloud import language, exceptions
import twitter
import re
import tweepy
import numpy as np
import matplotlib.pyplot as plt; plt.rcdefaults()
import matplotlib.pyplot as plt
import json

client = language.Client()

consumer_key = 'Vduhbz2fU7IpZNwinIQtEVihH'
consumer_key_secret = 'yUyulJnd70F5UOJ7nlFhZefGXa0X022cZc7QkxDb14Khs53e01'

access_token = '2324074514-1VIioiwCafm9ErU3JeCU8lzsuxivw8qVv3zB6w0'
access_token_secret = '	9fuQOuKWSisy6jl7HbjYZabiB0lFfGHxFlV2UW3dDt0yg'

api = twitter.Api(consumer_key=consumer_key,
                  consumer_secret=consumer_key_secret,
                  access_token_key=access_token,
                  access_token_secret=access_token_secret)

#auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
#auth.set_access_token(access_token, access_token_secret)
#api = tweepy.API(auth)

topic_dict = json.loads(open("topic_data.json", "r").read())

handles = open("influencers.txt", "r")
general_sent = []
influ_sent = []
topic_list = []
sent = []


def general_scrape(query):
	q = str("q=" + query + "%20&result_type=recent&since=2016-01-01&count=100")
	tweet_struct = {}
	tweet_struct[q] = {}
	try:
		tweets = api.GetSearch(
			raw_query= q
		)
	except twitter.error.TwitterError as e:
		print("*** Encounter error: " + str(e))
		print("Plotting scraped data...")
		plot()
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
		text = tweet.text.encode("utf-8")
		try:
			document = client.document_from_text(text)
			sentiment_response = document.analyze_sentiment()
			sentiment = sentiment_response.sentiment.score

			sent_dict = {}
			if sentiment > 0.25:
				sent_dict['pos'] = sentiment
				sum_pos += sent_dict['pos']
			if 0.25 > sentiment > -0.25:
				sent_dict['neutral'] = abs(sentiment)
				sum_neu += sent_dict['neutral']
			else:
				sent_dict['neg'] = abs(sentiment)
				sum_neg += sent_dict['neg']
			tweet_struct[q][id]['sentiment'] = sent_dict
			tweet_counter += 1
		except exceptions.BadRequest:
			print("Invalid request, continuing to scrape...")
	print("Tweets Scraped: " + str(tweet_counter))
	if tweet_counter > 0:
		general_sent.append([int((sum_pos / tweet_counter) * 100), int((sum_neu / tweet_counter) * 100), int((sum_neg / tweet_counter) * 100)])
	return tweet_struct


def scrape_user(user_list, query):
	user_struct = {}
	user_tweets = []
	sum_pos = 0
	sum_neg = 0
	sum_neu = 0
	for user in user_list:
		tweet_counter = 0
		try:
			q = str("q="+query+"%3A"+user+"&result_type=recent")
			user_tweets = api.GetSearch(
				raw_query=q
			)
			print("[SCRAPING] " + str(user))
			print("...")
		except twitter.error.TwitterError as e:
			print("*** Encountered exception: " + str(e))
			plot()
		u = user
		user_struct[u] = {}
		for tweet in user_tweets:
			id = str(tweet.id)
			text = tweet.text.encode("utf-8")
			if id not in user_struct[u]:
				user_struct[u][id] = {}
			user_struct[u][id]['text'] = text
			user_struct[u][id]['favorites'] = tweet.favorite_count
			user_struct[u][id]['retweets'] = tweet.retweet_count
			user_struct[u][id]['followers'] = tweet.user.followers_count
			try:
				document = client.document_from_text(text)
				sentiment_response = document.analyze_sentiment()
				sentiment = sentiment_response.sentiment.score

				sent_dict = {}
				if sentiment > 0.25:
					sent_dict['pos'] = sentiment
					sum_pos += sent_dict['pos']
				if 0.25 > sentiment > -0.25:
					sent_dict['neutral'] = abs(sentiment)
					sum_neu += sent_dict['neutral']
				else:
					sent_dict['neg'] = abs(sentiment)
					sum_neg += sent_dict['neg']
				user_struct[u][id]['sentiment'] = sent_dict
				tweet_counter += 1
			except exceptions.BadRequest:
				print("Invalid request, continuing to scrape...")
		print("Tweets Scraped: " + str(tweet_counter))
		if tweet_counter > 0:
			influ_sent.append([int((sum_pos / tweet_counter) * 100), int((sum_neu / tweet_counter) * 100),
			                     int((sum_neg / tweet_counter) * 100)])
		else:
			influ_sent.append([0, 0, 0])
	return user_struct

def struct_json(topic):
	t = topic
	topic_dict[t] = {}
	topic_dict[t]['general'] = general_scrape(topic)
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
		plt.barh(y_pos, influ_sent[0], align='center', alpha=0.6)
		print("Influencer(s) Sentiment: " + str(influ_sent[0]))
		plt.yticks(y_pos, labels)
		plt.xlabel('Sentiment Score')
		plt.title('Sentiment Analysis of Given Topic: ' + topic)
		print('T Test Statistic: ' + str(stats.ttest_ind(general_sent[count], influ_sent[0], equal_var=False)[0]))
		print(
			'Two-Tailed P Value : ' + str(stats.ttest_ind(general_sent[count], influ_sent[0], equal_var=False)[1]))
		plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
		                    wspace=0.35)
		print(' ')
		count += 1
	plt.show()


main_dict = {}
query = ''
while query != ' ':
	query = raw_input("Enter your topic (type 'quit' to exit): ")
	if query == 'quit':
		break
	topic_list.append(query)

for query in topic_list:
	main_dict[query] = {}
	main_dict[query]['data'] = struct_json(query)
	scrape_user(handles, query)
	print('...')

with open('topic_data.json', 'w') as fo:
	fo.write(json.dumps(main_dict, indent=4, sort_keys=False))
plot()