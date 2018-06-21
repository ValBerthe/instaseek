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
#key_features = ['commentscore', 'engagement', 'followers', 'followings', 'frequency', 'lastpost', 'usermentions', 'colorfulness_std', 'color_distorsion']
key_features = ['engagement', 'followers', 'followings', 'frequency', 'usermentions', 'commentscore']

def build_users_model():
	xlfile = pd.read_excel(xl_path, encoding='ISO-8859-1')

	users = xlfile['user'].tolist()
	labels = xlfile['label'].tolist()

	# On récupère toutes les features nécessaires pour entraîner le modèle
	user_model = User()
	for index, user in enumerate(users):
		print('PROCESSING USER N°%s...' % index)
		user_model.username = user.split(ig_url)[1]
		user_model.getUserInfoIG()
		if os.path.isfile(users_model_path):
			with open(users_model_path, 'rb') as f:
				users_array = pickle.load(f)
		else:
			users_array = []
		try:
			item = {
				'color_distorsion': user_model.color_distorsion,
				'colorfulness_std': user_model.colorfulness_std,
				'contrast_std': user_model.contrast_std,
				'lastpost': user_model.lastpost,
				'username': user_model.username,
				'frequency': user_model.frequency,
				'engagement': user_model.engagement,
				'followings': user_model.followings,
				'followers': user_model.followers,
				'usermentions': user_model.usermentions,
				'brandpresence': user_model.brandpresence,
				'brandtypes': user_model.brandtypes,
				'commentscore': user_model.commentscore,
				'label': labels[index]
			}
			users_array.append(item)
		except Exception as e:
			print('Error while appending to users_array (train.py) : ', e)
			pass
		with open(users_model_path, 'wb') as f:
			pickle.dump(users_array, f)

def pickle_labels():
	labels = [-1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 2, 0, 0, 0, 2, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, -1, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 2, 0, 1, 0, 1, 0, 2, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 2, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 2, -1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 2, 0, 0, -1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 2, 1, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 1, 1, 0, -1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, -1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 2, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 2, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, -1, 2, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, -1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0]
	with open(labels_model_path, 'wb') as f:
		pickle.dump(labels, f)

def train_model():
	n_split = 372
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
			clf.fit(features_array[:n_split], labels[:n_split])
			importance = clf.feature_importances_
			score = clf.score(features_array[n_split:], labels[n_split:])
			print(score)
		pred = clf.predict(features_array[n_split:])
		print('\n%s\n' % str(pred))
		print(confusion_matrix(labels[n_split:], pred))
		print('\n')
		for couple in zip(key_features, importance):
			print('________ %s' % str((couple[0], '%.2f%%' % float(100 * couple[1]))))
		print('\n')
		print(classification_report(labels[n_split:], pred))
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
				#user.commentscore, 
				user.engagement,
				user.followers,
				user.followings,
				user.frequency,
				#user.lastpost,
				user.usermentions
				#user.colorfulness_std,
				#user.color_distorsion
			]]
			pred = clf.predict(vector)
			print('_______________________________')
			print('IS INFLUENCER ?')
			print(pred)


if not os.path.isfile(users_model_path):
	build_users_model()
	
if not os.path.isfile(model_path):
	#pickle_labels()
	train_model()

classify_user()








