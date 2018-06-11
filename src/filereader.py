import pickle
import pprint

pp = pprint.PrettyPrinter(indent = 2)

with open('../models/users_sample.model', 'rb') as f:
	_array = pickle.load(f)
	pp.pprint(_array)