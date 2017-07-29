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

consumer_key = ['TuazY9pjad7QUCuzU9zJbreV8',
                'oZNDqncnvc9hFDwYocRGukS0V',
                '5dBoQA35kcig7TwCk2M0Xhjo2']
consumer_key_secret = ['afNPWMmB4HonTDWSOToePUjKO0wb3eL34NiTb3whk4RkOneJvi',
                       'wh4kSf3Xa11HWdShuW3Wdqkgdq67wOAeW7FCeTklUltshF6eZA',
                       'QGtLsOmi4ZsxXgDHYsWNr0uizQzSUhm8KPd3GtPf30nYvyVdB7']

access_token = ['2324074514-LovPdW7V2VgDLUZuhpq8M0Ztnfj4TdILtih7cTw',
                '2324074514-GThBujMPCXhg6Xjjt9xBH4AueTovPEQTet2j5Kn',
                '2324074514-SY9hg2Qx90nxGNdNLWOYe5HqigO2syvsoSn2jhu']
access_token_secret = ['Qo2ZKipTZ09bTZKtiToehJG5PI4BgiYNgTU1Ot0wmHndM',
                       'diYMPbqq0sh8fqpP6rHKp2dMENdvkMBlWwkvYD45Y0ImH',
                       't0ZQ2ruh65dHApEsKlMEOCAdft6JwS5WHAFCBou8UZusK']

api = twitter.Api(consumer_key=consumer_key[0],
                  consumer_secret=consumer_key_secret[0],
                  access_token_key=access_token[0],
                  access_token_secret=access_token_secret[0])

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

	pos_count = 0
	neu_count = 0
	neg_count = 0

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
				pos_count += 1
			if 0.25 > sentiment > 0:
				sent_dict['neutral'] = abs(sentiment)
				sum_neu += sent_dict['neutral']
				neu_count += 1
			else:
				sent_dict['neg'] = abs(sentiment)
				sum_neg += sent_dict['neg']
				neg_count += 1
			tweet_struct[q][id]['sentiment'] = sent_dict
			tweet_counter += 1
		except exceptions.BadRequest:
			print("Invalid request, continuing to scrape...")
	print("Tweets Scraped: " + str(tweet_counter))
	if pos_count > 0:
		av_pos = int((sum_pos / pos_count) * 100)
	else:
		av_pos = 0
	if neu_count > 0:
		av_neu = int((sum_neu / neu_count) * 100)
	else:
		av_neu = 0
	if neg_count > 0:
		av_neg = int((sum_neg / neg_count) * 100)
	else:
		av_neg = 0
	general_sent.append([av_pos, av_neu, av_neg])
	return tweet_struct


def scrape_user(user_list, query):
	user_struct = {}
	user_tweets = []
	total_tweets = 0

	sum_pos = 0
	sum_neg = 0
	sum_neu = 0

	pos_count = 0
	neu_count = 0
	neg_count = 0

	av_pos = 0
	av_neu = 0
	av_neg = 0

	for user in user_list:
		try:
			q = str("q="+query+"%3A"+user+"&result_type=recent")
			user_tweets = api.GetSearch(
				raw_query=q
			)
			print("[SCRAPING] " + str(user))
			print("...")
		except twitter.error.TwitterError as e:
			print("*** Encountered exception: " + str(e))
			if not influ_sent:
				influ_sent.append([0, 0, 0])
			else:
				influ_sent.append([av_pos, av_neu, av_neg])
			plot()
		u = user
		user_struct[u] = {}
		tweet_counter = 0
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
					pos_count += 1
				if 0.25 > sentiment > 0:
					sent_dict['neutral'] = abs(sentiment)
					sum_neu += sent_dict['neutral']
					neu_count += 1
				else:
					sent_dict['neg'] = abs(sentiment)
					sum_neg += sent_dict['neg']
					neg_count += 1
				user_struct[u][id]['sentiment'] = sent_dict
				tweet_counter += 1
				total_tweets += 1
			except exceptions.BadRequest:
				print("Invalid request, continuing to scrape...")
		print("Tweets Scraped: " + str(tweet_counter))
		if pos_count > 0:
			av_pos = int((sum_pos / pos_count) * 100)
		else:
			av_pos = 0
		if neu_count > 0:
			av_neu = int((sum_neu / neu_count) * 100)
		else:
			av_neu = 0
		if neg_count > 0:
			av_neg = int((sum_neg / neg_count) * 100)
		else:
			av_neg = 0
	influ_sent.append([av_pos, av_neu, av_neg])
	return user_struct

def struct_json(topic):
	t = topic
	topic_dict[t] = {}
	topic_dict[t]['general'] = general_scrape(topic)
	topic_dict[t]['user'] = scrape_user(handles, query)
	return topic_dict


def plot():
	labels = ('Positive', 'Neutral', 'Negative')
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
	print('...')

with open('topic_data.json', 'w') as fo:
	fo.write(json.dumps(main_dict, indent=4, sort_keys=False))
plot()