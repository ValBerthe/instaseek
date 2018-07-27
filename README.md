# Instaseek : find your influencers on Instagram

## Manual

This project aims to detect genuine and organic influencers on Instagram. The model is data-based and uses a machine learning approach :

- Simple metrics such as followers, following, media count, mean engagement rate, post frequency, etc.
- Comment quality score: is the audience engaged ?
- Metrics over the feed images' quality : unity of contrast and colorfulness, redundancy of colors, etc.

## Setup

Clone this repository on your local machine.
Install [Python 3.6](https://www.python.org/downloads/release/python-360/)

I will later make a pip package out of this project.

### Install dependencies using `pipenv` and Pipfile

- If you haven't installed `pipenv` yet, `pip install pipenv`
- `pipenv install`
- If you encounter dependencies conflicts, `pipenv install --skip-lock`

### Install dependencies using `requirements.txt`

- `pip install -r requirements.txt`

### Start classification

- `python src/__init__.py`

## Docs

You can check out docs [here](https://valberthe.github.io/).

## Script files

- `annotation_tool.py` helped me to annotate influencers streamed in the database.
- `classifier.py` lets you analyze an Instagram profile and classifies it among inlfuencer/not influencer.
- `main.py` is the entrypoint. Currently, it lauches `streamer.py`.
- `sql_client.py` is the SQL client. It processes and creates SQL requests to the database.
- `streamer.py` streams Instagram content into the database.
- `train.py` trains the model with data available in the database.
- `user.py` processes user infomation and extracts feature for machine learning.
- `utils.py` gathers all utility functions.

## Contact

Valentin Berthelot

valentin.berthelot@imt-atlantique.fr
valentin.berthelot5@gmail.com

