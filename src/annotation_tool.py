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

	for user in users:

		### Ouvre un nouvel onglet, sur la page Instagram de l'utilisateur à annoter. ###
		webbrowser.get(chrome_path).open(user)
		label = -1

		### On recommence tant que l'utilisateur n'a pas été annoté par 0 ou par 1. ###
		while label not in ['0', '1']:
			label = input('Label pour cette page ? %s : ' % user)

		### Set le label en base. ###
		sqlClient.openCursor()
		username = user.split(insta_path)[1]
		sqlClient.setLabel(username, label)
		sqlClient.closeCursor()

		sqlClient.openCursor()
		if sqlClient.getTestRatio > 0.25:
			sqlClient.setTest(username, True)
		sqlClient.closeCursor()

### Si le programme est lancé ad hoc. ###
if __name__ == "__main__":
	annotate()
	
