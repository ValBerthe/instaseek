import webbrowser
import pandas as pd
import os
import sys
import math

sys.path.append(os.path.dirname(__file__))

from sql_client import *

if __name__ == "__main__":
	sys.path.append(os.path.dirname(__file__))

	sqlClient = SqlClient()

	csv_path = os.path.join(os.path.dirname(__file__), '../res/iguserssample.csv')
	xl_path = os.path.join(os.path.dirname(__file__), '../res/iguserssample.xlsx')
	chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
	insta_path = 'http://www.instagram.com/'

	xlfile = pd.read_excel(xl_path, encoding='ISO-8859-1')

	#users = xlfile['user'].tolist()
	sqlClient.openCursor()
	users = sqlClient.getUsernameUrls()
	sqlClient.closeCursor()

	print(len(users))
	print(users[:10])

	labels = list()
	writer = pd.ExcelWriter(xl_path)

	for index, user in enumerate(users):
		#if not math.isnan(xlfile.at[index, 'label']):
		#		continue
		webbrowser.get(chrome_path).open(user)
		label = -1
		while label not in ['0','1']:
			label = input('Label pour cette page ? %s : ' % user)
		sqlClient.openCursor()
		sqlClient.setLabel(user.split(insta_path)[1], label)
		sqlClient.closeCursor()
		#xlfile.at[index, 'label'] = label
		#xlfile.to_excel(writer, 'iguserssample')
		#writer.save()


