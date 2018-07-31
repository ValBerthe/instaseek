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
import pickle
import pprint
import time
import math
import regex
import sys
import os
import configparser
import numpy as np

from ast import literal_eval as make_tuple
from statistics import mean, stdev
from io import BytesIO
from collections import Counter

### Installed libs. ###
import scipy
import scipy.misc
import scipy.cluster
from cv2 import cv2
import matplotlib.pyplot as plt
import requests
from InstagramAPI import InstagramAPI
from tqdm import tqdm
from PIL import Image
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
from mpl_toolkits.mplot3d import Axes3D
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

sys.path.append(os.path.dirname(__file__))

### Custom libs. ###
from sql_client import SqlClient
from utils import get_post_image_url

### On set les chemins d'accès et le prettyprinter. ###
pp = pprint.PrettyPrinter(indent=2)
comments_model_path = os.path.join(os.path.dirname(__file__), './models/comments.model')
biographies_model_path = os.path.join(os.path.dirname(__file__), './models/biographies.model')
users_model_path = os.path.join(os.path.dirname(__file__), './models/users_sample.model')
config_path = os.path.join(os.path.dirname(__file__), './config.ini')

N_CLUSTERS = 3

class User(object):
	"""
	Classe utilisateur.
	"""

	def __init__(self):
		"""
		__init__ function.
		"""

		### L'utilisateur hérite de la classe `object`. ###
		super().__init__()

		### On charge les variables depuis le fichier de config. ###
		self.config = configparser.ConfigParser()
		self.config.read(config_path)
		
		self.username = ''

		### Instanciation du client SQL. ###
		
		self.n_clusters = N_CLUSTERS

		### Initialisation des features pour l'apprentissage. ###
		self.lastpost = 0
		self.frequency = 0
		self.engagement = 0
		self.followings = 0
		self.followers = 0
		self.usermentions = 0
		self.brandpresence = 0
		self.brandtypes = 0
		self.commentscore = 0

		### Paramètres de fonctions maths, pour ajustement de scores. ###
		self.K = 0.17
		self.K_ = 7
		self.B = 0.5

	def getUserNames(self, limit = 0):
		"""
		Récupère les usernames des utilisateurs annotés, sous la forme:

		[
			{"username": "foo"},
			{"username": "bar"},
			...
		]

		Args:
				limit (int) : La limite du nombre d'utilisateurs à retourner.

		Returns:
				(list) : la liste des noms d'utilisateur issus de la BDD.
		"""
		self.sqlClient = SqlClient()

		### Récupération des noms d'utilisateurs annotés. ###
		self.sqlClient.openCursor()
		allUsers = self.sqlClient.getUserNames(limit, labeled=True)
		self.sqlClient.closeCursor()
		return allUsers

	def getUserInfoIG(self):
		"""
		Récupération des critères de l'utilisateur via l'API d'Instagram.
		Utilisée lorsqu'on veut tester notre modèle en live, sur un utilisateur qui n'est pas forcément en base.

		Args:
				(none)

		Returns:
				(none)
		"""

		igusername = self.config['Instagram']['user']
		igpassword = self.config['Instagram']['password']

		### Connexion à l'API. ###
		self.InstagramAPI = InstagramAPI(igusername, igpassword)
		self.InstagramAPI.login()
		### On essaye d'extraire les features du profil Instagram. 								  					 ###
		### Si il y a une erreur, on pass (on ne veut pas break e script en cas de re-promptage). 					 ###
		### Les `time.sleep` préviennent des erreurs 503, dues à une sollicitation trop soudaine de l'API Instagram. ###

		if not os.path.isfile(os.path.join(comments_model_path)):
			print('Creating comments model...')

			### Crée le modèle de commentaires s'il n'existe pas. ###
			self.createCommentsModel()
		
		if not os.path.isfile(os.path.join(biographies_model_path)):
			print('Creating biographies model...')

			### Crée le modèle de biographies s'il n'existe pas. ###
			self.createBiographiesModel()

		### Charge le modèle de commentaires. ###
		self.comments_model = pickle.load(open(comments_model_path, 'rb'))

		### Charge le modèle de biographies. ###
		self.count_vect, self.tfidf_transformer, self.clf = pickle.load(open(biographies_model_path, 'rb'))

		username = self.username

		### On initialise le temps de départ pour mesurer le temps d'exécution global. ###
		time_temp_start = time.time()

		### On questionne l'API à propos du nom d'utilisateur, cela nous retourne l'utilisateur en entier. ###
		self.InstagramAPI.searchUsername(username)
		user_server = self.InstagramAPI.LastJson['user']

		### On récupère le feed entier de l'utilisateur, afin d'analyser certaines métriques. ###
		self.InstagramAPI.getUserFeed(user_server['pk'])
		feed = self.InstagramAPI.LastJson['items']

		### On initialise les listes utiles pour l'étude. ###
		rates = list()
		timestamps = list()
		comment_scores = list()
		brpscs = list()
		colorfulness_list = list()
		dominant_colors_list = list()
		contrast_list = list()
		avglikes = list()
		avgcomments = list()

		### On affiche la longueur du feed retourné par l'API. ###
		print('Feed is %s post-long' % str(len(feed)))

		### On boucle sur le feed afin d'en extraire les données pertinentes pour le calcul de nos features. 					  ###
		### On prend 50 posts du feed pour ne pas avoir un temps d'éxécution trop long. 										  ###
		### TODO: demander à l'API de ne pas récupérer l'intégralité des posts de l'utilisateur, mais simplement les 50 premiers. ###
		for index, post in enumerate(feed):

			### On affiche l'état de progression de l'analyse. ###
			print('Post %s/%s...' %
					(index + 1, len(feed[:50])), end='\r', flush=True)

			### Si le serveur renvoie une erreur (notamment 503), on attend 1 minute avant de renvoyer une requête. ###
			### Ajout du nombre de likes et de commentaires pour moyenner sur le feed. ###
			avglikes.append(post['like_count'])
			avgcomments.append(post['comment_count'])

			### On ajoute le timestamp du post pour les analyses de fréquence. ###
			timestamps.append(int(post['taken_at']))

			### Si l'utilisateur n'a pas de followers, on considère que le taux d'engagement est 0 (au lieu d'infini). ###
			if user_server['follower_count'] == 0:
				engagement_rate = 0

			else:
				### Pourcentage du taux d'engagement. ###
				k = 100 / user_server['follower_count']

				### On distingue plusieurs cas: celui où il y a commentaires et likes, celui où il en manque un des deux, et celui où il n'y a rien. ###
				if 'like_count' in post:
					if 'comment_count' in post:
						engagement_rate = (
							int(post['like_count']) + int(post['comment_count'])) * k
					else:
						engagement_rate = int(post['like_count']) * k

				else:
					if 'comment_count' in post:
						engagement_rate = int(
							post['comment_count']) * k
					else:
						engagement_rate = 0

			### On ajoute le taux d'engagement du post à la liste de taux d'engagement. ###
			rates.append(engagement_rate)

			### On récupère le code binaire des images en BDD, et on y opère les traitements : ###
			### - STD du contraste															   ###
			### - STD de l'intensité colorimétrique											   ###
			### - Distorsion des clusters de couleur										   ###

			### Depuis le JSON de réponse de l'API, on récupère l'adresse URL de la plus petite image. ###
			url = get_post_image_url(post)

			### On fait une requête HTTP.GET sur l'adresse récupérée, puis on entrait les octets de l'image en réponse. ###
			response = requests.get(url)
			img = Image.open(BytesIO(response.content))

			### On convertit l'image en N&B pour l'étude du contraste. ###
			grayscale_img = img.convert('LA')

			### On ajoute la couleur dominante du post pour une analyse colorimétrique. ###
			most_dominant_colour = self.getMostDominantColour(img)
			dominant_colors_list.append(most_dominant_colour)

			### On récupère le taux de colorité de l'image, qu'on ajoute à la liste globale si cette première n'est pas nan. ###
			colorfulness = self.getImageColorfulness(img)
			colorfulness_list.append(colorfulness)

			### On récupère le taux de contraste de l'image, qu'on ajoute à la liste globale si cette première n'est pas nan. ###
			contrast = self.getContrast(grayscale_img)
			if not math.isnan(contrast):
					contrast_list.append(contrast)


			### Fetch les marques détectées dans les posts. ###
			brpsc = self.getBrandPresence(post)
			if brpsc:
				brpscs.extend(brpsc)

			### On récupère le score de commentaires sur tout le feed de l'utilisateur. ###
			self.InstagramAPI.getMediaComments(str(post['id']))
			comments_server = self.InstagramAPI.LastJson

			#time.sleep(1)

			### On cherche tous les commentaires retournés dans la variable `comments_server`. ###
			if 'comments' in comments_server:

					for comment in comments_server['comments']:
						### On ne prend que les 10 premier commentaires pour chaque post. ###
						if len(comment_scores) > 10:
							break

						### Si la personne qui commente est l'auteur du post, alors on ignore le commentaire. ###
						if comment['user']['username'] == self.username:
							continue

						score = self.getCommentScore(comment['text'])
						comment_scores.append(score)

						#time.sleep(1)

		### Assignation des critères et affichage des résultats. ###
		if len(rates) > 0:
			avg = mean(rates)
			self.lastpost = time.time() - max(timestamps)
			self.frequency = self.calculateFrequency(len(feed), min(timestamps))
			self.engagement = avg
			self.avglikes = mean(avglikes) if len(avglikes) > 1 else 0
			self.avgcomments = mean(avgcomments) if len(avgcomments) > 1 else 0
			self.followings = int(user_server['following_count'])
			self.followers = int(user_server['follower_count'])
			self.usermentions = int(user_server['usertags_count'])
			self.nmedias = int(user_server['media_count'])
			self.brandpresence = brpscs
			self.brandtypes = self.getBrandTypes(brpscs)
			self.commentscore = mean(comment_scores) * (1 + stdev(comment_scores)) if len(comment_scores) > 1 else 0
			self.biographyscore = self.getBiographyScore(user_server['biography'])
			self.colorfulness_std = stdev(colorfulness_list) if len(colorfulness_list) > 1 else 0
			self.contrast_std = stdev(contrast_list) if len(contrast_list) > 1 else 0
			self.colors = [[color.lab_l, color.lab_a, color.lab_b] for color in dominant_colors_list]
			self.codes, self.color_distorsion = scipy.cluster.vq.kmeans(np.array(self.colors), self.n_clusters)
			self.colors_dispersion = self.calcCentroid3d(self.colors)

			print('Username : %s' % self.username)
			print('Last post: %s' % self.uiGetIlya(max(timestamps)))
			print('Frequency: %.2f' % float(self.frequency))
			print('Engagement: %.2f%%' % float(self.engagement))
			print('Average like count: %.2f' % float(self.avglikes))
			print('Average comment count: %.2f' % float(self.avgcomments))
			print('N followings: %s' % self.uiFormatInt(self.followings))
			print('N followers: %s' % self.uiFormatInt(self.followers))
			print('User mentions: %s' %self.uiFormatInt(self.usermentions))
			print('Brand presence: %s' % str(self.brandpresence))
			print('Brand types: %s' % str(self.brandtypes))
			print('Biography score: %s' % str(self.biographyscore))
			print('Comments score: %s' % str(self.commentscore))
			print('Colorfulness standard deviation: %s' % self.colorfulness_std)
			print('Contrast standard deviation: %s' % self.contrast_std)
			print('Overall color distorsion : %s' % str(self.color_distorsion))
			print('\nFeature extraction ended in %.2fs seconds' % (float(time.time() - time_temp_start)))

		else:
			print('This user has no posts !')

	def getUserInfoSQL(self):
		"""
		On récupère les posts de l'utilisateur à partir de la BDD, et on en extrait les features nécessaires pour l'apprentissage.
		L'intérêt de cette méthode est qu'on peut solliciter la BDD très vite par rapport à l'API Instagram, ce qui nous permet de faire un
		apprentissage 'rapide'!
		La méthode est cependant très similaire à `self.getUserInfoIG()`.

				Args:
						(none)

				Returns:
						(none)
		"""
		self.sqlClient = SqlClient()

		self.sqlClient.openCursor()
		posts = self.sqlClient.getUserPosts(self.username)

		###	Initialisation des listes de stockage pour les métriques. ###
		rates = list()
		timestamps = list()
		comment_scores = list()
		brpscs = list()
		colorfulness_list = list()
		dominant_colors_list = list()
		contrast_list = list()
		avglikes = list()
		avgcomments = list()

		if not os.path.isfile(os.path.join(comments_model_path)):
			print('Creating comments model...')

			### Crée le modèle de commentaires s'il n'existe pas. ###
			self.createCommentsModel()
		
		if not os.path.isfile(os.path.join(biographies_model_path)):
			print('Creating biographies model...')

			### Crée le modèle de biographies s'il n'existe pas. ###
			self.createBiographiesModel()

		### Charge le modèle de commentaires. ###
		self.comments_model = pickle.load(open(comments_model_path, 'rb'))

		### Charge le modèle de biographies. ###
		self.count_vect, self.tfidf_transformer, self.clf = pickle.load(open(biographies_model_path, 'rb'))

		for index, post in enumerate(posts):

			avglikes.append(post['n_likes'])
			avgcomments.append(post['n_comments'])

			### Timestamps et taux d'engagement: métriques immédiates. ###
			timestamps.append(int(post['timestamp']))

			if post['n_follower'] == 0:
				engagement_rate = 0

			else:
				k = 100 / post['n_follower']

				if 'n_likes' in post:

					if 'n_comments' in post:
						engagement_rate = (
							int(post['n_likes']) + int(post['n_comments'])) * k
					else:
						engagement_rate = int(post['n_likes']) * k

				else:
					if 'n_comments' in post:
						engagement_rate = int(post['n_comments']) * k
					else:
						engagement_rate = 0
			rates.append(engagement_rate)

			### On récupère le code binaire des images en BDD, et on y opère les traitements : ###
			### - STD du contraste															   ###
			### - STD de l'intensité colorimétrique											   ###
			### - Distorsion des clusters de couleur										   ###
			img = post['image']

			if img:

				### On essaye d'avoir les images des posts afin de les traiter automatiquement et en extraire les features. ###
				### Si erreur il y a, on passe à la suivante sans breaker le script.										###
				try:
					### On récupère les octets de l'image. ###
					img = Image.open(BytesIO(img))
					### On convertit l'image en N&B pour l'étude du contraste. ###
					grayscale_img = img.convert('LA')

					### On ajoute la couleur dominante du post pour une analyse colorimétrique. ###
					most_dominant_colour = self.getMostDominantColour(img)
					dominant_colors_list.append(most_dominant_colour)

					### On récupère le taux de colorité de l'image, qu'on ajoute à la liste globale si cette première n'est pas nan. ###
					colorfulness = self.getImageColorfulness(img)
					if not math.isnan(colorfulness):
						colorfulness_list.append(colorfulness)

					### On récupère le taux de contraste de l'image, qu'on ajoute à la liste globale si cette première n'est pas nan. ###
					contrast = self.getContrast(grayscale_img)
					if not math.isnan(contrast):
						contrast_list.append(contrast)
				except Exception as e:
					print('Error while trying to retrieve %s\'s image n°%s : %s' % (
						str(self.username), str(index), e))
					pass

			### Pour l'instant on ne s'en sert pas, à ré-utiliser quand on s'intéressera à la détection des placements de produits. ###
			"""
			brpsc = self.getBrandPresence(post)
			if brpsc:
				brpscs.extend(brpsc)
			"""
			# On récupère les commentaires depuis la BDD, grâce à l'ID du post.
			self.sqlClient.openCursor()
			comments = self.sqlClient.getComments(str(post['id_post']))
			self.sqlClient.closeCursor()

			### On parcourt les commentaires du post pour en extraire le "score de commentaires". ###
			for comment in comments:
				if comment['user_id'] == post['id_user']:
					continue
				score = self.getCommentScore(comment['comment'])
				comment_scores.append(score)

			biography_score = self.getBiographyScore(post['biography'])

			### Si le nombre de commentaires est trop bas, on affecte des valeurs particulières.  ###
			### En effet, la variance d'une VA prend en arguments deux points de données minimum. ###
			if len(comment_scores) > 1:
				commentscore = mean(comment_scores) * \
					(1 + stdev(comment_scores))
			elif len(comment_scores) == 1:
				commentscore = comment_scores[0]
			else:
				commentscore = 0

		### Dernière phase: on affecte les variables d'instance (= features) une fois que tous les critères ont été traités. ###
		if len(rates) > 1:
			avg = mean(rates)
			self.engagement = avg
			self.avglikes = mean(avglikes) if len(avglikes) > 1 else 0
			self.avgcomments = mean(avgcomments) if len(avgcomments) > 1 else 0
			self.lastpost = time.time() - max(timestamps)
			self.frequency = self.calculateFrequency(len(posts), min(timestamps))
			self.followings = int(posts[0]['n_following'])
			self.followers = int(posts[0]['n_follower'])
			self.usermentions = int(posts[0]['n_usertags'])
			self.nmedias = int(posts[0]['n_media'])
			self.brandpresence = brpscs
			self.brandtypes = self.getBrandTypes(brpscs)
			self.commentscore = commentscore
			self.biographyscore = biography_score
			self.colorfulness_std = stdev(colorfulness_list) if len(colorfulness_list) > 1 else 0
			self.contrast_std = stdev(contrast_list) if len(contrast_list) > 1 else 0
			self.colors = [[color.lab_l, color.lab_a, color.lab_b] for color in dominant_colors_list]

			### Ici, on cherche à avoir la distorsion des k-means des couleurs du feed. 						###
			### Parfois, on peut avoir que une ou deux couleurs outputées du k-mean.                            ###
			### Si on a une erreur, on baisse le nombre de clusters jusqu'à ce que le k-mean puisse être opéré. ###

			while True:
				try:
					if (self.n_clusters == 0):
						break
					self.codes, self.color_distorsion = scipy.cluster.vq.kmeans(
						np.array(self.colors), self.n_clusters)
				except Exception as e:
					self.n_clusters = self.n_clusters - 1
					continue
				break
			self.label = int(post['label'])
			self.testset = post['test_set']

		else:
			print('This user has no posts !')

	def uiFormatInt(self, n):
		"""
		Conversion du nombre de followers/abonnements en K (mille) et M (million).

		Args:
				n (int) : nombre à convertir en format souhaité.

		Returns:
				(str) Un string formatté.
		"""

		if n > 1000000:
			return '{:.1f}M'.format(n / 1000000)
		elif n > 1000:
			return '{:.1f}K'.format(n / 1000)
		return str(n)

	def uiGetIlya(self, _time):
		"""
		Génération du string (exemple) :
		Il y a 15 jours, 0 heure, 36 minutes et 58 secondes.

		Args:
				_time (int) le temps en format POSIX.

		Returns:
				(str) Un string formatté.
		"""

		### Différence de time POSIX (donc des secondes) entre le temps considéré, et la date actuelle. ###
		ilya = math.floor(time.time() - _time)

		### Définition des mutliplicateurs jours, heures, secondes. ###
		days_mult = 60 * 60 * 24
		hours_mult = 60 * 60
		minutes_mult = 60

		### Conversion et troncage des jours, heures, secondes pour le formatttage en chaine de caractère. ###
		days = ilya // days_mult
		hours = (ilya - days * days_mult) // hours_mult
		minutes = (ilya - days * days_mult -
				   hours * hours_mult) // minutes_mult
		seconds = ilya % minutes_mult

		### On retourne les valeurs en prenant en compte les singuliers et pluriels. ###
		return '%s day%s, %s hour%s, %s minut%s, %s second%s' % (days, '' if days in [0, 1] else 's', hours, '' if hours in [0, 1] else 's', minutes, '' if minutes in [0, 1] else 's', seconds, '' if seconds in [0, 1] else 's')

	def calculateFrequency(self, n, min_time):
		"""
		Calcul de la fréquence de post.

		Args:
				n (int) : le nombre de posts à considérer dans l'intervalle de temps donné.
				min_time (int) : le plus vieux post, à comparer avec la date actuelle.

		Returns:
				(int) La fréquence de post.
		"""

		### Différence de time POSIX (donc des secondes) entre le post le plus ancien, et la date actuelle. ###
		ilya = math.floor(time.time() - min_time)

		### Calcul de la fréquence de post. ###
		days = ilya // (60 * 60 * 24)
		days = days if days != 0 else 1
		return float(n / days)

	def calcCentroid3d(self, _list):
		"""
		Calcul des distances de tous les points au barycentre des points de couleur dans le repère lab*.

		Args:
				_list ((int * 3)[]) : liste de points 3D dont on veut calculer le barycentre.

		Returns:
				(int) La distance moyenne de tous les points du nuage au barycentre de ce dernier.
		"""

		arr = np.array(_list)
		length = arr.shape[0]
		sum_x = np.sum(arr[:, 0])
		sum_y = np.sum(arr[:, 1])
		sum_z = np.sum(arr[:, 2])

		### Calcul des coordonnées du barycentre. ###
		centroid = np.array([sum_x/length, sum_y/length, sum_z/length])

		### Calcul des distances de tous les points au barycentre. ###
		distances = [np.linalg.norm(data - centroid) for data in _list]
		return float(mean(distances))

	def getMostDominantColour(self, image):
		"""
		Retourne la couleur dominante de l'image.

				Args:
						image (Image PIL) : l'image qu'on considère pour l'étude.

				Returns:
						(tuple) La couleur dominante de l'image dans le repère lab*.
		"""

		### Définition du nombre de clusters pour les pixels. ###
		NUM_CLUSTERS = 5

		### On resize l'image pour que les temps de traitement soient réduits. ###

		ar = np.array(image)
		shape = ar.shape
		ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

		### On opère un K-mean sur les pixels de l'image. ###
		codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
		vecs, dist = scipy.cluster.vq.vq(ar, codes)
		counts, bins = scipy.histogram(vecs, len(codes))
		index_max = scipy.argmax(counts)

		### La couleur la plus importante de l'image, déduite du décompte de l'histogramme des couleurs. ###
		peak = codes[index_max]

		### Conversion de la couleur RGB dans l'espace lab*. ###
		rgb = sRGBColor(*peak)
		return convert_color(rgb, LabColor)

	def getImageColorfulness(self, image):
		"""
		Retourne l'intensité colorimétrique de l'image.

				Args:
						image (Image PIL) : l'image qu'on considère pour l'étude.

				Returns:
						(int) L'intensité colorimétrique de l'image.
		"""

		ar = np.array(image)

		### Transforme l'image pour OpenCV. ###
		open_cv_image = ar[:, :, ::-1].copy()

		### Performe une analyse des composantes RGB de l'image. ###
		B, G, R, *A = cv2.split(open_cv_image.astype("float"))
		rg = np.absolute(R - G)
		yb = np.absolute(0.5 * (R + G) - B)
		(rbMean, rbStd) = (np.mean(rg), np.std(rg))
		(ybMean, ybStd) = (np.mean(yb), np.std(yb))
		stdRoot = np.sqrt((rbStd ** 2) + (ybStd ** 2))
		meanRoot = np.sqrt((rbMean ** 2) + (ybMean ** 2))
		return float(stdRoot + (0.3 * meanRoot))

	def getContrast(self, img):
		"""
		Retourne le contraste global de l'image en passant par un calcul d'entropie.

				Args:
					img (Image PIL) : l'image N&B qu'on considère pour l'étude (matrice d'entiers allant de 0 à 255).
				
				Returns:
					(int) Le contraste de l'image.
		"""

		### Transforme l'image pour OpenCV. ###
		ar = np.array(img)

		### Histogramme de l'image (niveaux de gris). ###
		hist = np.histogram(ar)
		data = hist[0]

		### Normalisation de l'histogramme. ###
		data = data / data.sum()

		### On retourne le calcul de l'entropie. ###
		return float(- (data * np.log(np.abs(data))).sum())

	def getBrandPresence(self, post):
		"""
		Retourne les mentions utilisateur qui matchent avec les utilisateurs mentionnés dans la description du post.
		
				Args:
					post (dict) : un post Instagram sous forme de dictionnaire.

				Returns:
					(str[]) Le tableau contenant les marques détectées.
		"""

		### Définition de la liste de stockage des marques. ###
		brands = list()

		### On essaye de voir s'il y a des marques dans le champ du post. 									  ###
		### Pour cela, on compare les mentions utilisateurs dans la description du post :                     ###
		### Les mentions dans la descriptions sont activées par un '@utilisateur'.                            ###
		### On compare ces dernières avec les utilisateurs tagués sur la photo.                               ###
		### Si les deux existent, on considère que l'utilisateur a cherché à mettre le profil tagué en avant. ###
		### S'il n'y a pas de marques, on a une erreur; on pass. 		                                      ###
		try:
			text = post['caption']['text']

			### On ajoute un '@' pour matcher avec les mentions trouvées dans la description du post. ###
			if hasattr(post, 'usertags'):
				usertags = ['@%s' % user['user']['username'] for user in post['usertags']['in']]

				### On match les mentions utilisateur dans la description du post. ###
				matches = regex.findall(r'@[\w\.]+', text)

				### Si il y a un utilisateur qui se retrouve à la fois tagué sur la photo et en description du post, alors on l'extrait. 			###
				### Ce modèle est perfectible, on peut aussi décider de s'occuper uniquement des personnes taguées et/ou des personnes mentionnées. ###
				for match in matches:
					if match in usertags:
						brands.append(match.split('@')[1])
			
			return brands

		except:
			pass

	def getBrandTypes(self, brands):
		"""
		Retourne les types de business que sont les 'marques' mentionnées à la fois dans la description du post et en mention utilisateur.

				Args:
					brands (str[]) : le tableau des utilisateurs détectés.
				
				Returns:
					(Counter) Le compteur de types de profils utilisateur (Blog, Photographe, Acteur, etc.), si le type de compte est 'Business' seulement.
		"""

		### Définition du compteur de marques. ###
		brand_counter = Counter()

		### On itère sur les noms de marques. ###
		for brand in brands:

			### On récupère le type de compte (si le compte est de type 'Business' seulement). ###
			self.InstagramAPI.searchUsername(brand)
			brand_full = self.InstagramAPI.LastJson['user']

			### Si l'utilisateur est 'Business'. ###
			if 'category' in brand_full:
				brand_counter[brand_full['category']] += 1
		return brand_counter
	
	def getBiographyScore(self, bio):
		"""
		Retourne le score de biographie basé sur le modèle de biographies.
		
				Args:
					comment (str): la biographie sous forme de texte.
				
				Returns:
					(int) Le score de qualité de biographie.
		"""

		if not os.path.isfile(os.path.join(biographies_model_path)):
			print('Creating biographies model...')

			### Crée le modèle de biographies s'il n'existe pas. ###
			self.createBiographiesModel()

		self.count_vect, self.tfidf_transformer, self.clf = pickle.load(open(biographies_model_path, 'rb'))

		X_test_counts = self.count_vect.transform([bio])
		self.X_test_tfidf = self.tfidf_transformer.transform(X_test_counts)

		pred = self.clf.predict_proba(self.X_test_tfidf)[0][1]
		return float(pred)

	def getCommentScore(self, comment):
		
		"""
		Retourne le score de commentaire basé sur le modèle de commentaires.
		Les commentaire les plus pertinents pour une photo (= dont les mots importants sont peu utilisés dans le modèle de commentaires) sont privilégiés.
		Les commentaires les plus longs sont privilégiés.
		
				Args:
					comment (str): le commentaire texte.
				
				Returns:
					(int) Le score de qualité de commentaire, situé entre 0 et 1.
		"""

		### Pickle le modèle (dictionnaire de mots contenus dans les commentaires + leurs occurences) pour ne pas avoir à le générer à chaque run. ###
		

		### Liste des scores de commentaires. ###
		word_scores = list()

		### Regex pour attraper les mots dans différents alphabets, dont les emojis. ###
		for word in regex.compile(r'[@#\p{L}_\u263a-\U0001f645]+').findall(comment):

			### Pré-process le mot. ###
			_word = self.processWordComment(word)

			if _word:

				### Attribue un score de commentaire inversement proportionnel à ses occurences dans tous les commentaires de la BDD. ###
				if self.comments_model[_word] > 0:
					word_score = 1 / self.comments_model[_word]

				else:
					word_score = 1
				word_scores.append(word_score)
		
		### S'il n'y a pas de mots, on attribue 0 pour le commentaire. ###
		### Sinon, on prend la moyenne. 							   ###
		if len(word_scores) > 0:
			comment_score = mean(word_scores)
		else:
			comment_score = 0

		### On mutliplie le score de commentaires par des composantes paramétriques: on privilégie d'abord les commentaires les plus longs. ###
		k = 1 - math.exp(- self.K * len(word_scores))

		### Ensuite, on privilégie les commentaires qui on des mots dont l'écart-type des scores est important. 					    ###
		### La raison derrière cela, est que les stop-words sont des mots qui vont forcément avoir un score faible.                     ###
		### De ce fait, si les mots-clés du commentaire sont 'importants' = si leur score est élevé, alors l'écart-type sera important. ###
		j = 1 / (1 + math.exp(- self.K_ * (stdev(word_scores) - self.B))
				 ) if len(word_scores) > 1 else 0

		return k * j * comment_score * len(word_scores)

	def createCommentsModel(self):
		"""
		Crée le modèle de commentaires.

				Args:
					(none)
				
				Returns:
					(none)
		"""

		self.sqlClient = SqlClient()

		### Récupère tous les commentaires en base. ###
		self.sqlClient.openCursor()
		comments = self.sqlClient.getAllComments()
		self.sqlClient.closeCursor()

		### Déclaration des variables locales pour les compteurs. ###
		comment_count = Counter()
		i = 0
		j = 0

		### On boucle sur les commentaires et on affiche la progression avec TQDM. ###
		for comment in tqdm(comments):
			comment = str(comment)

			### Trouve tous les mots, dont les emojis et les caractères de différents alphabets. ###
			wordArray = regex.compile(
				r'[@#\p{L}_\u263a-\U0001f645]+').findall(comment)
			length = len(wordArray)

			### Pour chaque mot trouvé, on le préprocess. ###
			for word in wordArray:
				_word = self.processWordComment(word)

				### Ajoute au compteur non pas l'occurence simple du mot, mais dans quel contexte celui-là apparaît (se trouve-t-il dans une phrase longue ou courte ?). ### 
				if _word:
					i += 1
					comment_count[_word] += 1 / length
				else:
					j += 1
		print('Éléments considérés : %s' % str(i))
		print('Éléments non considérés : %s' % str(j))

		### Sauvegarde le modèle dans le dossier models. ###
		with open(os.path.join(comments_model_path), 'wb') as outfile:
			pickle.dump(comment_count, outfile)

	def createBiographiesModel(self):
		"""
		Crée le modèle de commentaires.

				Args:
					(none)
				
				Returns:
					(none)
		"""

		self.sqlClient = SqlClient()

		### Récupère toutes les biographies des utilisateurs annotés. ###
		self.sqlClient.openCursor()
		response = self.sqlClient.getAllBiographies()
		self.sqlClient.closeCursor()

		### Récupération des champs biographies, et labels. ###
		bios = [row['biography'] for row in response]
		labels = [row['label'] for row in response]
		
		### Construction du modèle TF-IDF et apprentissage d'un classifieur calibré pour sortir des probabilités. ###
		### Vecteurs de comptage. ###
		self.count_vect = CountVectorizer()
		X_train_counts = self.count_vect.fit_transform(bios)

		### Transformateur TF-IDF. ###
		self.tfidf_transformer = TfidfTransformer()
		self.X_train_tfidf = self.tfidf_transformer.fit_transform(X_train_counts)

		### Entraînement du classificateur. ###
		oneVsRest = CalibratedClassifierCV()
		self.clf = oneVsRest.fit(self.X_train_tfidf, labels)

		### Sauvegarde du modèle. ###
		with open(os.path.join(biographies_model_path), 'wb') as outfile:
			pickle.dump((self.count_vect, self.tfidf_transformer, self.clf), outfile)

	def processWordComment(self, word):
		"""
		Pré-processe le commentaire.

				Args:
					word (str) : le mot.

				Return:
					(str) Le mot pré-processé.
		"""

		### On vérifie si le mot ne commence pas par un @ (mention) ou un # (hashtag). ###
		### On vérifie si le "mot" n'est pas une ponctuation. 						   ###
		if word[0] in ['#', '@'] or word in ['.', '!', '?', ',', ':', ';', '-', '+', '=', '/', '&', '@', '$', '_']:
			word = None

		else:
			try:
				### Ici ça pète quand il y a du russe ou des emojis. ###
				word = str(word).lower()
			except:
				word = word
		return word

	def cleanNonExistingUsers(self):
		"""
		Supprime les utilisateurs en base qui ont changé de nom/n'existent plus.

				Args:
					None
				
				Returns:
					None
		"""
		self.sqlClient = SqlClient()

		self.sqlClient.openCursor()
		usernames = self.sqlClient.getUserNames(0)
		self.sqlClient.closeCursor()

		self.InstagramAPI = InstagramAPI(self.config['Instagram']['user'], self.config['Instagram']['password'])
		self.InstagramAPI.login()

		for username in tqdm(usernames):

			self.InstagramAPI.searchUsername(username['user_name'])
			user_server = self.InstagramAPI.LastJson

			if user_server['status'] == 'fail':
				self.sqlClient.openCursor()
				self.sqlClient.setLabel(username['user_name'], '-2')
				self.sqlClient.closeCursor()
			
			time.sleep(1)

	def testCommentScore(self):
		"""
		Tooling permettant de tester les scores des commentaires utilisateur.

				Args:
					(none)
				
				Returns:
					(none)
		"""

		while True:

			### L'utilisateur rentre un nom de compte Instagram pour tester le modèle de commentaires. ###
			text = input(
				'Comment and I will tell your score ! (type \'exit\' to go next) : ')

			### L'utilisateur entre "exit" pour sortir de la boucle. ###
			if text == 'exit':
				break
			
			### Sort le score de commentaires pour l'utilisateur en question. ###
			else:
				comment_score = self.getCommentScore(text)
				print(text)
				print(comment_score)
