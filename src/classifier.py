import pickle
from InstagramAPI import InstagramAPI
from utils import *
import pprint
from tqdm import tqdm
import time
from statistics import mean
from sql_client import *
import math
import re
import sys
import os
from collections import Counter

pp = pprint.PrettyPrinter(indent=2)
sys.path.append(os.path.dirname(__file__))
comments_model_path = os.path.join(os.path.dirname(__file__), '../models/comments.model')

class Classifier(object):
	def __init__(self):
		super().__init__
		username = 'project_bulb'
		password = '=Xx4>+Arw:N7mrM4'
		self.InstagramAPI = InstagramAPI(username, password)
		self.InstagramAPI.login()
		self.sqlClient = SqlClient()

	def __uiFormatInt(self, n):
		if n > 1000000:
			return '{:.1f}M'.format(n / 1000000)
		elif n > 1000:
			return '{:.1f}K'.format(n / 1000)
		return n

	def getUserInsights(self):
		try:
			username = input('\n\nUtilisateur : ')
			time_temp_start = time.time()
			self.InstagramAPI.searchUsername(username)
			user_server = self.InstagramAPI.LastJson['user']
			self.InstagramAPI.getUserFeed(user_server['pk'])
			feed = self.InstagramAPI.LastJson['items']
			rates = list()
			timestamps = list()
			comment_scores = list()
			brpscs = list()
			print('Feed is %s post-long' % str(len(feed)))
			for post in feed:
				# Questionnement de l'API sur les champs du post
				timestamps.append(int(post['taken_at']))
				if user_server['follower_count'] == 0:
					engagement_rate = 0
				else:
					engagement_rate = (int(post['like_count']) + int(post['comment_count'])) * 100 / user_server['follower_count']
				rates.append(engagement_rate)

				# Brand presence
				brpsc = self.getBrandPresence(post)
				if brpsc:
					brpscs.extend(brpsc)

				# Get comment scores
				self.InstagramAPI.getMediaComments(str(post['id']))
				comments_server = self.InstagramAPI.LastJson
				for comment in comments_server['comments']:
					print(comment['text'])
					print(self.getCommentScore(comment['text']))
					comment_scores.append(self.getCommentScore(comment['text']))
			freq = self.__calculateFrequency(len(feed), min(timestamps))
			brand_types = self.getBrandTypes(brpscs)
			'''while True:
				text = input('Comment and I will tell your score ! (type \'exit\' to go next) : ')
				if text == 'exit': 
					break
				else: 
					comment_score = self.getCommentScore(text)
					print(text)
					print(comment_score)'''
			print(comment_scores)
			if len(rates) > 0:
				avg = mean(rates)
				print('Last post: %s' % self.__getIlya(max(timestamps)))
				print('Frequency: %.2f' % float(freq))
				print('Engagement: %.2f%%' % float(avg))
				print('N followings: %s' % self.__uiFormatInt(int(user_server['following_count'])))
				print('N followers: %s' % self.__uiFormatInt(int(user_server['follower_count'])))
				print('User mentions: %s' % self.__uiFormatInt(int(user_server['usertags_count'])))
				print('Brand presence: %s' % str(brpscs))
				print('Brand types: %s' % str(brand_types))
				print('Comments score: %s' % str(mean(comment_scores)))
				print('\nClassification ended in %.2fs seconds' % float(time.time()) - time_temp_start)
			else:
				print('This user has no posts !')
		except Exception as e:
			print(e)
			pass

	def getBrandPresence(self, post):
		brands = list()
		try:
			text = post['caption']['text']
			usertags = ['@%s' % user['user']['username'] for user in post['usertags']['in']]
			matches = re.findall('@[\w\.]+', text)
			for match in matches:
				if match in usertags:
					brands.append(match.split('@')[1])
			return brands
		except Exception as e:
			print(e)
			pass

	def getBrandTypes(self, brands):
		brand_counter = Counter()
		for brand in brands:
			self.InstagramAPI.searchUsername(brand)
			brand_full = self.InstagramAPI.LastJson['user']
			if 'category' in brand_full:
				brand_counter[brand_full['category']] += 1
		return brand_counter

	def __calculateFrequency(self, n, min_time):
		ilya = math.floor(time.time() - min_time)
		days = ilya // (60 * 60 * 24)
		days = days if days != 0 else 1
		return n / days

	def getCommentScore(self, comment):
		if not os.path.isfile(os.path.join(comments_model_path)):
			print('Creating comments model...')
			self.createCommentsModel()
		model = pickle.load(open(comments_model_path, 'rb'))
		word_scores = list()
		for word in re.compile('[#A-zÀ-ÿ]+').findall(comment):
			_word = self.processWordComment(word)
			if _word:
				if model[_word] > 0:
					word_score = 1 / model[_word]
				else:
					word_score = 1
				word_scores.append(word_score)
		if len(word_scores) > 0:
			comment_score = mean(word_scores)
		else:
			comment_score = 0
		k = 1 - (1.5 * math.exp(- 0.5 * len(word_scores)))
		return k * comment_score

	def createCommentsModel(self):
		self.sqlClient.openCursor()
		comments = self.sqlClient.getAllComments()
		self.sqlClient.closeCursor()
		comment_count = Counter()
		i = 0
		j = 0
		for comment in tqdm(comments):
			comment = str(comment)
			for word in re.compile('[#A-zÀ-ÿ]+').findall(comment):
				_word = self.processWordComment(word)
				if _word:
					i += 1
					comment_count[str(_word)] += 1
				else:
					j += 1
		print('Éléments considérés : %s' % str(i))
		print('Éléments non considérés : %s' % str(j))
		print(comment_count['beautiful'])
		with open(os.path.join(comments_model_path), 'wb') as outfile:
			pickle.dump(comment_count, outfile)

	def processWordComment(self, word):
		if word[0] == '#':
			word = None
		else:
			try:
				word = str(word).lower()
			except:
				word = None
		return word

	def __getIlya(self, _time):
		ilya = math.floor(time.time() - _time)
		days_mult = 60 * 60 * 24
		hours_mult = 60 * 60
		minutes_mult = 60
		days = ilya // days_mult
		hours = (ilya - days * days_mult) // hours_mult
		minutes = (ilya - days * days_mult - hours * hours_mult) // minutes_mult
		seconds = ilya % minutes_mult
		return '%s jour%s, %s heure%s, %s minute%s, %s seconde%s' % (days, '' if days in [0, 1] else 's', hours, '' if hours in [0, 1] else 's', minutes, '' if minutes in [0, 1] else 's', seconds, '' if seconds in [0, 1] else 's')

clf = Classifier()

while True:
	clf.getUserInsights()
	