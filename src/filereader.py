import pickle
import pprint
from user import User
import scipy
import scipy.misc
import scipy.cluster
import cv2
import numpy as np
from colormath.color_objects import LabColor, sRGBColor
from colormath.color_conversions import convert_color
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from statistics import mean

pp = pprint.PrettyPrinter(indent = 2)
NUM_CLUSTERS = 4

'''with open('../models/users_sample.model', 'rb') as f:
	_array = pickle.load(f)
	pp.pprint(_array)'''

users_list = ['bannanas_fithk', 'valberthe', 'glueandglitter', 'cirialostaunau', 'ozgekondakci', 'jimmyjummblz', 'domdraper666', 'gabrielleaguzar', 'serpilkrkll', 'kayfula_50']
influencers_list = ['its.pally', 'd_zheleva', 'dthompsy', 'mllegew', 'lisaster', 'evanranft', 'iamchouquette', 'coffeeandscarves', '_hellotiara', 'femkemegan']

users_dist = list()
influencer_dist = list()

user = User()

user.createCommentsModel()
user.testCommentScore()

for username in users_list:
	user.username = username
	user.getUserInfoIG()
	colors = user.colors
	arr1 = np.array(colors)
	codes1, dist1 = scipy.cluster.vq.kmeans(arr1, NUM_CLUSTERS)
	users_dist.append(dist1)

for username in influencers_list:
	user.username = username
	user.getUserInfoIG()
	colors = user.colors
	arr1 = np.array(colors)
	codes1, dist1 = scipy.cluster.vq.kmeans(arr1, NUM_CLUSTERS)
	influencer_dist.append(dist1)

print(users_dist)
print(influencer_dist)

user_mean = mean(users_dist)
influencer_mean = mean(influencer_dist)

print('___________')
print(user_mean)
print(influencer_mean)


'''fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter([dpoint[0] for dpoint in colors1], [dpoint[1] for dpoint in colors1], [dpoint[2] for dpoint in colors1])

arr1 = np.array(colors1)
arr2 = np.array(colors2)

codes1, dist1 = scipy.cluster.vq.kmeans(arr1, NUM_CLUSTERS)
codes2, dist2 = scipy.cluster.vq.kmeans(arr2, NUM_CLUSTERS)

print(codes1)
print(codes2)
print(dist1)
print(dist2)

plt.show()'''


'''user.createCommentsModel()
user.testCommentScore()'''
