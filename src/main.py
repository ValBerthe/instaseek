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

import sys
import os

sys.path.append(os.path.dirname(__file__))

config_path = os.path.join(os.path.dirname(__file__), './config.ini')

from train import Trainer
from utils import createConfigFile

if __name__ == '__main__':

    if not os.path.isfile(os.path.join(config_path)):
        content = createConfigFile()
        with open(config_path, 'w') as file:
            file.write(content)

    while True:
        try:
            Trainer().classify_user()
        except Exception as e:
            print(e)
            break