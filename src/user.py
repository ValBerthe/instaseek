import pickle
from InstagramAPI import InstagramAPI
from utils import *
import pprint
from tqdm import tqdm
import time
from statistics import mean, stdev
from sql_client import *
import math
import numpy as np
import regex
import sys
import os
from PIL import Image
import requests
from io import BytesIO
from collections import Counter
import scipy
import scipy.misc
import scipy.cluster
import cv2
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

pp = pprint.PrettyPrinter(indent=2)
sys.path.append(os.path.dirname(__file__))
comments_model_path = os.path.join(os.path.dirname(__file__), '../models/comments.model')
users_model_path = os.path.join(os.path.dirname(__file__), '../models/users_sample.model')

N_CLUSTERS = 3

class User(object):
	"""
	Classe utilisateur.
	"""
	def __init__(self):
		"""
		__init__ function.
		"""
		super().__init__()
		igusername = 'project_bulb'
		igpassword = '=Xx4>+Arw:N7mrM4'
		self.username = ''
		self.InstagramAPI = InstagramAPI(igusername, igpassword)
		self.InstagramAPI.login()
		self.sqlClient = SqlClient()
		self.n_clusters = N_CLUSTERS

		# Features pour l'apprentissage
		self.lastpost = 0
		self.frequency = 0
		self.engagement = 0
		self.followings = 0
		self.followers = 0
		self.usermentions = 0
		self.brandpresence = 0
		self.brandtypes = 0
		self.commentscore = 0

		"""
		Function parameters
		"""
		self.K = 0.17
		self.K_ = 7
		self.B = 0.5

	def __uiFormatInt(self, n):
		"""
		Conversion du nombre de followers/abonnements en K (mille) et M (million).
		"""
		if n > 1000000:
			return '{:.1f}M'.format(n / 1000000)
		elif n > 1000:
			return '{:.1f}K'.format(n / 1000)
		return n

	def __uiGetIlya(self, _time):
		"""
		Génération du string: Il y a...
		"""
		ilya = math.floor(time.time() - _time)
		days_mult = 60 * 60 * 24
		hours_mult = 60 * 60
		minutes_mult = 60
		days = ilya // days_mult
		hours = (ilya - days * days_mult) // hours_mult
		minutes = (ilya - days * days_mult - hours * hours_mult) // minutes_mult
		seconds = ilya % minutes_mult
		return '%s jour%s, %s heure%s, %s minute%s, %s seconde%s' % (days, '' if days in [0, 1] else 's', hours, '' if hours in [0, 1] else 's', minutes, '' if minutes in [0, 1] else 's', seconds, '' if seconds in [0, 1] else 's')

	def __calculateFrequency(self, n, min_time):
		"""
		Calcul de la fréquence de post.
		"""
		ilya = math.floor(time.time() - min_time)
		days = ilya // (60 * 60 * 24)
		days = days if days != 0 else 1
		return n / days

	def __calcCentroid3d(self, listie):
		"""
		Calcul des barycentres des points de couleur dans le repère lab*. 
		"""
		arr = np.array(listie)
		length = arr.shape[0]
		sum_x = np.sum(arr[:, 0])
		sum_y = np.sum(arr[:, 1])
		sum_z = np.sum(arr[:, 2])
		centroid = np.array([sum_x/length, sum_y/length, sum_z/length])
		distances = [np.linalg.norm(data - centroid) for data in listie]
		return mean(distances)
	
	def getUserNames(self):
		"""
		Récupère les usrnames des utilisateurs annotés.
		"""
		self.sqlClient.openCursor()
		allusers = self.sqlClient.getAllUsers()
		self.sqlClient.closeCursor()
		return allusers

	def getUserInfoIG(self):
		"""
		Récupération des critères de l'utilisateur via. l'API d'Instagram.
		"""
		try:
			username = self.username
			time_temp_start = time.time()
			self.InstagramAPI.searchUsername(username)
			user_server = self.InstagramAPI.LastJson['user']
			time.sleep(1)
			feed = self.InstagramAPI.getTotalUserFeed(user_server['pk'])
			#feed = self.InstagramAPI.LastJson['items']
			time.sleep(1)
			rates = list()
			timestamps = list()
			comment_scores = list()
			brpscs = list()
			colorfulness_list = list()
			dominant_colors_list = list()
			contrast_list = list()
			print('Feed is %s post-long' % str(len(feed)))
			for index, post in enumerate(feed[:50]):
				print('Post %s/%s...' % (index + 1, len(feed[:50])), end = '\r', flush = True)
				try:
					# Questionnement de l'API sur les champs du post
					timestamps.append(int(post['taken_at']))
					if user_server['follower_count'] == 0:
						engagement_rate = 0
					else:
						k = 100 / user_server['follower_count']
						if 'like_count' in post:
							if 'comment_count' in post:
								engagement_rate = (int(post['like_count']) + int(post['comment_count'])) * k
							else:
								engagement_rate = int(post['like_count']) * k
						else:
							if 'comment_count' in post:
								engagement_rate = int(post['comment_count']) * k
							else:
								engagement_rate = 0
					rates.append(engagement_rate)

					# Image urls
					try:
						url = get_post_image_url(post)

						response = requests.get(url)
						img = Image.open(BytesIO(response.content))
						grayscale_img = img.convert('LA')

						most_dominant_colour = self.getMostDominantColour(img)
						dominant_colors_list.extend(most_dominant_colour)

						colorfulness = self.getImageColorfulness(img)
						colorfulness_list.append(colorfulness)

						contrast = self.getContrast(grayscale_img)
						contrast_list.append(contrast)
					except Exception as e:
						print('Error while getting image info (user.py): %s' % e)


					# Brand presence
					brpsc = self.getBrandPresence(post)
					if brpsc:
						brpscs.extend(brpsc)

					# Get comment scores
					self.InstagramAPI.getMediaComments(str(post['id']))
					comments_server = self.InstagramAPI.LastJson

					# Sleep to avoid 503 errors : too many requests
					time.sleep(1)
					if 'comments' in comments_server:
						for comment in comments_server['comments']:
							if len(comment_scores) > 10:
								break
							if comment['user']['username'] == self.username:
								continue
							score = self.getCommentScore(comment['text'])
							comment_scores.append(score)
							time.sleep(1)
				except Exception as e:
					j = 0
					while j < 4:
						for i in range(60):
							print('Something went wrong while getting post info:\n%s\nWaiting %s seconds before requesting server again.' % (e, (60 - i)), end='\r', flush=True)
							time.sleep(1)
						j += 1
						self.getUserInfoIG()
					pass

			# Assign and print features
			if len(rates) > 0:
				avg = mean(rates)
				self.lastpost = time.time() - max(timestamps)
				self.frequency =  self.__calculateFrequency(len(feed), min(timestamps))
				self.engagement = avg
				self.followings = int(user_server['following_count'])
				self.followers = int(user_server['follower_count'])
				self.usermentions = int(user_server['usertags_count'])
				self.brandpresence = brpscs
				self.brandtypes = self.getBrandTypes(brpscs)
				self.commentscore = mean(comment_scores) * (1 + stdev(comment_scores))
				self.colorfulness_std = stdev(colorfulness_list)
				self.contrast_std = stdev(contrast_list)
				self.colors = [[color.lab_l, color.lab_a, color.lab_b] for color in dominant_colors_list]
				self.codes, self.color_distorsion = scipy.cluster.vq.kmeans(np.array(self.colors), self.n_clusters)
				self.colors_dispersion = self.__calcCentroid3d(self.colors)

				print('Username : %s' % self.username)
				print('Last post: %s' % self.__uiGetIlya(max(timestamps)))
				print('Frequency: %.2f' % float(self.frequency))
				print('Engagement: %.2f%%' % float(self.engagement))
				print('N followings: %s' % self.__uiFormatInt(self.followings))
				print('N followers: %s' % self.__uiFormatInt(self.followers))
				print('User mentions: %s' % self.__uiFormatInt(self.usermentions))
				print('Brand presence: %s' % str(self.brandpresence))
				print('Brand types: %s' % str(self.brandtypes))
				print('Comments score: %s' % str(self.commentscore))
				print('Colorfulness standard deviation: %s' % self.colorfulness_std)
				print('Contrast standard deviation: %s' % self.contrast_std)
				print('Overall color distorsion : %s' % str(self.color_distorsion))
				print('\nFeature extraction ended in %.2fs seconds' % (float(time.time() - time_temp_start)))
			else:
				print('This user has no posts !')

		except Exception as e:
			print(e)
			pass
	
	def getUserInfoSQL(self):
		"""
		On récupère les posts de l'utilisateur à partir de la BDD, et on en extrait les features nécessaires pour l'apprentissage.
		L'intérêt de cette méthode est qu'on peut solliciter la BDD très vite par rapport à l'API Instagram, ce qui nous permet de faire un
		apprentissage 'rapide'!
		"""
		self.sqlClient.openCursor()
		user_sql = self.sqlClient.getUser(self.username)
		posts = self.sqlClient.getUserPosts(user_sql['id'])

		"""
		Initialisation des listes de stockage pour les métriques.
		"""
		rates = list()
		timestamps = list()
		comment_scores = list()
		brpscs = list()
		colorfulness_list = list()
		dominant_colors_list = list()
		contrast_list = list()

		for post in posts:
			"""
			Timestamps et taux d'engagement: métriques immédiates.
			"""
			timestamps.append(int(post['timestamp']))
			if user_sql['n_follower'] == 0:
				engagement_rate = 0
			else:
				k = 100 / user_sql['n_follower']
				if 'n_likes' in post:
					if 'n_comments' in post:
						engagement_rate = (int(post['n_likes']) + int(post['n_comments'])) * k
					else:
						engagement_rate = int(post['n_likes']) * k
				else:
					if 'n_comments' in post:
						engagement_rate = int(post['n_comments']) * k
					else:
						engagement_rate = 0
			rates.append(engagement_rate)

			"""
			On récupère le code binaire des images en BDD, et on y opère les traitements :
			- STD du contraste
			- STD de l'intensité colorimétrique
			- Distorsion des clusters de couleur
			"""
			img = post['image']
			if (img):
				img = Image.open(BytesIO(img[0]))
				grayscale_img = img.convert('LA')

				most_dominant_colour = self.getMostDominantColour(img)
				dominant_colors_list.extend(most_dominant_colour)

				colorfulness = self.getImageColorfulness(img)
				if not math.isnan(colorfulness):
					colorfulness_list.append(colorfulness)

				contrast = self.getContrast(grayscale_img)
				if not math.isnan(contrast):
					contrast_list.append(contrast)

			
			# Brand presence
			"""
			Pour l'instant on ne s'en sert pas, à ré-utiliser quand on s'intéressera à la détection des placements de produits.
			"""
			"""
			brpsc = self.getBrandPresence(post)
			if brpsc:
				brpscs.extend(brpsc)
			"""

			# Get comment scores
			comments = self.sqlClient.getComments(str(post['id']))
			for comment in comments:
				if comment['id_user'] == post['user_id']:
					continue
				score = self.getCommentScore(comment['comment'])
				comment_scores.append(score)
			if len(comment_scores) > 1:
				commentscore = mean(comment_scores) * (1 + stdev(comment_scores))
			elif len(comment_scores) == 1:
				commentscore = comment_scores[0]
			else:
				commentscore = 0
			
		# Assign and print features
		"""
		self.engagement : Le taux d'engagement sur le feed : n_likes + n_comments / n_followers.
		self.lastpost : le timestamp POSIX du dernier post.
		self.frequency : la fréquence de psot sur le feed.
		self.followers : le nombre de followers.
		self.followings : le nombre d'abonnements de l'utilisateur.
		self.usermentions : le nombre de mentions utilisateur.
		self.brandpresence : la liste des comptes, potentiellement des marques, avec qui l'influenceur fait des placements de produit.
		self.brandtypes : le type de marques que l'utilisateur tague.
		self.commentscore : le score de commentaires moyen que reçoit l'utilisateur.
		self.colorfulness_std : l'intensité de couleurs sur le feed (écart-type).
		self.contrast_std : le contraste sur les photos du feed (écart-type).
		self.color_distorsion : la distorsion des clusters de couleur.
		self.label : la catégorie de l'utilisateur.
		"""
		if len(rates) > 0:
			avg = mean(rates)
			self.engagement = avg
			self.lastpost = time.time() - max(timestamps)
			self.frequency =  self.__calculateFrequency(len(posts), min(timestamps))		
			self.followings = int(user_sql['n_following'])
			self.followers = int(user_sql['n_follower'])
			self.usermentions = int(user_sql['n_usertags'])
			self.brandpresence = brpscs
			self.brandtypes = self.getBrandTypes(brpscs)
			self.commentscore = commentscore
			self.colorfulness_std = stdev(colorfulness_list)
			self.contrast_std = stdev(contrast_list)
			self.colors = [[color.lab_l, color.lab_a, color.lab_b] for color in dominant_colors_list]
			
			"""
			Ici, on cherche à avoir la distorsion des k-means des couleurs du feed.
			Parfois, on peut avoir que une ou deux couleurs outputées du k-mean.
			Si on a une erreur, on baisse le nombre de clusters jusqu'à ce que le k-mean puisse être opéré.
			"""
			while True:
				try:
					if (self.n_clusters == 0):
						break
					self.codes, self.color_distorsion = scipy.cluster.vq.kmeans(np.array(self.colors), self.n_clusters)
				except:
					self.n_clusters = self.n_clusters - 1
					continue
				break
			self.colors_dispersion = self.__calcCentroid3d(self.colors)
			self.label = int(user_sql['label'])
		else:
			print('This user has no posts !')

	def getMostDominantColour(self, image):
		"""
		Retourne la couleur dominante de l'image.
		"""
		NUM_CLUSTERS = 5
		image = image.resize((150, 150))
		ar = np.array(image)
		shape = ar.shape
		ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

		codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
		vecs, dist = scipy.cluster.vq.vq(ar, codes)         
		counts, bins = scipy.histogram(vecs, len(codes))    
		index_max = scipy.argmax(counts)
		peak = codes[index_max]

		rgb = sRGBColor(*peak)
		lab = convert_color(rgb, LabColor)
		return [lab]

	def getImageColorfulness(self, image):
		"""
		Retoune l'intensité colorimétrique de l'image.
		"""
		ar = np.array(image)
		open_cv_image = ar[:, :, ::-1].copy()
		(B, G, R) = cv2.split(open_cv_image.astype("float"))
		rg = np.absolute(R - G)
		yb = np.absolute(0.5 * (R + G) - B)
		(rbMean, rbStd) = (np.mean(rg), np.std(rg))
		(ybMean, ybStd) = (np.mean(yb), np.std(yb))
		stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
		meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))
		return stdRoot + (0.3 * meanRoot)

	def getContrast(self, img):
		"""
		Retourne le contraste global de l'image.
		Passe par un calcul d'entropie.
		"""
		ar = np.array(img)
		hist = np.histogram(ar)
		data = hist[0]
		data = data / data.sum()
		return - (data * np.log(np.abs(data))).sum()

	def getBrandPresence(self, post):
		"""
		Retourne les mentions utilisateur qui matchent avec les utilisateurs mentionnés dans la description du post.
		"""
		brands = list()
		try:
			text = post['caption']['text']
			usertags = ['@%s' % user['user']['username'] for user in post['usertags']['in']]
			matches = regex.findall(r'@[\w\.]+', text)
			for match in matches:
				if match in usertags:
					brands.append(match.split('@')[1])
			return brands
		except Exception as e:
			pass

	def getBrandTypes(self, brands):
		"""
		Retourne les types de business que sont les 'marques' mentionnées à la fois dans la description du post et en mention utilisateur.
		"""
		brand_counter = Counter()
		for brand in brands:
			self.InstagramAPI.searchUsername(brand)
			brand_full = self.InstagramAPI.LastJson['user']
			if 'category' in brand_full:
				brand_counter[brand_full['category']] += 1
		return brand_counter

	def getCommentScore(self, comment):
		"""
		Retourne le score de commentaire basé sur le modèle de commentaires.
		"""
		if not os.path.isfile(os.path.join(comments_model_path)):
			print('Creating comments model...')
			self.createCommentsModel()
		model = pickle.load(open(comments_model_path, 'rb'))
		word_scores = list()
		for word in regex.compile(r'[@#\p{L}_\u263a-\U0001f645]+').findall(comment):
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
		k = 1 - math.exp(- self.K * len(word_scores))
		j = 1 / (1 + math.exp(- self.K_ * (stdev(word_scores) - self.B))) if len(word_scores) > 1 else 0
		return k * j * comment_score

	def createCommentsModel(self):
		"""
		Crée le modèle de commentaires.
		"""
		self.sqlClient.openCursor()
		comments = self.sqlClient.getAllComments()
		self.sqlClient.closeCursor()
		comment_count = Counter()
		i = 0
		j = 0
		for comment in tqdm(comments):
			comment = str(comment)
			wordArray = regex.compile(r'[@#\p{L}_\u263a-\U0001f645]+').findall(comment)
			length = len(wordArray)
			for word in wordArray:
				_word = self.processWordComment(word)
				if _word:
					i += 1
					comment_count[_word] += 1 / length
				else:
					j += 1
		print('Éléments considérés : %s' % str(i))
		print('Éléments non considérés : %s' % str(j))
		print(comment_count['beautiful'])
		with open(os.path.join(comments_model_path), 'wb') as outfile:
			pickle.dump(comment_count, outfile)

	def processWordComment(self, word):
		"""
		Pré-processe le commentaire.
		"""
		if word[0] in ['#', '@'] or word in ['.', '!', '?', ',', ':', ';', '-', '+', '=', '/', '&', '@', '$', '_']:
			word = None
		else:
			try:
				"""
				Ici ça pète quand il y a du russe ou des emojis.
				"""
				word = str(word).lower()
			except:
				word = word
		return word

	def testCommentScore(self):
		"""
		Tooling permettant de tester les scores des commentaires utilisateur.
		"""
		while True:
			text = input('Comment and I will tell your score ! (type \'exit\' to go next) : ')
			if text == 'exit': 
				break
			else: 
				comment_score = self.getCommentScore(text)
				print(text)
				print(comment_score)
