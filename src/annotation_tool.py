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
import os
import sys
import math

### Installed libs. ###
import webbrowser

sys.path.append(os.path.dirname(__file__))

### Custom libs. ###
from sql_client import SqlClient

ACCEPTED_VALUES = ['0', '1', '-2']

def annotate():
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

	for index, user in enumerate(users):

		### Ouvre un nouvel onglet, sur la page Instagram de l'utilisateur à annoter. ###
		webbrowser.get(chrome_path).open(user)
		label = -1

		username = user.split(insta_path)[1]

		### On recommence tant que l'utilisateur n'a pas été annoté par 0 ou par 1. -2 correspond à un utilisateur non trouvé. ###
		while label not in ACCEPTED_VALUES:
			label = input('%s. %s : ' % (str(index), user))

			### Si on a fait une erreur et que l'on veur revenir en arrière. ###
			if label == 'previous':
				if index > 0:
					### Ouvre de nouveau la page précédente. ###
					webbrowser.get(chrome_path).open(users[index - 1])

					labelprevious = -1
					while labelprevious not in ACCEPTED_VALUES:
						labelprevious = input('%s. %s : ' % (str(index - 1), users[index - 1]))
					### Set le label en base. ###
					sqlClient.openCursor()
					sqlClient.setLabel(users[index - 1].split(insta_path)[1], labelprevious)
					sqlClient.closeCursor()
				else:
					print('Cannot go previous first user.')

				### Réouvre la page courante. ###		
				webbrowser.get(chrome_path).open(user)

		### Set le label en base. ###
		sqlClient.openCursor()
		sqlClient.setLabel(username, label)
		sqlClient.closeCursor()

		sqlClient.openCursor()
		testRatio = sqlClient.getTestRatio()
		print(testRatio)
		if testRatio < 0.25:
			sqlClient.setTest(username, True)
		sqlClient.closeCursor()

### Si le programme est lancé ad hoc. ###
if __name__ == "__main__":
	annotate()
	
