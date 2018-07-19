"""
Copyright © 2018 Valentin Berthelot.

This file is part of Instaseek.

Instaseek is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Instaseek is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Instaseek. If not, see <https://www.gnu.org/licenses/>.
"""

### System libs. ###
import json
import getpass
import os
import sys
import configparser
import time
import atexit
import math
import gc
import pprint
from random import randint

### Installed libs. ###
import psycopg2
from tqdm import tqdm
from InstagramAPI import InstagramAPI
import imageio

imageio.plugins.ffmpeg.download()
sys.path.append(os.path.dirname(__file__))

### Custom libs. ###
from utils import *
from sql_client import *

### Tracking du chemin des fichiers et instanciation du PrettyPrinter. ###
config_path = os.path.join(os.path.dirname(__file__), './config.ini')
pp = pprint.PrettyPrinter(indent=2)
TTW = 8

class Streamer(object):
	"""
	Streamer class.
	"""
	def __init__(self):
		"""
		__init__ function.
		"""
		super().__init__()
		### Login au compte Instagram du projet pour avoir accès à l'API. ###
		self.config = configparser.ConfigParser()
		self.config.read(config_path)
		igusername = self.config['Instagram']['user']
		igpassword = self.config['Instagram']['password']

		### Connexion à l'API. ###
		self.InstagramAPI = InstagramAPI(igusername, igpassword)
		self.InstagramAPI.login()
		self.hashtags_sponsor_related = get_sponsor_hashtags()
		self.hashtags_random = get_random_hashtags()
		self.sqlClient = SqlClient()
		self.n_posts, self.n_authors, self.n_likes, self.n_comments = [0] * 4
		atexit.register(self.exit_handler)

	def exit_handler(self):
		"""
		Ferme la session Postgre quand le script exit.

				Args:
					(none)
				
				Returns:
					(none)
		"""

		print('Process ended ! Closing the session.')
		self.sqlClient.close()
		self.display_status()

	def display_status(self):
		"""
		Affiche le statut du stream.

				Args:
					(none)
				
				Returns:
					(none)
		"""

		tqdm.write('Number of posts and authors processed : %s,' % str(self.n_posts))
		tqdm.write('Number of likes processed : %s,' % str(self.n_likes))
		tqdm.write('Number of comments processed : %s' % str(self.n_comments))

	def process_post(self, post, topPost = False):
		"""
		Traite le post Instagram et l'insère en base.

				Args:
					post (dict) : le post Instagram à traiter.
					topPost (bool) : le post est-il récupéré en tant que TopPost sur Instagram ?
				
				Returns:
					(none)
		"""

		### Calcul du temps d'exécution de la fonction. On veut que le temps minimal d'exécution soit de 10s. ###
		time_start = time.time()
		
		try:
			### Questionnement de l'API sur les champs du post. ###
			time_temp_start = time.time()
			self.InstagramAPI.getUsernameInfo(post['user']['pk'])
			user_server = self.InstagramAPI.LastJson
			tqdm.write('Got 1 Author in %.2f seconds' % float(time.time() - time_temp_start))

			time_temp_start = time.time()
			self.InstagramAPI.getMediaComments(str(post['id']))
			comments_server = self.InstagramAPI.LastJson
			tqdm.write('Got %s Comments in %.2f seconds' % (str(len(comments_server['comments'])), float(time.time() - time_temp_start)))

			time_temp_start = time.time()
			self.InstagramAPI.getMediaLikers(str(post['id']))
			likers_server = self.InstagramAPI.LastJson
			tqdm.write('Got %s Likers in %.2f seconds' % (str(len(likers_server['users'])), float(time.time() - time_temp_start)))

			time_temp_start = time.time()
			self.InstagramAPI.getUserFeed(post['user']['pk'])
			feed = self.InstagramAPI.LastJson['items']
			tqdm.write('Got %s posts from feed in %.2f seconds' % (str(len(feed)), float(time.time() - time_temp_start)))

			### Insertion dans la BDD. ###
			time_temp_start = time.time()
			self.sqlClient.insertUser(user_server['user'])
			tqdm.write('Inserted 1 Author in %.2f seconds' % float(time.time() - time_temp_start))
			self.n_authors += 1

			time_temp_start = time.time()
			self.sqlClient.insertPost(post, topPost = topPost)
			tqdm.write('Inserted 1 Post in %.2f seconds' % float(time.time() - time_temp_start))
			self.n_posts += 1

			time_temp_start = time.time()
			self.sqlClient.insertUserFeed(feed)
			tqdm.write('Inserted feed of %s posts in %.2f seconds' % (str(len(feed)), float(time.time() - time_temp_start)))
			self.n_posts += len(feed)

			time_temp_start = time.time()
			self.sqlClient.insertLikers(post['id'], likers_server['users'])
			tqdm.write('Inserted %s Likers in %.2f seconds' % (str(len(likers_server['users'])), float(time.time() - time_temp_start)))
			self.n_likes += len(likers_server['users'])

			time_temp_start = time.time()
			self.sqlClient.insertComments(post['id'], comments_server['comments'])
			tqdm.write('Inserted %s Comments in %.2f seconds' % (str(len(comments_server['comments'])), float(time.time() - time_temp_start)))
			self.n_comments += len(comments_server['comments'])

			self.display_status()

		except Exception as e:
			print(e)
			### Si le client SQL ferme, on le réinstancie pour le rouvrir. ###
			self.sqlClient = SqlClient()
			self.sqlClient.openCursor()
			pass

		diff = time.time() - time_start
		if diff < TTW:
			tqdm.write('Waiting %.2f seconds before performing next request...' % float(TTW - diff))
			time.sleep(TTW - diff)
		tqdm.write('\n')

	def stream_step(self, hashtag, getTopPosts, stepIndex):
		"""
		Définit une étape du stream.

				Args:
					hashtag (str) : le hashtag à streamer.
					getTopPosts (bool) : prendre en compte les Top Posts uniquement ou non.
					stepIndex (int) : le numéro de l'étape de stream.
				
				Returns:
					(none)
		"""

		### Récupération des top posts et des posts les plus récents liés au hashtag en question. ###
		self.InstagramAPI.getHashtagFeed(hashtag)
		feed = self.InstagramAPI.LastJson
		self.sqlClient.openCursor()

		### Est-ce qu'on récupère les Top Posts Instagram ? ###
		if getTopPosts:
			topPostIter = tqdm(feed['ranked_items'])
			topPostIter.set_description('Streaming #%s\'s top posts...' % hashtag)

			### Processing des top posts. ###
			for post in topPostIter:
				self.process_post(post, topPost = True)
				self.display_status()
			sys.stdout.write("\033[K")

		### On parcourt la réponse de l'API avec les posts pour récupérer les auteurs de chaque post. ###
		postIter = tqdm(feed['items'])
		postIter.set_description('N°%s - Streaming #%s\'s recent posts...' % (stepIndex, hashtag))

		for post in postIter:
			self.process_post(post)
		self.sqlClient.closeCursor()

		sys.stdout.write("\033[K")

	def start_stream(self):
		"""
		Démarre le stream.

				Args:
					(none)
				
				Returns:
					(none)
		"""

		### Index de départ. ###
		i = 0

		### On stream ad vitam eternam. ###
		while True:
			print('Step n°%s...' % str(i), flush = True)
			should_get_top_posts = False
			if i % 10 == 0 and i != 0:
				should_get_top_posts = True
			### Selon le numéro de l'index, on va prendre des posts de hashtags sponsorisés, ou alors des hashtags populaires aléatoires. ###
			if i % 4 < 2:
				currentHashtag = self.hashtags_sponsor_related[i % 4]
			else:
				currentHashtag = self.hashtags_random[randint(0, len(self.hashtags_random) - 1)]
			self.sqlClient.setHashtag(currentHashtag)
			self.stream_step(currentHashtag, getTopPosts = should_get_top_posts, stepIndex = i)
			gc.collect()
			i += 1


