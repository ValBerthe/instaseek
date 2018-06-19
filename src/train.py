from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, classification_report
import sys
import os
import pandas as pd
import pickle
import pprint

from user import User

pp = pprint.PrettyPrinter(indent = 2)
sys.path.append(os.path.dirname(__file__))

xl_path = os.path.join(os.path.dirname(__file__), '../res/iguserssample.xlsx')
model_path = os.path.join(os.path.dirname(__file__), '../models/classifier.model')
users_model_path = os.path.join(os.path.dirname(__file__), '../models/users_sample.model')
labels_model_path = os.path.join(os.path.dirname(__file__), '../models/labels.model')
ig_url = 'http://www.instagram.com/'
key_features = ['commentscore', 'engagement', 'followers', 'followings', 'frequency', 'lastpost', 'usermentions', 'colorfulness_std', 'color_distorsion']
#key_features = ['engagement', 'followers', 'followings', 'frequency', 'usermentions']

def build_users_model():
	xlfile = pd.read_excel(xl_path, encoding='ISO-8859-1')

	users = xlfile['user'].tolist()
	labels = xlfile['label'].tolist()

	# On récupère toutes les features nécessaires pour entraîner le modèle
	user_model = User()
	for user in users:
		user_model.username = user.split(ig_url)[1]
		user_model.getUserInfoIG()
		if os.path.isfile(users_model_path):
			with open(users_model_path, 'rb') as f:
				users_array = pickle.load(f)
		else:
			users_array = []
		try:
			users_array.append({
				'color_distorsion': user_model.color_distorsion,
				'colorfulness_std': user_model.colorfulness_std,
				'lastpost': user_model.lastpost,
				'frequency': user_model.frequency,
				'engagement': user_model.engagement,
				'followings': user_model.followings,
				'followers': user_model.followers,
				'usermentions': user_model.usermentions,
				'brandpresence': user_model.brandpresence,
				'brandtypes': user_model.brandtypes,
				'commentscore': user_model.commentscore
			})
		except Exception as e:
			print('Error while appending to users_array (train.py) : ', e)
			pass
		with open(users_model_path, 'wb') as f:
			pickle.dump(users_array, f)
	with open(labels_model_path, 'wb') as f:
		pickle.dump(labels, f)

def train_model():
	with open(users_model_path, 'rb') as f:
		with open(labels_model_path, 'rb') as _f:
			labels = pickle.load(_f)
			users_array = pickle.load(f)
			zipped = zip(users_array, labels)
			users_array = list()
			labels = list()
			for zipp in zipped:
				if zipp[1] in [0, 1]:
					features = list()
					for key in key_features:
						features.append(zipp[0][key])
					users_array.append(features)
					labels.append(zipp[1])

			# train classifier
			clf = RandomForestClassifier(n_estimators = 500)
			clf.fit(users_array[:370], labels[:370])
			importance = clf.feature_importances_
			score = clf.score(users_array[370:], labels[370:])
			print(score)
			pred = clf.predict(users_array[370:])
			print('\n%s\n' % str(pred))
			print(confusion_matrix(labels[370:], pred))
			print('\n')
			for couple in zip(key_features, importance):
				print('________ %s' % str((couple[0], '%.2f%%' % float(100 * couple[1]))))
			print('\n')
			print(classification_report(labels[370:], pred))
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


if not (os.path.isfile(users_model_path) and os.path.isfile(labels_model_path)):
	build_users_model()
	
if not os.path.isfile(model_path):
	train_model()

classify_user()








