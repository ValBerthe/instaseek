### System libs. ###
import sys
import os
import pickle
import random
import math

### Installed libs. ###
import pprint
import pandas as pd
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.utils import shuffle
from tqdm import tqdm

sys.path.append(os.path.dirname(__file__))

### Custom libs. ###
from user import User

### Setup du PrettyPrinter, ainsi que des chemin d'accès aux fichiers. ###
pp = pprint.PrettyPrinter(indent = 2)

xl_path = os.path.join(os.path.dirname(__file__), '../res/iguserssample.xlsx')
model_path = os.path.join(os.path.dirname(__file__), '../models/classifier.model')
users_model_path = os.path.join(os.path.dirname(__file__), '../models/users_sample.model')
labels_model_path = os.path.join(os.path.dirname(__file__), '../models/labels.model')
ig_url = 'http://www.instagram.com/'

class Trainer(object):
	"""
	Classe d'entraînement du modèle de détection des influenceurs.
	"""

	def __init__(self, split_ratio = 0.8):
		"""
		__init__ function. On définit aussi les features que l'on va utiliser pour l'étude.
		"""

		super().__init__()
		self.key_features = [
			'commentscore', 
			'engagement',
			'followers',
			'followings',
			'frequency',
			'lastpost',
			'usermentions',
			'colorfulness_std',
			'color_distorsion',
			'contrast_std'
		]
		self.features_array = list()
		self.labels = list()
		self.split_ratio = split_ratio

	def buildUsersModel(self):
		"""
		Construit la liste des utilisateurs utile pour l'entrainement, avec les features correspondantes.

				Args:
					(none)
				Returns:
					(none)
				
		"""

		### On récupère toutes les features nécessaires pour entraîner le modèle. ###
		self.user_model = User()
		users = self.user_model.getUserNames()

		### Si le modèle d'utilisateurs existe déjà, on l'ouvre. ###
		if os.path.isfile(users_model_path):
			with open(users_model_path, 'rb') as f:
				users_array = pickle.load(f)
		else:
			users_array = []
		
		### Index du split. ###
		self.n_split = math.floor(self.split_ratio * len(users_array)) + 1

		### On parcourt le tableau des utilisateurs pour leur assigner les features. ###
		for user in tqdm(users):

			### Si l'utilisateur se trouve déjà dans le teableau, on n'a pas à réeffectuer le traitement. ###
			if user['user_name'] in [_user['username'] for _user in users_array]:
				continue
			self.user_model.username = user['user_name']

			### Récupère les features via la classe User. ###
			self.user_model.getUserInfoSQL()
			item = {
				'color_distorsion': self.user_model.color_distorsion,
				'colorfulness_std': self.user_model.colorfulness_std,
				'contrast_std': self.user_model.contrast_std,
				'lastpost': self.user_model.lastpost,
				'username': self.user_model.username,
				'frequency': self.user_model.frequency,
				'engagement': self.user_model.engagement,
				'followings': self.user_model.followings,
				'followers': self.user_model.followers,
				'usermentions': self.user_model.usermentions,
				'brandpresence': self.user_model.brandpresence,
				'brandtypes': self.user_model.brandtypes,
				'commentscore': self.user_model.commentscore,
				'label': self.user_model.label
			}
			users_array.append(item)

			### Sauvegarde du modèle d'utilisateurs. ###
			with open(users_model_path, 'wb') as f:
				pickle.dump(users_array, f)

		### Assignation de la liste des features en tant que liste, et les labels correspondants. ###
		for user in users_array:
			features = list()
			for key in self.key_features:
				features.append(user[key])
			self.features_array.append(features)
			self.labels.append(user['label'])
		
		### On mélange les résultats pour ne pas avoir toujours les mêmes répartitions coup sur coup. ###
		self.features_array, self.labels = shuffle(self.features_array, self.labels, random_state = 0)

	def train(self):
		"""
		Entraînement du modèle.
		
			Args:
				(none)
			
			Returns:
				(none)
		"""

		### Définition du classifieur de type Random Forest à 500 estimateurs. ###
		clf = RandomForestClassifier(n_estimators = 500)

		### On entraîne le classifieur avec le set d'entraînement (jusqu'à l'index n_split). ###
		clf.fit(self.features_array[:self.n_split], self.labels[:self.n_split])

		### On peut avoir l'importance des features dans la décision de la classification. ###
		importance = clf.feature_importances_

		### Score de la classification. ###
		score = clf.score(self.features_array[self.n_split:], self.labels[self.n_split:])
		print(score)

		### On calcule une prédiction pour la matrice de confusion et le rapport de classification. ###
		pred = clf.predict(self.features_array[self.n_split:])
		print('\n%s\n' % str(pred))
		print(confusion_matrix(self.labels[self.n_split:], pred))
		print('\n')

		### On affiche l'importance des critères de classification. ###
		for couple in zip(self.key_features, importance):
			print('________ %s' % str((couple[0], '%.2f%%' % float(100 * couple[1]))))
		print('\n')

		print(classification_report(self.labels[self.n_split:], pred))

		### Sauvegarde le classifieur en tant que modèle. ###
		with open(model_path, 'wb') as __f:
			pickle.dump(clf, __f)

	def classify_user(self):
		"""
		Classe un utilisateur Instagram selon le modèle déjà entraîné.

				Args:
					(none)
				
				Returns:
					(none)
		"""

		### Ouvre le modèle de classification. ###
		with open(model_path, 'rb') as f:
			clf = pickle.load(f)

			### L'utilisateur entre un nom de profil Instagram afin d'utiliser le modèle de classification, et estimer si cette personne est un influenceur ou non. ###
			while True:
				username = input('Username: ')
				user = User()
				user.username = username
				user.getUserInfoIG()
				vector = [[
					user.commentscore, 
					user.engagement,
					user.followers,
					user.followings,
					user.frequency,
					user.lastpost,
					user.usermentions,
					user.colorfulness_std,
					user.color_distorsion
				]]

				### Prédiction. ###
				pred = clf.predict(vector)
				print('%s' % ('Yes' if pred == 1 else 'No'))

if __name__ == "__main__":
	trainer = Trainer()
	trainer.buildUsersModel()
	trainer.train()









