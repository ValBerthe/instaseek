import psycopg2
import psycopg2._psycopg as hem
import sys
import os
import time
import math
from utils import *
import pprint

pp = pprint.PrettyPrinter(indent=2)
sys.path.append(os.path.dirname(__file__))


class SqlClient(object):
	def __init__(self):
		super().__init__()
		self.conn = psycopg2.connect("dbname='bulb' user='Bulb' host='91.121.211.203' password='ddHbhWIjriGN6i9weHUM'")
		self.hashtag = ''

	def openCursor(self):
		self.cursor = self.conn.cursor()

	def closeCursor(self):
		self.cursor.close()

	def setHashtag(self, hashtag):
		self.hashtag = hashtag

	def insertPost(self, post, topPost = False):
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

	def insertUser(self, user):
		u_id, u_user_name, u_full_name, u_is_private, u_is_verified, u_profile_pic_url, u_category, u_n_media, u_n_follower, u_n_following, u_is_business, u_biography, u_n_usertags, u_email, u_phone, u_city_id = get_user_fields(
			user)
		self.cursor.execute('''
			INSERT INTO users (id, user_name, full_name, is_private, is_verified, profile_pic_url, category, n_media, n_follower, n_following, is_business, biography, n_usertags, email, phone, city_id)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			ON CONFLICT (id) DO UPDATE
			SET (id, user_name, full_name, is_private, is_verified, profile_pic_url, category, n_media, n_follower, n_following, is_business, biography, n_usertags, email, phone, city_id) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
				str(u_city_id)
			)
		)
		self.conn.commit()

	def insertComments(self, post_id, comments):
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

	def getUsers(self, n = 0):
		if n > 0:
			self.cursor.execute('''
				SELECT * FROM users
				ORDER BY id DESC LIMIT %s
			''' % str(n))
			return self.cursor.fetchall()

	def getAverageFollowersPerUser(self):
		self.cursor.execute('''
			SELECT AVG(n_follower)
			FROM users
			'''
		)
		result = "{0:0.2f}".format(self.cursor.fetchone()[0])
		print('Average number of followers: ', result)

	def getAverageFollowingsPerUser(self):
		self.cursor.execute('''
			SELECT AVG(n_following)
			FROM users
			'''
		)
		result = "{0:0.2f}".format(self.cursor.fetchone()[0])
		print('Average number of followings: ', result)

	def getAverageLikesPerPost(self):
		self.cursor.execute('''
			SELECT avg(count) FROM (
				SELECT count(id_post) 
				FROM likes 
				GROUP BY id_post
			) AS counts
			'''
		)
		result = "{0:0.2f}".format(self.cursor.fetchone()[0])
		print('Average number of likes: ', result)

	def getAverageCommentsPerPost(self):
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
		

	def close(self):
		self.closeCursor()
		self.conn.close()
