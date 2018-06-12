import pickle
import pprint
from user import User

pp = pprint.PrettyPrinter(indent = 2)

'''with open('../models/users_sample.model', 'rb') as f:
	_array = pickle.load(f)
	pp.pprint(_array)'''

user = User()
user.createCommentsModel()
user.testCommentScore()
