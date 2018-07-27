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

import random

from sql_client import SqlClient

class Migrations(object):
    """
    Classe Migration. Définit les migrations à opérer sur la base de données, ainsi que les rollbacks possibles.
    """

    def __init__(self):
        """
        __init__ function.
        """
        super().__init__()
    
    def mig_1(self):
        """
        Migration n°1. Permet de séparer les utilisateurs annotés en jeu d'entraînement et de test.
        """

        ### Définition du client SQL. ###
        sqlClient = SqlClient()

        ### Récupération des utilisateurs annotés.
        sqlClient.openCursor()
        usernames = sqlClient.getUserNames(limit = 0)
        sqlClient.closeCursor

        random.shuffle(usernames)

        ### Indexation au jeu d'entraînement ou de test. ###
        for index, user in enumerate(usernames):
            isTest = False
            if index % 4 == 0:
                isTest = True
            sqlClient.openCursor()
            sqlClient.setTest(user['user_name'], isTest)
            sqlClient.closeCursor()
    
    def mig_1_rollback(self):
        """
        Rollback de la migration n°1. Permet de séparer les utilisateurs annotés en jeu d'entraînement et de test.
        """

        ### Définition du client SQL. ###
        sqlClient = SqlClient()

        ### Récupération des utilisateurs annotés.
        sqlClient.openCursor()
        usernames = sqlClient.getUserNames(limit = 0)
        sqlClient.closeCursor

        ### Reset des valeurs de la colonne 'test_set'. ###
        for user in usernames:
            sqlClient.openCursor()
            sqlClient.setTest(user['user_name'], False)
            sqlClient.closeCursor()

if __name__ == "__main__":

    migrations = Migrations()
    migrations.mig_1()