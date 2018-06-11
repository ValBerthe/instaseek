import webbrowser
import pandas as pd
import os
import sys
import math
sys.path.append(os.path.dirname(__file__))

csv_path = os.path.join(os.path.dirname(__file__), '../res/iguserssample.csv')
xl_path = os.path.join(os.path.dirname(__file__), '../res/iguserssample.xlsx')
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

xlfile = pd.read_excel(xl_path, encoding='ISO-8859-1')

users = xlfile['user'].tolist()

labels = list()
writer = pd.ExcelWriter(xl_path)

for index, user in enumerate(users):
	if not math.isnan(xlfile.at[index, 'label']):
		continue
	webbrowser.get(chrome_path).open(user)
	label = input('Label pour cette page ? %s : ' % user)
	xlfile.at[index, 'label'] = label
	xlfile.to_excel(writer, 'iguserssample')
	writer.save()


