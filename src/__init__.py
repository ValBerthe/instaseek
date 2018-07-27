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

import os
import sys
import warnings
import getpass

warnings.simplefilter(action='ignore', category = DeprecationWarning)

from InstagramAPI import InstagramAPI
import pprint

sys.path.append(os.path.dirname(__file__))

from train import Trainer
from utils import createConfigFile

pp = pprint.PrettyPrinter(indent = 2)
config_path = os.path.join(os.path.dirname(__file__), './config.ini')

def lauchClassification():
	while True:
		try:
			Trainer().classify_user()
		except Exception as e:
			print(e)
			break

if __name__ == '__main__':

	if not os.path.isfile(os.path.join(config_path)):
		print('DISCLAIMER:\n\nIn order to acces Instagram API and process Instagram users\' data, you need to provide an Instagram account.\nPlease insert below your Instagram credentials (we won\'t be using it for other purposes).\n')
		username = input('Instagram username : ')
		password = getpass.getpass('Password : ')
		print('\nTrying to log in...')

		### Essaye de se connecter à Instagram pour valider les credentials. ###
		InstagramApi = InstagramAPI(username, password)
		InstagramApi.login()
		response = InstagramApi.LastJson

		if response['status'] == 'ok':
			content = createConfigFile(username, password)
			with open(config_path, 'w') as file:
				file.write(content)
			print('\nSuccessfully logged in.\nSaving credentials at: %s' % config_path)
			lauchClassification()
		else:
			print('\n' + response['message'])
	
	else:
		lauchClassification()

	
