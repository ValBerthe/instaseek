from InstagramAPI import InstagramAPI
from utils import *
import pprint
from tqdm import tqdm
import time
from statistics import mean
import math
import re
from collections import Counter

pp = pprint.PrettyPrinter(indent=2)

username = 'project_bulb'
password = '=Xx4>+Arw:N7mrM4'
InstagramAPI = InstagramAPI(username, password)
InstagramAPI.login()

def uiFormatInt(n):
	if n > 1000000:
		return '{:.1f}M'.format(n / 1000000)
	elif n > 1000:
		return '{:.1f}K'.format(n / 1000)
	return n

def getUserInsights():
	try:
		username = input('\n\nUtilisateur : ')
		time_temp_start = time.time()
		InstagramAPI.searchUsername(username)
		user_server = InstagramAPI.LastJson['user']
		InstagramAPI.getUserFeed(user_server['pk'])
		feed = InstagramAPI.LastJson['items']
		rates = list()
		timestamps = list()
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
			brpsc = getBrandPresence(post)
			if brpsc:
				brpscs.extend(brpsc)
		freq = calculateFrequency(len(feed), min(timestamps))
		brand_types = get_brand_types(brpscs)
		if len(rates) > 0:
			avg = mean(rates)
			print('Last post: %s' % getIlya(max(timestamps)))
			print('Frequency: %.2f' % float(freq))
			print('Engagement: %.2f%%' % float(avg))
			print('N followings: %s' % uiFormatInt(int(user_server['following_count'])))
			print('N followers: %s' % uiFormatInt(int(user_server['follower_count'])))
			print('User mentions: %s' % uiFormatInt(int(user_server['usertags_count'])))
			print('Brand presence: %s' % str(brpscs))
			print('Brand types: %s' % str(brand_types))
			print('\nClassification ended in %.2fs seconds' % time.time() - time_temp_start)
		else:
			print('This user has no posts !')
	except Exception as e:
		#print(e)
		pass

def getBrandPresence(post):
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
		#print(e)
		pass

def get_brand_types(brands):
	brand_counter = Counter()
	for brand in brands:
		InstagramAPI.searchUsername(brand)
		brand_full = InstagramAPI.LastJson['user']
		if 'category' in brand_full:
			brand_counter[brand_full['category']] += 1
	return brand_counter

def calculateFrequency(n, min_time):
	ilya = math.floor(time.time() - min_time)
	days = ilya // (60 * 60 * 24)
	days = days if days != 0 else 1
	return n / days

def getIlya(_time):
	ilya = math.floor(time.time() - _time)
	days_mult = 60 * 60 * 24
	hours_mult = 60 * 60
	minutes_mult = 60
	days = ilya // days_mult
	hours = (ilya - days * days_mult) // hours_mult
	minutes = (ilya - days * days_mult - hours * hours_mult) // minutes_mult
	seconds = ilya % minutes_mult
	return '%s jour%s, %s heure%s, %s minute%s, %s seconde%s' % (days, '' if days in [0, 1] else 's', hours, '' if hours in [0, 1] else 's', minutes, '' if minutes in [0, 1] else 's', seconds, '' if seconds in [0, 1] else 's')

while True:
	getUserInsights()
	