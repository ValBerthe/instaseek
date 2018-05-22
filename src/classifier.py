from InstagramAPI import InstagramAPI
from utils import *
import pprint
from tqdm import tqdm
import time
from statistics import mean

pp = pprint.PrettyPrinter(indent=2)

username = 'project_bulb'
password = '=Xx4>+Arw:N7mrM4'
InstagramAPI = InstagramAPI(username, password)
InstagramAPI.login()

def isUserInfluencer():
	try:
		username = input('Utilisateur : ')
		time_temp_start = time.time()
		InstagramAPI.searchUsername(username)
		user_server = InstagramAPI.LastJson['user']
		InstagramAPI.getUserFeed(user_server['pk'])
		feed = InstagramAPI.LastJson
		rates = list()
		for post in feed['items']:
			# Questionnement de l'API sur les champs du post
			if user_server['follower_count'] == 0:
				engagement_rate = 0
			else:
				engagement_rate = (int(post['like_count']) + int(post['comment_count'])) * 100 / user_server['follower_count']
			rates.append(engagement_rate)
		if len(rates) > 0:
			avg = mean(rates)
			print('Engagement: %.2f%%' % float(engagement_rate))
			print('N followings: %s' % user_server['following_count'])
			print('N followers: %s' % user_server['follower_count'])
			print('User mentions: %s' % user_server['usertags_count'])
		else:
			print('This user has no posts !')
	except (KeyError, AttributeError, TypeError):
		print('An error occured, please try again.')
		pass


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
	isUserInfluencer()
	