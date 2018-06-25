import sys
import os
import pandas as pd
import pickle
import pprint

from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, classification_report
from tqdm import tqdm
from user import User

pp = pprint.PrettyPrinter(indent = 2)
sys.path.append(os.path.dirname(__file__))

xl_path = os.path.join(os.path.dirname(__file__), '../res/iguserssample.xlsx')
model_path = os.path.join(os.path.dirname(__file__), '../models/classifier.model')
users_model_path = os.path.join(os.path.dirname(__file__), '../models/users_sample.model')
labels_model_path = os.path.join(os.path.dirname(__file__), '../models/labels.model')
ig_url = 'http://www.instagram.com/'

class Trainer(object):
	def __init__(self):
		"""
		__init__ function
		"""
		super().__init__()
		self.key_features = ['commentscore', 'engagement', 'followers', 'followings', 'frequency', 'lastpost', 'usermentions', 'colorfulness_std', 'color_distorsion', 'contrast_std']

	def buildUsersModel(self):
		"""
		Construit la liste des utilisateurs utile pour l'entrainement, avec les features correspondantes 
		"""

		self.n_split = 70

		"""
		On récupère toutes les features nécessaires pour entraîner le modèle
		"""
		self.user_model = User()

		users = self.user_model.getUserNames()
		if os.path.isfile(users_model_path):
			with open(users_model_path, 'rb') as f:
				users_array = pickle.load(f)
		else:
			users_array = []

		for user in tqdm(users):
			if user['user_name'] in [_user['username'] for _user in users_array]:
				continue
			self.user_model.username = user['user_name']
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
			with open(users_model_path, 'wb') as f:
				pickle.dump(users_array, f)

		features_array = list()
		labels = list()
		for user in users_array:
			features = list()
			for key in self.key_features:
				features.append(user[key])
			features_array.append(features)
			labels.append(user['label'])

		# train classifier
		print(len(features_array))
		c = [1, 10, 15, 20, 30, 50, 100, 200, 300, 500]
		for n in c:
			clf = RandomForestClassifier(n_estimators = n)
			clf.fit(features_array[:self.n_split], labels[:self.n_split])
			importance = clf.feature_importances_
			score = clf.score(features_array[self.n_split:], labels[self.n_split:])
			print(score)
		pred = clf.predict(features_array[self.n_split:])
		print('\n%s\n' % str(pred))
		print(confusion_matrix(labels[self.n_split:], pred))
		print('\n')
		for couple in zip(key_features, importance):
			print('________ %s' % str((couple[0], '%.2f%%' % float(100 * couple[1]))))
		print('\n')
		print(classification_report(labels[self.n_split:], pred))
		with open(model_path, 'wb') as __f:
			pickle.dump(clf, __f)

	def train_model():
		self.n_split = 372
		with open(users_model_path, 'rb') as f:
			users_array = pickle.load(f)
			features_array = list()
			labels = list()
			for user in users_array:
				features = list()
				for key in key_features:
					features.append(user[key])
				features_array.append(features)
				labels.append(user['label'])

			# train classifier
			print(len(features_array))
			c = [1, 10, 15, 20, 30, 50, 100, 200, 300, 500]
			for n in c:
				clf = RandomForestClassifier(n_estimators = n)
				clf.fit(features_array[:self.n_split], labels[:self.n_split])
				importance = clf.feature_importances_
				score = clf.score(features_array[self.n_split:], labels[self.n_split:])
				print(score)
			pred = clf.predict(features_array[self.n_split:])
			print('\n%s\n' % str(pred))
			print(confusion_matrix(labels[self.n_split:], pred))
			print('\n')
			for couple in zip(key_features, importance):
				print('________ %s' % str((couple[0], '%.2f%%' % float(100 * couple[1]))))
			print('\n')
			print(classification_report(labels[self.n_split:], pred))
			with open(model_path, 'wb') as __f:
				pickle.dump(clf, __f)

	def classify_user():
		with open(model_path, 'rb') as f:
			clf = pickle.load(f)
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
				pred = clf.predict(vector)
				print('_______________________________')
				print('IS INFLUENCER ?')
				print(pred)

if __name__ == "__main__":
	trainer = Trainer()
	trainer.buildUsersModel()









