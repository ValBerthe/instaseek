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
import time
import math
import requests
import configparser
import random
from io import BytesIO
from collections import Counter

### Installed libs. ###
import psycopg2
import psycopg2._psycopg as hem
import pprint
from PIL import Image

sys.path.append(os.path.dirname(__file__))

### Custom libs. ###
from utils import *

pp = pprint.PrettyPrinter(indent = 2)
sys.path.append(os.path.dirname(__file__))
min_timestamp_selection = 1529680225
config_path = os.path.join(os.path.dirname(__file__), './config.ini')

class SqlClient(object):
	"""
	SQL Client class.
	"""

	def __init__(self):
		"""
		__init__ function.
		"""
		super().__init__()
		self.config = configparser.ConfigParser()
		self.config.read(config_path)
		self.conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" % (
			self.config['pgAdmin']['dbname'],
			self.config['pgAdmin']['user'],
			self.config['pgAdmin']['host'],
			self.config['pgAdmin']['password']
		))
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

	def createDatabase(self):
		"""
		Créée la base de données vide.
		"""
		self.cursor.execute('''
				--
				-- PostgreSQL database dump
				--

				-- Dumped from database version 9.6.9
				-- Dumped by pg_dump version 9.6.9

				-- Started on 2018-07-17 14:37:30 CEST

				SET statement_timeout = 0;
				SET lock_timeout = 0;
				SET idle_in_transaction_session_timeout = 0;
				SET client_encoding = 'UTF8';
				SET standard_conforming_strings = on;
				SELECT pg_catalog.set_config('search_path', '', false);
				SET check_function_bodies = false;
				SET client_min_messages = warning;
				SET row_security = off;

				--
				-- TOC entry 2177 (class 1262 OID 18214)
				-- Name: bulb; Type: DATABASE; Schema: -; Owner: Bulb
				--

				--
				-- TOC entry 1 (class 3079 OID 12395)
				-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner:
				--


				--
				-- TOC entry 2179 (class 0 OID 0)
				-- Dependencies: 1
				-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner:
				--



				SET default_tablespace = '';

				SET default_with_oids = false;

				--
				-- TOC entry 189 (class 1259 OID 18259)
				-- Name: comments; Type: TABLE; Schema: public; Owner: Bulb
				--

				CREATE TABLE comments (
					post_id text NOT NULL,
					user_id text NOT NULL,
					comment text NOT NULL,
					id_comment text NOT NULL
				);



				--
				-- TOC entry 190 (class 1259 OID 29565)
				-- Name: images; Type: TABLE; Schema: public; Owner: Bulb
				--

				CREATE TABLE images (
					url text NOT NULL,
					post_id text NOT NULL,
					image blob NOT NULL
				);



				--
				-- TOC entry 187 (class 1259 OID 18243)
				-- Name: likes; Type: TABLE; Schema: public; Owner: Bulb
				--

				CREATE TABLE likes (
					post_id text NOT NULL,
					user_id text NOT NULL,
					id_like text NOT NULL
				);



				--
				-- TOC entry 185 (class 1259 OID 18219)
				-- Name: posts; Type: TABLE; Schema: public; Owner: Bulb
				--

				CREATE TABLE posts (
					id_post text NOT NULL,
					timestamp integer NOT NULL,
					media_type smallint NOT NULL,
					small_img_url text,
					tall_img_url text,
					n_likes integer NOT NULL,
					n_comments integer,
					location bigint,
					user_id text NOT NULL,
					text text,
					is_top_post boolean,
					hashtag_origin text,
					timestamp_inserted_at integer
				);




				--
				-- TOC entry 188 (class 1259 OID 18251)
				-- Name: user_tags; Type: TABLE; Schema: public; Owner: Bulb
				--

				CREATE TABLE user_tags (
					post_id text NOT NULL,
					user_id text NOT NULL,
					id_usertag text NOT NULL
				);



				--
				-- TOC entry 186 (class 1259 OID 18227)
				-- Name: users; Type: TABLE; Schema: public; Owner: Bulb
				--

				CREATE TABLE users (
					id_user text NOT NULL,
					user_name text NOT NULL,
					full_name text NOT NULL,
					is_private boolean NOT NULL,
					is_verified boolean NOT NULL,
					profile_pic_url text,
					n_media integer NOT NULL,
					n_follower integer NOT NULL,
					n_following integer NOT NULL,
					is_business boolean NOT NULL,
					biography text NOT NULL,
					n_usertags integer NOT NULL,
					email text,
					phone text,
					city_id text,
					category text,
					with_feed boolean DEFAULT false,
					label smallint DEFAULT '-1'
				);




				--
				-- TOC entry 2045 (class 2606 OID 19162)
				-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: Bulb
				--

				ALTER TABLE ONLY comments
					ADD CONSTRAINT comments_pkey PRIMARY KEY (id_comment);


				--
				-- TOC entry 2048 (class 2606 OID 29572)
				-- Name: images images_pkey; Type: CONSTRAINT; Schema: public; Owner: Bulb
				--

				ALTER TABLE ONLY images
					ADD CONSTRAINT images_pkey PRIMARY KEY (url);


				--
				-- TOC entry 2040 (class 2606 OID 19165)
				-- Name: likes likes_pkey; Type: CONSTRAINT; Schema: public; Owner: Bulb
				--

				ALTER TABLE ONLY likes
					ADD CONSTRAINT likes_pkey PRIMARY KEY (id_like);


				--
				-- TOC entry 2035 (class 2606 OID 18226)
				-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: Bulb
				--

				ALTER TABLE ONLY posts
					ADD CONSTRAINT posts_pkey PRIMARY KEY (id_post);


				--
				-- TOC entry 2037 (class 2606 OID 18234)
				-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: Bulb
				--

				ALTER TABLE ONLY users
					ADD CONSTRAINT users_pkey PRIMARY KEY (id_user);


				--
				-- TOC entry 2043 (class 2606 OID 19229)
				-- Name: user_tags usertags_pkey; Type: CONSTRAINT; Schema: public; Owner: Bulb
				--

				ALTER TABLE ONLY user_tags
					ADD CONSTRAINT usertags_pkey PRIMARY KEY (id_usertag);


				--
				-- TOC entry 2033 (class 1259 OID 18289)
				-- Name: fki_author_user; Type: INDEX; Schema: public; Owner: Bulb
				--

				CREATE INDEX fki_author_user ON public.posts USING btree (user_id);


				--
				-- TOC entry 2046 (class 1259 OID 18272)
				-- Name: fki_id_post; Type: INDEX; Schema: public; Owner: Bulb
				--

				CREATE INDEX fki_id_post ON public.comments USING btree (post_id);


				--
				-- TOC entry 2038 (class 1259 OID 18283)
				-- Name: fki_id_post_likes; Type: INDEX; Schema: public; Owner: Bulb
				--

				CREATE INDEX fki_id_post_likes ON public.likes USING btree (post_id);


				--
				-- TOC entry 2041 (class 1259 OID 18295)
				-- Name: fki_id_post_user_tags; Type: INDEX; Schema: public; Owner: Bulb
				--

				CREATE INDEX fki_id_post_user_tags ON public.user_tags USING btree (post_id);


				--
				-- TOC entry 2049 (class 2606 OID 18284)
				-- Name: posts author_user; Type: FK CONSTRAINT; Schema: public; Owner: Bulb
				--

				ALTER TABLE ONLY posts
					ADD CONSTRAINT author_user FOREIGN KEY (user_id) REFERENCES users(id_user);


				--
				-- TOC entry 2050 (class 2606 OID 18273)
				-- Name: likes id_post; Type: FK CONSTRAINT; Schema: public; Owner: Bulb
				--

				ALTER TABLE ONLY likes
					ADD CONSTRAINT id_post FOREIGN KEY (post_id) REFERENCES posts(id_post);


				--
				-- TOC entry 2053 (class 2606 OID 18267)
				-- Name: comments id_post_comments; Type: FK CONSTRAINT; Schema: public; Owner: Bulb
				--

				ALTER TABLE ONLY comments
					ADD CONSTRAINT id_post_comments FOREIGN KEY (post_id) REFERENCES posts(id_post);


				--
				-- TOC entry 2051 (class 2606 OID 18278)
				-- Name: likes id_post_likes; Type: FK CONSTRAINT; Schema: public; Owner: Bulb
				--

				ALTER TABLE ONLY likes
					ADD CONSTRAINT id_post_likes FOREIGN KEY (post_id) REFERENCES posts(id_post);


				--
				-- TOC entry 2052 (class 2606 OID 18290)
				-- Name: user_tags id_post_user_tags; Type: FK CONSTRAINT; Schema: public; Owner: Bulb
				--
				ALTER TABLE ONLY user_tags
					ADD CONSTRAINT id_post_user_tags FOREIGN KEY (post_id) REFERENCES posts(id_post);


				--
				-- TOC entry 2054 (class 2606 OID 29573)
				-- Name: images image_fk; Type: FK CONSTRAINT; Schema: public; Owner: Bulb
				--

				ALTER TABLE ONLY images
					ADD CONSTRAINT image_fk FOREIGN KEY (post_id) REFERENCES posts(id_post);


				-- Completed on 2018-07-17 14:37:30 CEST

				--
				-- PostgreSQL database dump complete
				--
		''')
		self.conn.commit()

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
			INSERT INTO posts (id_post, timestamp, timestamp_inserted_at, media_type, text, small_img_url, tall_img_url, n_likes, n_comments, location, user_id, is_top_post, hashtag_origin)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			ON CONFLICT (id_post) DO UPDATE
			SET (id_post, timestamp, timestamp_inserted_at, media_type, text, small_img_url, tall_img_url, n_likes, n_comments, location, user_id, is_top_post, hashtag_origin) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
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
				INSERT INTO user_tags (id_usertag, post_id, user_id)
				VALUES (%s, %s, %s)
				ON CONFLICT (id_usertag) DO UPDATE
				SET (id_usertag, post_id, user_id) = (%s, %s, %s);
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
				INSERT INTO posts (id_post, timestamp, timestamp_inserted_at, media_type, text, small_img_url, tall_img_url, n_likes, n_comments, location, user_id, is_top_post, hashtag_origin)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				ON CONFLICT (id_post) DO UPDATE
				SET (id_post, timestamp, timestamp_inserted_at, media_type, text, small_img_url, tall_img_url, n_likes, n_comments, location, user_id, is_top_post, hashtag_origin) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
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
					INSERT INTO user_tags (id_usertag, post_id, user_id)
					VALUES (%s, %s, %s)
					ON CONFLICT (id_usertag) DO UPDATE
					SET (id_usertag, post_id, user_id) = (%s, %s, %s);
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
			INSERT INTO users (id_user, user_name, full_name, is_private, is_verified, profile_pic_url, category, n_media, n_follower, n_following, is_business, biography, n_usertags, email, phone, city_id, with_feed)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
			ON CONFLICT (id_user) DO UPDATE
			SET (id_user, user_name, full_name, is_private, is_verified, profile_pic_url, category, n_media, n_follower, n_following, is_business, biography, n_usertags, email, phone, city_id, with_feed) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
				INSERT INTO comments (id_comment, post_id, user_id, comment)
				VALUES (%s, %s, %s, %s)
				ON CONFLICT (id_comment) DO UPDATE
				SET (id_comment, post_id, user_id, comment) = (%s, %s, %s, %s);
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

	def insertLikers(self, post_id, likers):
		"""
		Insère un like en BDD.
		"""
		for liker in likers:
			user_id = get_liker_fields(liker)
			_id = str(post_id) + str(user_id)
			self.cursor.execute('''
				INSERT INTO likes (id_like, post_id, user_id)
				VALUES (%s, %s, %s)
				ON CONFLICT (id_like) DO UPDATE
				SET (id_like, post_id, user_id) = (%s, %s, %s);
				''',
				(
					str(_id),
					str(post_id), 
					str(user_id),
					# for update
					str(_id),
					str(post_id), 
					str(user_id)
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
	
	def setTest(self, username, isTest):
		"""
		Définit si l'utilisateur fait partie du set de test ou du training set.
		"""
		self.cursor.execute('''
			UPDATE users as u
			SET test_set = '%s'
			WHERE u.user_name = '%s'
		''' % ('true' if isTest else 'false', username))
		self.conn.commit()
	
	def getTestRatio(self):
		"""
		Retourne le ratio de la taille du jeu de données avec 
		"""
		self.cursor.execute('''
			SELECT test_set FROM users AS u
			WHERE u.label > -1
		''')
		values = self.cursor.fetchall()
		keys = [desc[0] for desc in self.cursor.description]
		result = [dict(zip(keys, value)) for value in values]
		bools = [row['test_set'] for row in result]
		cntr = Counter(bools)
		ratio = cntr[True] / (cntr[True] + cntr[False])
		print(ratio)
		return ratio

	def getUsernameUrls(self, labeled = True, randomized = True, sponsored_only = True):
		"""
		Récupère une liste d'adresses URL de profils en BDD.
		"""
		self.cursor.execute('''
			SELECT u.user_name FROM public.users AS u
			INNER JOIN public.posts AS p
			ON p.user_id = u.id_user
			INNER JOIN public.images AS i
			ON i.post_id = p.id_post
			WHERE u.label %s -1 %s
			GROUP BY u.user_name
		''' % ('>' if labeled else '=', 'and p.hashtag_origin in (\'ad\', \'sponsored\')' if sponsored_only else ''))
		array = ['http://www.instagram.com/%s' % name for name in self.cursor.fetchall()]
		if randomized:
			random.shuffle(array)
		return array
	
	def getUserPosts(self, username):
		"""
		Récupère un utilisateur et ses posts en fonction de son nickname.
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
			SELECT * FROM public.users AS u
			INNER JOIN public.posts AS p
			ON p.user_id = u.id_user
			INNER JOIN public.images AS i
			ON i.post_id = p.id_post
			WHERE u.user_name = '%s'
		''' % username)
		values = self.cursor.fetchall()
		keys = [desc[0] for desc in self.cursor.description]
		result = [dict(zip(keys, value)) for value in values]
		return result

	def getUser(self, username):
		"""
		Récupère les informations d'un utilisateur.
		"""
		self.cursor.execute('''
			SELECT * FROM public.users AS u
			WHERE u.user_name = '%s'
		''' % str(username))
		keys = [desc[0] for desc in self.cursor.description]
		values = self.cursor.fetchone()
		return dict(zip(keys, values))

	def getUsers(self, limit, labeled = True):
		"""
		Retourne les utilisateurs annotés.
		"""
		self.cursor.execute('''
			SELECT * FROM public.users AS u
			INNER JOIN public.posts AS p
			ON p.user_id = u.id_user
			INNER JOIN public.images AS i
			ON i.post_id = p.id_post
			WHERE u.label %s -1
			LIMIT %s
		''' % ('>' if labeled else '=', str(limit)))
		values = self.cursor.fetchall()
		keys = [desc[0] for desc in self.cursor.description]
		result = [dict(zip(keys, value)) for value in values]
		return result
	
	def getUserNames(self, limit, labeled = True):
		"""
		Retourne les usernames des utilisateurs annotés.
		"""
		self.cursor.execute('''
			SELECT u.user_name FROM public.users AS u
			INNER JOIN public.posts AS p
			ON p.user_id = u.id_user
			INNER JOIN public.images AS i
			ON i.post_id = p.id_post
			WHERE u.label %s -1
			GROUP BY u.user_name
			%s
		''' % ('>' if labeled else '=', 'LIMIT' + str(limit) if limit > 0 else ''))
		values = self.cursor.fetchall()
		keys = [desc[0] for desc in self.cursor.description]
		result = [dict(zip(keys, value)) for value in values]
		return result

	def getComments(self, post_id):
		"""
		Retourne les commentaires du post.
		"""
		self.cursor.execute('''
			SELECT * from public.comments as c
			WHERE c.post_id = '%s'
		''' % post_id)
		values = self.cursor.fetchall()
		keys = [desc[0] for desc in self.cursor.description]
		return [dict(zip(keys, value)) for value in values]

	def getAllLikes(self, n = 0):
		"""
		Retourne n likes en base de données.
		"""
		self.cursor.execute('''
			SELECT l.user_id, p.user_id FROM public.likes as l
			INNER JOIN public.posts as p
			ON l.post_id = p.id_post
			ORDER BY RANDOM()
			LIMIT %s
		''' % str(n))
		values = self.cursor.fetchall()
		#keys = [desc[0] for desc in self.cursor.description]
		#return [dict(zip(keys, value)) for value in values]
		return values

	def getUserPostComments(self, user_id):
		"""
		Retourne tous les commentaires que l'utilisateur a eu sur ses posts.
		"""
		self.cursor.execute('''
			SELECT * FROM public.comments AS c
			WHERE c.id_post IN (
				SELECT (id_post) FROM public.posts AS p
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
				SELECT count(post_id) 
				FROM likes 
				GROUP BY post_id
			) AS counts
			'''
		)
		average = "{0:0.2f}".format(self.cursor.fetchone()[0])
		self.cursor.execute(
			'''
			SELECT count_lk.likes_floor,  count(count_lk.likes_floor)
			FROM (
				SELECT  FLOOR((count(lk.post_id) / 10) *10) as likes_floor
				FROM likes as lk
				GROUP BY lk.post_id
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
				SELECT count(post_id) 
				FROM comments 
				GROUP BY post_id
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
			SELECT comment FROM comments
		''')
		return self.cursor.fetchall()
	
	def getAllBiographies(self):
		"""
		Récupère toutes les biographies de la BDD.
		"""
		self.cursor.execute('''
			SELECT biography, label FROM users AS u
			WHERE u.label > -1 AND u.test_set = false
		''')
		values = self.cursor.fetchall()
		keys = [desc[0] for desc in self.cursor.description]
		result = [dict(zip(keys, value)) for value in values]
		print(result)
		return result

	def close(self):
		"""
		Ferme la connexion.
		"""
		self.closeCursor()
		self.conn.close()
