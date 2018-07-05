### System libs. ###
import os
import sys
import math

### Installed libs. ###
import webbrowser

sys.path.append(os.path.dirname(__file__))

### Custom libs. ###
from sql_client import SqlClient

### Si le programme est lancé ad hoc. ###
if __name__ == "__main__":

	sys.path.append(os.path.dirname(__file__))
	chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
	insta_path = 'http://www.instagram.com/'

	### Ouvre le client SQL. ###
	sqlClient = SqlClient()
	sqlClient.openCursor()

	### Récupère les noms d'utilisateurs à annoter. ###
	users = sqlClient.getUsernameUrls(labeled=False)
	print('Fetched %s users.' % str(len(users)))
	sqlClient.closeCursor()

	labels = list()

	for index, user in enumerate(users):
		### Ouvre un nouvel onglet, sur la page Instagram de l'utilisateur à annoter. ###
		webbrowser.get(chrome_path).open(user)
		label = -1

		### On recommence tant que l'utilisateur n'a pas été annoté par 0 ou par 1. ###
		while label not in ['0', '1']:
			label = input('Label pour cette page ? %s : ' % user)
		sqlClient.openCursor()

		### Set le label en base. ###
		sqlClient.setLabel(user.split(insta_path)[1], label)
		sqlClient.closeCursor()
