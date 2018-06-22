import psycopg2
import psycopg2._psycopg as hem
import sys
import os
import time
import math
from utils import *
import pprint
import requests

from PIL import Image
from io import BytesIO

pp = pprint.PrettyPrinter(indent=2)
sys.path.append(os.path.dirname(__file__))


class SqlClient(object):
	def __init__(self):
		"""
		__init__ function.
		"""
		super().__init__()
		self.conn = psycopg2.connect("dbname='bulb' user='Bulb' host='91.121.211.203' password='ddHbhWIjriGN6i9weHUM'")
		self.hashtag = ''

	def openCursor(self):
		"""
		Ouvre le curseur SQL du client.
		"""
		self.cursor = self.conn.cursor()

	def closeCursor(self):
		"""
		Ferme le curseur SQL du client.
		"""
		self.cursor.close()

	def setHashtag(self, hashtag):
		"""
		Définit le hashtag actuel.
		"""
		self.hashtag = hashtag

	def insertPost(self, post, topPost = False):
		"""
		Insère un post en BDD.
		"""

		p__id, p__timestamp, p_media_type, p_text, p_small_img_url, p_tall_img_url, p_n_likes, p_n_comments, p_location, p_user_id, user_tags, sponsor_tags = get_post_fields(post)

		self.cursor.execute('''
			INSERT INTO posts (id, timestamp, timestamp_inserted_at, media_type, text, small_img_url, tall_img_url, n_likes, n_comments, location, user_id, is_top_post, hashtag_origin)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			ON CONFLICT (id) DO UPDATE
			SET (id, timestamp, timestamp_inserted_at, media_type, text, small_img_url, tall_img_url, n_likes, n_comments, location, user_id, is_top_post, hashtag_origin) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
			''',
			(
				str(p__id),
				str(p__timestamp),
				str(math.floor(time.time())),
				str(p_media_type),
				str(p_text),
				str(p_small_img_url),
				str(p_tall_img_url),
				str(p_n_likes),
				str(p_n_comments),
				str(p_location),
				str(p_user_id),
				str(topPost),
				str(self.hashtag),
				# for update
				str(p__id),
				str(p__timestamp),
				str(math.floor(time.time())),
				str(p_media_type),
				str(p_text),
				str(p_small_img_url),
				str(p_tall_img_url),
				str(p_n_likes),
				str(p_n_comments),
				str(p_location),
				str(p_user_id),
				str(topPost),
				str(self.hashtag)
			)
		)
		self.conn.commit()
		for user_tag in user_tags:
			id_user_tag = user_tag['user']['pk']
			_id = str(p__id) + str(id_user_tag)
			self.cursor.execute('''
				INSERT INTO user_tags (id, id_post, id_user)
				VALUES (%s, %s, %s)
				ON CONFLICT (id) DO UPDATE
				SET (id, id_post, id_user) = (%s, %s, %s);
				''',
				(
					str(_id),
					str(p__id),
					str(id_user_tag),
					# for update
					str(_id),
					str(p__id), 
					str(id_user_tag)
				)
			)
			self.conn.commit()
		
		url = get_post_image_url(post)
		response = requests.get(url)

		self.cursor.execute('''
			INSERT INTO images (url, post_id, image)
			VALUES (%s, %s, %s)
			ON CONFLICT (url) DO UPDATE
			SET (url, post_id, image) = (%s, %s, %s)
		''',
		(
			str(url),
			str(p__id),
			response.content,
			# for udpate
			str(url),
			str(p__id),
			response.content
		))

	def insertUserFeed(self, feed):
		"""
		Insère un feed de profil en BDD.
		"""
		for post in feed:
			
			p__id, p__timestamp, p_media_type, p_text, p_small_img_url, p_tall_img_url, p_n_likes, p_n_comments, p_location, p_user_id, user_tags, sponsor_tags = get_post_fields(post)

			self.cursor.execute('''
				INSERT INTO posts (id, timestamp, timestamp_inserted_at, media_type, text, small_img_url, tall_img_url, n_likes, n_comments, location, user_id, is_top_post, hashtag_origin)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				ON CONFLICT (id) DO UPDATE
				SET (id, timestamp, timestamp_inserted_at, media_type, text, small_img_url, tall_img_url, n_likes, n_comments, location, user_id, is_top_post, hashtag_origin) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
				''',
				(
					str(p__id),
					str(p__timestamp),
					str(math.floor(time.time())),
					str(p_media_type),
					str(p_text),
					str(p_small_img_url),
					str(p_tall_img_url),
					str(p_n_likes),
					str(p_n_comments),
					str(p_location),
					str(p_user_id),
					str('false'),
					str(self.hashtag),
					# for update
					str(p__id),
					str(p__timestamp),
					str(math.floor(time.time())),
					str(p_media_type),
					str(p_text),
					str(p_small_img_url),
					str(p_tall_img_url),
					str(p_n_likes),
					str(p_n_comments),
					str(p_location),
					str(p_user_id),
					str('false'),
					str(self.hashtag)
				)
			)

			for user_tag in user_tags:
				id_user_tag = user_tag['user']['pk']
				_id = str(p__id) + str(id_user_tag)
				self.cursor.execute('''
					INSERT INTO user_tags (id, id_post, id_user)
					VALUES (%s, %s, %s)
					ON CONFLICT (id) DO UPDATE
					SET (id, id_post, id_user) = (%s, %s, %s);
					''',
					(
						str(_id),
						str(p__id),
						str(id_user_tag),
						# for update
						str(_id),
						str(p__id), 
						str(id_user_tag)
					)
				)

			url = get_post_image_url(post)
			response = requests.get(url)

			self.cursor.execute('''
				INSERT INTO images (url, post_id, image)
				VALUES (%s, %s, %s)
				ON CONFLICT (url) DO UPDATE
				SET (url, post_id, image) = (%s, %s, %s)
			''',
			(
				str(url),
				str(p__id),
				response.content,
				# for udpate
				str(url),
				str(p__id),
				response.content
			))
		self.conn.commit()

	def insertUser(self, user):
		"""
		Insère un utilisateur en BDD.
		"""
		u_id, u_user_name, u_full_name, u_is_private, u_is_verified, u_profile_pic_url, u_category, u_n_media, u_n_follower, u_n_following, u_is_business, u_biography, u_n_usertags, u_email, u_phone, u_city_id = get_user_fields(
			user
		)
		self.cursor.execute('''
			INSERT INTO users (id, user_name, full_name, is_private, is_verified, profile_pic_url, category, n_media, n_follower, n_following, is_business, biography, n_usertags, email, phone, city_id, with_feed)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			ON CONFLICT (id) DO UPDATE
			SET (id, user_name, full_name, is_private, is_verified, profile_pic_url, category, n_media, n_follower, n_following, is_business, biography, n_usertags, email, phone, city_id, with_feed) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
		''', (
				str(u_id),
				str(u_user_name),
				str(u_full_name),
				str(u_is_private),
				str(u_is_verified),
				str(u_profile_pic_url),
				str(u_category),
				str(u_n_media),
				str(u_n_follower),
				str(u_n_following),
				str(u_is_business),
				str(u_biography),
				str(u_n_usertags),
				str(u_email),
				str(u_phone),
				str(u_city_id),
				'true',
				# for update
				str(u_id),
				str(u_user_name),
				str(u_full_name),
				str(u_is_private),
				str(u_is_verified),
				str(u_profile_pic_url),
				str(u_category),
				str(u_n_media),
				str(u_n_follower),
				str(u_n_following),
				str(u_is_business),
				str(u_biography),
				str(u_n_usertags),
				str(u_email),
				str(u_phone),
				str(u_city_id),
				'true'
			)
		)
		self.conn.commit()

	def insertComments(self, post_id, comments):
		"""
		Insère un commentaire en BDD.
		"""
		for comment in comments:
			_id, comment_user_id, comment_text = get_comment_fields(comment)
			self.cursor.execute('''
				INSERT INTO comments (id, id_post, id_user, comment)
				VALUES (%s, %s, %s, %s)
				ON CONFLICT (id) DO UPDATE
				SET (id, id_post, id_user, comment) = (%s, %s, %s, %s);
				''',
				(
					str(_id),
					str(post_id), 
					str(comment_user_id),
					str(comment_text),
					# for update
					str(_id),
					str(post_id), 
					str(comment_user_id),
					str(comment_text)
				)
			)
			self.conn.commit()

	def insertLikers(self, id_post, likers):
		"""
		Insère un like en BDD.
		"""
		for liker in likers:
			id_user = get_liker_fields(liker)
			_id = str(id_post) + str(id_user)
			self.cursor.execute('''
				INSERT INTO likes (id, id_post, id_user)
				VALUES (%s, %s, %s)
				ON CONFLICT (id) DO UPDATE
				SET (id, id_post, id_user) = (%s, %s, %s);
				''',
				(
					str(_id),
					str(id_post), 
					str(id_user),
					# for update
					str(_id),
					str(id_post), 
					str(id_user)
				)
			)
		self.conn.commit()

	def setLabel(self, username, label):
		"""
		Annote l'utilisateur en influenceur (1)/non influenceur (0).
		"""
		self.cursor.execute('''
			UPDATE users as u
			SET label = '%s'
			WHERE u.user_name = '%s'
		''' % (str(label), username))
		self.conn.commit()

	def getUsers(self, n = 0):
		"""
		Récupère n utilisateurs de la BDD.
		"""
		if n > 0:
			self.cursor.execute('''
				SELECT * FROM users
				ORDER BY id DESC LIMIT %s
			''' % str(n))
			return self.cursor.fetchall()
	
	def getUsernameUrls(self):
		"""
		Récupère une liste d'adresses URL de profils en BDD.
		"""
		self.cursor.execute('''
			SELECT user_name FROM public.users as u
			WHERE (
				SELECT count(*) FROM public.images AS i
				WHERE i.post_id in (
					SELECT id FROM public.posts AS p
					WHERE p.user_id = u.id
				)
			) > 0 AND u.label = -1
		''')
		return ['http://www.instagram.com/%s' % name for name in self.cursor.fetchall()]
	
	def getUser(self, username):
		"""
		Récupère un utilisateur en fonction de son nickname.
		"""
		self.cursor.execute('''
			SELECT * FROM users as u
			WHERE u.user_name = '%s'
		''' % username)
		values = self.cursor.fetchone()
		keys = [desc[0] for desc in self.cursor.description]
		return dict(zip(keys, values))

	def getUserPosts(self, _id):
		"""
		Récupère tous les posts des utilisateurs.
		Retourne : {
			id: ...
			timestamps: ...
			media_type: ...
			small_img_url: ...
			tall_img_url: ...
			n_likes: ...
			n_comments: ...
			location: ...
			user_id: ...
			text: ...
			is_top_post: ...
			hashtag_origin: ...
			timestamp_inserted_at: ...
			image: ...
		}
		"""
		self.cursor.execute('''
			SELECT * FROM posts
			WHERE false
		''')
		keys = [desc[0] for desc in self.cursor.description]
		self.cursor.execute('''
			SELECT * FROM posts as p
			WHERE p.user_id = '%s'
		''' % str(_id))
		values = self.cursor.fetchall()
		posts = list()
		for post in values:
			post = dict(zip(keys, post))
			self.cursor.execute('''
				SELECT image FROM images as i
				WHERE i.post_id = '%s'
			''' % post['id'])
			image = self.cursor.fetchone()
			post['image'] = image
			posts.append(post)
		return posts

	def getAllUsers(self):
		"""
		Retourne les utilisateurs annotables.
		"""
		self.cursor.execute('''
			SELECT * FROM public.users as u
			WHERE (
				SELECT count(*) FROM public.images AS i
				WHERE i.post_id in (
					SELECT id FROM public.posts AS p
					WHERE p.user_id = u.id
				)
			) > 0 AND u.label > -1
		''')
		values = self.cursor.fetchall()
		keys = [desc[0] for desc in self.cursor.description]
		return [dict(zip(keys, value)) for value in values]

	def getComments(self, post_id):
		"""
		Retourne les commentaires du post.
		"""
		self.cursor.execute('''
			SELECT * from public.comments as c
			WHERE c.id_post = '%s'
		''' % post_id)
		values = self.cursor.fetchall()
		keys = [desc[0] for desc in self.cursor.description]
		return [dict(zip(keys, value)) for value in values]

	def getUserPostComments(self, user_id):
		"""
		Retourne tous les commentaires que l'utilisateur a eu sur ses posts.
		"""
		self.cursor.execute('''
			SELECT * FROM public.comments AS c
			WHERE c.id_post IN (
				SELECT (id) FROM public.posts AS p
				WHERE p.user_id = '%s'
			)
		''' % user_id)
		return self.cursor.fetchall()

	def getAverageFollowersPerUser(self):
		"""
		Récupère le nombre moyen de followers par utilisateur.
		"""
		self.cursor.execute('''
			SELECT AVG(n_follower)
			FROM users
			'''
		)
		result = "{0:0.2f}".format(self.cursor.fetchone()[0])
		print('Average number of followers: ', result)

	def getAverageFollowingsPerUser(self):
		"""
		Récupère le nombre moyen d'abonnements par utilisateur.
		"""
		self.cursor.execute('''
			SELECT AVG(n_following)
			FROM users
			'''
		)
		result = "{0:0.2f}".format(self.cursor.fetchone()[0])
		print('Average number of followings: ', result)

	def getAverageLikesPerPost(self):
		"""
		Récupère le nombre moyen de likes par post, ainsi que l'histogramme associé.
		"""
		self.cursor.execute(
			'''
			SELECT avg(count) FROM (
				SELECT count(id_post) 
				FROM likes 
				GROUP BY id_post
			) AS counts
			'''
		)
		average = "{0:0.2f}".format(self.cursor.fetchone()[0])
		self.cursor.execute(
			'''
			SELECT count_lk.likes_floor,  count(count_lk.likes_floor)
			FROM (
				SELECT  FLOOR((count(lk.id_post) / 10) *10) as likes_floor
				FROM likes as lk
				GROUP BY lk.id_post
			) as count_lk
			GROUP BY count_lk.likes_floor
			ORDER BY count_lk.likes_floor;
			'''
		)
		result = self.cursor.fetchall()
		return {
			'average': average,
			'histogram': result 
		}

	def getAverageCommentsPerPost(self):
		"""
		Récupère le nombre moyen de commentaires par post.
		"""
		self.cursor.execute('''
			SELECT avg(count) FROM (
				SELECT count(id_post) 
				FROM comments 
				GROUP BY id_post
			) AS counts
			'''
		)
		result = "{0:0.2f}".format(self.cursor.fetchone()[0])
		print('Average number of comments: ', result)

	def getHashtagsDetails(self):
		"""
		Récupère la répartition des hashtags en BDD.
		"""
		self.cursor.execute('''
			SELECT hashtag_origin, count(hashtag_origin) 
			FROM posts
			GROUP BY hashtag_origin
			'''
		)
		result = self.cursor.fetchall()
		_result = dict()
		for couple in result:
			_result[str(couple[0])] = couple[1]
		return _result
		
	def getAllComments(self):
		"""
		Récupère tous les commentaires de la BDD.
		"""
		self.cursor.execute('''
			SELECT comment from comments
		''')
		return self.cursor.fetchall()
	
	def close(self):
		"""
		Ferme la connexion.
		"""
		self.closeCursor()
		self.conn.close()
