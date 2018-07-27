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
import sys
import os
import pickle
import random
import math

### Installed libs. ###
import pprint
import pandas as pd
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.utils import shuffle
from sklearn.model_selection import cross_val_score
from tqdm import tqdm
from PIL import Image
from cv2 import cv2

sys.path.append(os.path.dirname(__file__))

### Custom libs. ###
from user import User
from train import Trainer
from sql_client import SqlClient

### Instanciation du classificateur. ###
pp = pprint.PrettyPrinter(indent = 2)
classifier = Trainer()

users_model_path = os.path.join(os.path.dirname(__file__), './models/users_sample.model')

if __name__ == "__main__":
    """
    INSERT TESTS HERE
    """

    """
    END INSERT TESTS
    """

    ### Classe un utilisateur en influenceur/non influenceur. ###
    classifier.classify_user()