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
import sys
import os
import pickle
import random
import argparse
import math
from itertools import chain

### Installed libs. ###
import pprint
import pandas as pd
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, classification_report, roc_curve, auc
from sklearn.utils import shuffle
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
from tqdm import tqdm

sys.path.append(os.path.dirname(__file__))

### Custom libs. ###
from user import User
from sql_client import SqlClient

### Setup du PrettyPrinter, ainsi que des chemin d'accès aux fichiers. ###
pp = pprint.PrettyPrinter(indent = 2)

model_path = os.path.join(os.path.dirname(__file__), './models/classifier.model')
users_model_path = os.path.join(os.path.dirname(__file__), './models/users_sample.model')
labels_model_path = os.path.join(os.path.dirname(__file__), './models/labels.model')
dictvec_model_path = os.path.join(os.path.dirname(__file__), './models/dictvec.model')
ig_url = 'http://www.instagram.com/'

class Trainer(object):
	"""
	Classe d'entraînement du modèle de détection des influenceurs.
	"""

	def __init__(self):
		"""
		__init__ function. On définit aussi les features que l'on va utiliser pour l'étude.
		"""

		super().__init__()
		self.key_features = [
			#'biographyscore', # Construit sur le même jeu d'entrainement que la classification actuelle, à éviter donc jusqu'à trouver une nouvelle solution.
			'commentscore',
			'avglikes',
			'avgcomments',
			'engagement',
			'followers',
			'followings',
			'nmedias',
			'frequency',
			'usermentions',
			'colorfulness_std',
			'color_distorsion',
			'contrast_std',
			'category',
			'is_verified'
		]

		self.features_array_train = list()
		self.features_array_test = list()
		self.labels_train = list()
		self.labels_test = list()
		self.users_array = list()

	def buildUsersModel(self):
		"""
		Construit la liste des utilisateurs utile pour l'entrainement, avec les features correspondantes.

				Args:
					(none)
				Returns:
					(none)
				
		"""

		self.sqlClient = SqlClient()

		### On récupère toutes les features nécessaires pour entraîner le modèle. ###
		self.user_model = User()

		### `users` est une liste de dictionnaires de type [{user_name: "toto"}, {user_name: "valberthe"}, ...]. ###
		### `users_array` est une liste de noms d'utilisateurs : ["toto", "valberthe", ...].                     ###
		users = self.user_model.getUserNames()

		users_array = [user['user_name'] for user in users]

		### Si le modèle d'utilisateurs existe déjà, on l'ouvre. ###
		if os.path.isfile(users_model_path):
			with open(users_model_path, 'rb') as f:
				self.users_array = pickle.load(f)

		### On parcourt le tableau des utilisateurs pour leur assigner les features. ###
		for user in tqdm(users):

			### Si l'utilisateur se trouve déjà dans le teableau, on n'a pas à réeffectuer le traitement. ###
			if user['user_name'] in [_user['username'] for _user in self.users_array]:
				continue

			self.user_model.username = user['user_name']

			### Récupère les features via la classe User. ###
			self.user_model.getUserInfoSQL()
			item = {
				'avglikes': self.user_model.avglikes,
				'avgcomments': self.user_model.avgcomments,
				'category': self.user_model.category,
				'color_distorsion': self.user_model.color_distorsion,
				'colorfulness_std': self.user_model.colorfulness_std,
				'contrast_std': self.user_model.contrast_std,
				'lastpost': self.user_model.lastpost,
				'username': self.user_model.username,
				'frequency': self.user_model.frequency,
				'engagement': self.user_model.engagement,
				'followings': self.user_model.followings,
				'followers': self.user_model.followers,
				'nmedias': self.user_model.nmedias,
				'usermentions': self.user_model.usermentions,
				'brandpresence': self.user_model.brandpresence,
				'brandtypes': self.user_model.brandtypes,
				'commentscore': self.user_model.commentscore,
				'biographyscore': self.user_model.biographyscore,
				'is_verified': self.user_model.is_verified,
				'label': self.user_model.label,
				'testset': self.user_model.testset,
			}
			self.users_array.append(item)

			### Sauvegarde du modèle d'utilisateurs. ###
			with open(users_model_path, 'wb') as f:
				pickle.dump(self.users_array, f)

		self.users_array = [user for user in self.users_array if user['username'] in users_array]

		features_dict = [{key: user[key] for key in self.key_features} for user in self.users_array]

		### Assignation de la liste des features en tant que liste, et les labels correspondants. ###
		self.dictvec = DictVectorizer()
		self.dictvec.fit(features_dict)

		### Sauvegarde le modèle du vectorisateur de dico. ###
		with open(dictvec_model_path, 'wb') as f:
			pickle.dump(self.dictvec, f)

		for user in self.users_array:

			### On n'a pas besoin de filtrer de nouveau les champs ici: le DictVec s'en charge! ###
			### S'il ne connait pas un champ, il l'ignore. 									    ###
			features_list = self.dictvec.transform(user).toarray().flatten()

			if user['testset']:
				self.features_array_test.append(features_list)
				self.labels_test.append(user['label'])

			else:
				self.features_array_train.append(features_list)
				self.labels_train.append(user['label'])
		
	def alterUsersModel(self):
		"""
		Au lieu de reconstruire le modèle d'utilisateurs à chaque fois, on change juste un champ pour des modifications occasionnelles.

				Args:
					(none)
				Returns:
					(none)
		"""
		
		self.sqlClient = SqlClient()
		self.user_model = User()

		### Charge le tableau des utilisateurs dont les features sont déjà extraites. ###
		if os.path.isfile(users_model_path):
			with open(users_model_path, 'rb') as f:
				users_array = pickle.load(f)

		adjusted_users = list()

		for user in tqdm(users_array):
			
			self.sqlClient.openCursor()
			userserver = self.sqlClient.getUser(user['username'])
			self.sqlClient.closeCursor()

			user['is_verified'] = userserver['is_verified']
			adjusted_users.append(user)
			
		with open(users_model_path, 'wb') as f:
			pickle.dump(adjusted_users, f)

	def train(self):
		"""
		Entraînement du modèle de classification.
		
			Args:
				(none)
			
			Returns:
				(none)
		"""

		### Définition du classifieur de type Random Forest à 500 estimateurs. ###
		self.clf = RandomForestClassifier(n_estimators = 500)

		### On entraîne le classifieur avec le set d'entraînement (jusqu'à l'index n_split). ###
		self.clf.fit(self.features_array_train, self.labels_train)

		### On peut avoir l'importance des features dans la décision de la classification. ###
		importance = self.clf.feature_importances_

		### Score de la classification. ###
		scores = cross_val_score(
			self.clf,
			self.features_array_train + self.features_array_test,
			self.labels_train + self.labels_test,
			cv = 5
		)
		print("\nAccuracy: %0.2f (+/- %0.2f)\n" % (scores.mean(), scores.std() * 2))

		### On calcule une prédiction pour la matrice de confusion et le rapport de classification. ###
		pred = self.clf.predict(self.features_array_test)
		print(confusion_matrix(self.labels_test, pred))
		print('\n')

		### On affiche l'importance des critères de classification. ###
		categories_total = 0
		for couple in zip(self.dictvec.get_feature_names(), importance):
			### Malheureusement lorsqu'on boucle là dessus on a l'importance de chaque type de catégories... ###
			### Pour n'afficher que les catégories au global, on fait un test sur les features names.        ###
			if 'category=' in couple[0]:
				categories_total += couple[1]
				continue
			print('    %s: %s' % (str(couple[0]), '%.2f%%' % float(100 * couple[1])))
		print('    %s: %s' % ('category', '%.2f%%' % float(100 * categories_total)))
		print('\n')

		print(classification_report(self.labels_test, pred))

		### Affichage des faux positifs et faux négatifs pour observer quels influenceurs sont mal détectés. ###
		#self.displayFPFN(pred)

		### Génération des probabilités (et non du vote à majorité) du Random Forest
		y_score = self.clf.predict_proba(self.features_array_test)
		pred2 = [predclass[1] for predclass in y_score]

		### Construction de la courbe ROC. ###
		fpr, tpr, _ = roc_curve(self.labels_test, pred2)
		### Aire sous la courbe. ###
		roc_auc = auc(fpr, tpr)

		### Affichage de la courbe ROC. ###
		plt.figure()
		lw = 2
		plt.plot(fpr, tpr, color='darkorange', lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
		plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
		plt.xlim([0.0, 1.0])
		plt.ylim([0.0, 1.05])
		plt.xlabel('False Positive Rate')
		plt.ylabel('True Positive Rate')
		plt.title('Receiver operating characteristic example')
		plt.legend(loc="lower right")
		plt.show()

		### Sauvegarde le classifieur en tant que modèle. ###
		with open(model_path, 'wb') as __f:
			pickle.dump(self.clf, __f)
		
	def displayFPFN(self, preds):
		"""
		Affiche les faux positifs et les faux négatifs pour une étude plus poussée des erreurs.

				Args:
					preds (int[]): : une liste des valeurs prédites.

				Returns:
					(none)
		"""

		### On instancie les listes des faux positifs et des faux négatifs. ###
		fp = list()
		fn = list()

		### On parcourt le tableau des prédictions pour obtenir les faux positifs et les faux négatifs. ###
		for index, pred in enumerate(preds):

			### Faux positifs. ###
			if pred == 1 and self.labels[self.n_split:][index] == 0:
				fp.append(self.users_array[self.n_split:][index]['username'])
			if pred == 0 and self.labels[self.n_split:][index] == 1:
				fn.append(self.users_array[self.n_split:][index]['username'])
		
		print('\nFaux positifs:\n\n')
		pp.pprint(fp)
		print('\n\nFaux négatifs:\n\n')
		pp.pprint(fn)

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
			self.clf = pickle.load(f)
		
		### Ouvre le modèle DictVec. ###
		with open(dictvec_model_path, 'rb') as f:
			self.dictvec = pickle.load(f)

			### L'utilisateur entre un nom de profil Instagram afin d'utiliser le modèle de classification, et estimer si cette personne est un influenceur ou non. ###
			while True:
				username = input('Username: ')
				user = User()
				user.username = username
				user.getUserInfoIG()

				try:
					features_dict = {key: user.__dict__[key] for key in self.key_features}
					features_array = self.dictvec.transform(features_dict)

					### Prédiction. ###
					pred = self.clf.predict(features_array)
					y_score = self.clf.predict_proba(features_array)
					print('Result:\n\n%s\nScore: %.2f%%\n' % ('Influencer !' if pred == 1 else 'Not an influencer.', float(y_score[0][1] * 100)))
				
				except Exception as e:
					print(e)
					print('The user doesn\'t exist or has a private account. Please try again.')
					pass

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--alter-users', action = 'store_true')
	args = parser.parse_args()

	trainer = Trainer()
	if args.alter_users:
		trainer.alterUsersModel()
	
	trainer.buildUsersModel()
	trainer.train()