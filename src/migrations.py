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