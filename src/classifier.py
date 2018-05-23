from InstagramAPI import InstagramAPI
from utils import *
import pprint
from tqdm import tqdm
import time
from statistics import mean
import math

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
		print('Feed is %s post-long' % str(len(feed)))
		for post in feed:
			# Questionnement de l'API sur les champs du post
			timestamps.append(int(post['taken_at']))
			if user_server['follower_count'] == 0:
				engagement_rate = 0
			else:
				engagement_rate = (int(post['like_count']) + int(post['comment_count'])) * 100 / user_server['follower_count']
			rates.append(engagement_rate)
		freq = calculateFrequency(len(feed), min(timestamps))
		if len(rates) > 0:
			avg = mean(rates)
			print('Last post: %s' % getIlya(max(timestamps)))
			print('Frequency: %.2f' % float(freq))
			print('Engagement: %.2f%%' % float(avg))
			print('N followings: %s' % uiFormatInt(int(user_server['following_count'])))
			print('N followers: %s' % uiFormatInt(int(user_server['follower_count'])))
			print('User mentions: %s' % uiFormatInt(int(user_server['usertags_count'])))
		else:
			print('This user has no posts !')
	except (KeyError, AttributeError, TypeError, ValueError) as e:
		print(e)
		pass

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

def getHashtagUsersInfo():
	InstagramAPI.getHashtagFeed('sponsored')
	feed = InstagramAPI.LastJson

	for post in feed['items'][0:3]:
		# Questionnement de l'API sur les champs du post
		time_temp_start = time.time()
		InstagramAPI.getUsernameInfo(post['user']['pk'])
		user_server = InstagramAPI.LastJson['user']
		pp.pprint('Username: %s' % user_server['username'])
		pp.pprint('Got 1 Author in %.2f seconds' % float(time.time() - time_temp_start))

		time_temp_start = time.time()
		InstagramAPI.getMediaComments(str(post['id']))
		comments_server = InstagramAPI.LastJson
		pp.pprint('Got %s Comments in %.2f seconds' % (str(len(comments_server['comments'])), float(time.time() - time_temp_start)))

		time_temp_start = time.time()
		InstagramAPI.getMediaLikers(str(post['id']))
		likers_server = InstagramAPI.LastJson
		pp.pprint('Got %s Likers in %.2f seconds' % (str(len(likers_server['users'])), float(time.time() - time_temp_start)))

		engagement_rate = (len(likers_server) + len(comments_server['comments'])) / user_server['follower_count']
		pp.pprint('Likes: %s' % len(likers_server))
		pp.pprint('Comments: %s' % len(comments_server['comments']))
		pp.pprint('Engagement: %s' % engagement_rate)
		pp.pprint('N followers: %s' % user_server['follower_count'])
		pp.pprint('User mentions: %s' % user_server['usertags_count'])
		pp.pprint('___________')

		isInfluencer = user_server['follower_count'] > 3000

while True:
	getUserInsights()
	