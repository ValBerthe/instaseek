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

import pprint

pp = pprint.PrettyPrinter(indent = 2)

def get_post_fields(post):
	"""
	Formatte le post dans le format voulu.

			Args:
				post (dict) : Un dictionnaire de champs qui décrit le post.
			
			Returns:
				(tuple) : tuple des champs voulus.
	"""

	_id, _timestamp, media_type, text, small_img_url, tall_img_url, n_likes, n_comments, location, user_id, user_tags, sponsor_tags = [None] * 12
	try: #string
		_id = post['id']
	except KeyError:
		_id = ''
	try: #int
		_timestamp = post['taken_at']
	except KeyError:
		_timestamp = 0
	try: #int
		media_type = post['media_type']
	except KeyError:
		media_type = 0
	try: #int
		text = post['caption']['text']
	except (KeyError, TypeError):
		text = ''
	try: #string
		small_img_url = post['image_versions2']['candidates'][1]['url']
	except (KeyError, TypeError):
		small_img_url = ''
	try: #string
		tall_img_url = post['image_versions2']['candidates'][0]['url']
	except (KeyError, TypeError):
		tall_img_url = ''
	try: #int
		n_likes = post['like_count']
	except KeyError:
		n_likes = 0
	try: #int
		n_comments = post['comment_count']
	except KeyError:
		n_comments = 0
	try: #int
		location = post['location']['pk']
	except (KeyError, TypeError):
		location = 0
	try: #string
		user_id = post['user']['pk']
	except KeyError:
		user_id = ''
	try: #list
		user_tags = post['usertags']['in']
	except KeyError:
		user_tags = list()
	try: #list
		sponsor_tags = post['usertags']['sponsor_tags']
	except (KeyError, TypeError):
		sponsor_tags = list()
	return _id, _timestamp, media_type, text, small_img_url, tall_img_url, n_likes, n_comments, location, user_id, user_tags, sponsor_tags

def get_user_fields(user_server):
	"""
	Formatte l'utilisateur dans le format voulu.

			Args:
				post (dict) : Un dictionnaire de champs qui décrit l'utilisateur.
			
			Returns:
				(tuple) : tuple des champs voulus.
	"""

	u_id, u_user_name, u_full_name, u_is_private, u_is_verified, u_profile_pic_url, u_category, u_n_media, u_n_follower, u_n_following, u_is_business, u_biography, u_n_usertags, u_email, u_phone, u_city_id = [None] * 16
	try: #string
		u_id = user_server['pk']
	except KeyError:
		u_id = ''
	try: #string
		u_user_name = user_server['username']
	except KeyError:
		u_user_name = ''
	try: #string
		u_full_name = user_server['full_name']
	except KeyError:
		u_full_name = ''
	try: #bool
		u_is_private = user_server['is_private']
	except KeyError:
		u_is_private = False
	try: #bool
		u_is_verified = user_server['is_verified']
	except KeyError:
		u_is_verified = False
	try: #string
		u_profile_pic_url = user_server['hd_profile_pic_url_info']['url']
	except (KeyError, TypeError):
		u_profile_pic_url = ''
	try: #int
		u_n_media = user_server['media_count']
	except KeyError:
		u_n_media = 0
	try: #string
		u_category = user_server['category']
	except KeyError:
		u_category = ''
	try: #string
		u_n_follower = user_server['follower_count']
	except KeyError:
		u_n_follower = 0
	try: #string
		u_n_following = user_server['following_count']
	except KeyError:
		u_n_following = 0
	try: #string
		u_is_business = user_server['is_business']
	except KeyError:
		u_is_business = False
	try: #string
		u_biography = user_server['biography']
	except KeyError:
		u_biography = ''
	try: #string
		u_n_usertags = user_server['usertags_count']
	except KeyError:
		u_n_usertags = 0
	try: #string
		u_email = user_server['public_email']
	except KeyError:
		u_email = ''
	try: #string
		u_phone = user_server['public_phone_number']
	except KeyError:
		u_phone = ''
	try: #string
		u_city_id = user_server['city_id']
	except KeyError:
		u_city_id = ''
	return u_id, u_user_name, u_full_name, u_is_private, u_is_verified, u_profile_pic_url, u_category, u_n_media, u_n_follower, u_n_following, u_is_business, u_biography, u_n_usertags, u_email, u_phone, u_city_id

def get_comment_fields(comment):
	"""
	Formatte le commentaire dans le format voulu.

			Args:
				post (dict) : Un dictionnaire de champs qui décrit le commentaire.
			
			Returns:
				(tuple) : tuple des champs voulus.
	"""

	_id, user_id, comment_text = [None] * 3
	try: #string
		_id = comment['pk']
	except KeyError:
		_id = ''
	try: #string
		user_id = comment['user_id']
	except KeyError:
		user_id = ''
	try: #string
		comment_text = comment['text']
	except KeyError:
		comment_text = ''
	return _id, user_id, comment_text

def get_liker_fields(liker):
	"""
	Formatte le like dans le format voulu.

			Args:
				post (dict) : Un dictionnaire de champs qui décrit le like.
			
			Returns:
				(tuple) : tuple des champs voulus.
	"""

	user_id = None
	try: #string
		user_id = liker['pk']
	except KeyError:
		user_id = ''
	return user_id

def get_sponsor_hashtags():
	"""
	Retourne les hashtags décrivant les posts sponsorisés.

			Args:
				(none)
			
			Returns:
				(list) : la liste des hashtags sponsorisés.
	"""

	return ['ad', 'sponsored']

def get_random_hashtags():
	"""
	Retourne les hashtags décrivant les posts non sponsorisés.

			Args:
				(none)
			
			Returns:
				(list) : la liste des hashtags non sponsorisés.
	"""

	return ['love', 'followback', 'instagramers', 'envywear', 'tweegram', 'photooftheday', '20likes', 'amazing', 'smile', 'look', 'instalike', 'igers', 'picoftheday', 'food', 'instadaily', 'instafollow', 'followme', 'girl', 'instagood', 'bestoftheday', 'instacool', 'envywearco', 'follow', 'colorful', 'style', 'swag', 'fun', 'instagramers', 'model', 'envywear', 'food', 'smile', 'pretty', 'followme', 'nature', 'lol', 'dog', 'hair', 'sunset', 'swag', 'throwbackthursday', 'instagood', 'beach', 'friends', 'hot', 'funny', 'blue', 'life', 'art', 'photo', 'cool', 'envywearco', 'bestoftheday', 'clouds', 'amazing', 'envywear', 'fitness', 'followme', 'all_shots', 'textgram', 'family', 'instago', 'igaddict', 'awesome', 'girls', 'instagood', 'my', 'bored', 'baby', 'music', 'red', 'green', 'water', 'bestoftheday', 'black', 'party', 'white', 'yum', 'flower', 'envywearco', 'night', 'instalove', 'photo', 'photos', 'pic', 'pics', 'envywear', 'picture', 'pictures', 'snapshot', 'art', 'beautiful', 'instagood', 'picoftheday', 'photooftheday', 'color', 'all_shots', 'exposure', 'composition', 'focus', 'capture', 'moment', 'hdr', 'hdrspotters', 'hdrstyles_gf', 'hdri', 'hdroftheday', 'hdriphonegraphy', 'hdr_lovers', 'awesome_hdr', 'instagrammers', 'igers', 'instalove', 'instamood', 'instagood', 'followme', 'follow', 'comment', 'shoutout', 'iphoneography', 'androidography', 'filter', 'filters', 'hipster', 'contests', 'photo', 'instadaily', 'igaddict', 'envywear', 'photooftheday', 'pics', 'insta', 'picoftheday', 'bestoftheday', 'instadaily', 'instafamous', 'popularpic', 'popularphoto', 'fashion', 'style', 'stylish', 'love', 'envywear', 'envywear', 'cute', 'photooftheday', 'nails', 'hair', 'beauty', 'beautiful', 'instagood', 'pretty', 'swag', 'pink', 'girl', 'eyes', 'design', 'model', 'dress', 'shoes', 'heels', 'styles', 'outfit', 'purse', 'jewelry', 'shopping', 'ootd', 'outfitoftheday', 'lookoftheday', 'fashion', 'fashiongram', 'style', 'love', 'beautiful', 'currentlywearing', 'lookbook', 'wiwt', 'whatiwore', 'whatiworetoday', 'ootdshare', 'outfit', 'clothes', 'wiw', 'mylook', 'fashionista', 'todayimwearing', 'instastyle', 'envywear', 'instafashion', 'outfitpost', 'fashionpost', 'todaysoutfit', 'fashiondiaries', 'fashion', 'style', 'stylish', 'love', 'envywear', 'envywear', 'cute', 'photooftheday', 'nails', 'hair', 'beauty', 'beautiful', 'instagood', 'instafashion', 'pretty', 'girl', 'girls', 'eyes', 'model', 'dress', 'skirt', 'shoes', 'heels', 'styles', 'outfit', 'purse', 'jewelry', 'shopping', 'fashion', 'swag', 'style', 'stylish', 'envywear', 'envywear', 'swagger', 'photooftheday', 'jacket', 'hair', 'pants', 'shirt', 'handsome', 'cool', 'polo', 'swagg', 'guy', 'boy', 'boys', 'man', 'model', 'tshirt', 'shoes', 'sneakers', 'styles', 'jeans', 'fresh', 'dope', 'makeup', 'instamakeup', 'cosmetic', 'cosmetics', 'envywear', 'fashion', 'eyeshadow', 'lipstick', 'gloss', 'mascara', 'palettes', 'eyeliner', 'lip', 'lips', 'concealer', 'foundation', 'powder', 'eyes', 'eyebrows', 'lashes', 'lash', 'glue', 'glitter', 'crease', 'primers', 'base', 'beauty', 'beautiful', 'hair', 'hairstyle', 'instahair', 'envywear', 'hairstyles', 'haircolour', 'haircolor', 'hairdye', 'hairdo', 'haircut', 'longhairdontcare', 'braid', 'fashion', 'straighthair', 'longhair', 'style', 'straight', 'curly', 'black', 'brown', 'blonde', 'brunette', 'hairoftheday', 'hairideas', 'perfectcurls', 'hairfashion', 'hairofinstagram', 'coolhair', 'jewelry', 'jewels', 'jewel', 'envywear', 'fashion', 'gems', 'gem', 'gemstone', 'bling', 'stones', 'stone', 'trendy', 'accessories', 'love', 'crystals', 'beautiful', 'ootd', 'style', 'fashionista', 'accessory', 'instajewelry', 'stylish', 'cute', 'jewelrygram', 'fashionjewelry', 'bracelets', 'bracelet', 'armcandy', 'armswag', 'wristgame', 'pretty', 'love', 'beautiful', 'braceletstacks', 'trendy', 'instagood', 'fashion', 'braceletsoftheday', 'jewelry', 'fashionlovers', 'fashionista', 'envywear', 'accessories', 'armparty', 'wristwear', 'earrings', 'earring', 'earringsoftheday', 'jewelry', 'fashion', 'accessories', 'earringaddict', 'earringstagram', 'fashionista', 'girl', 'stylish', 'love', 'beautiful', 'piercing', 'piercings', 'pierced', 'cute', 'gorgeous', 'trendy', 'earringswag', 'envywear', 'earringfashion', 'earringlove', 'highheels', 'heels', 'platgorm', 'envywear', 'fashion', 'style', 'stylish', 'love', 'cute', 'photooftheday', 'tall', 'beauty', 'beautiful', 'girl', 'girls', 'model', 'shoes', 'styles', 'outfit', 'instaheels', 'fashionshoes', 'shoelover', 'instashoes', 'highheelshoes', 'heelsaddict', 'loveheels', 'iloveheels', 'shoestagram', 'shoes', 'shoe', 'kicks', 'envywear', 'instashoes', 'instakicks', 'sneakers', 'sneaker', 'sneakerhead', 'sneakerheads', 'solecollector', 'soleonfire', 'nicekicks', 'igsneakercommunity', 'sneakerporn', 'shoeporn', 'fashion', 'swag', 'instagood', 'photooftheday', 'nike', 'sneakerholics', 'sneakerfiend', 'shoegasm', 'kickstagram', 'walklikeus', 'peepmysneaks', 'flykicks', 'health', 'fitness', 'fit', 'envywear', 'fitnessmodel', 'fitnessaddict', 'fitspo', 'workout', 'bodybuilding', 'cardio', 'gym', 'train', 'training', 'health', 'healthy', 'instahealth', 'healthychoices', 'active', 'strong', 'motivation', 'instagood', 'determination', 'lifestyle', 'diet', 'getfit', 'cleaneating', 'eatclean', 'exercise', 'instafit', 'motivation', 'fit', 'envywear', 'fitness', 'gymlife', 'pushpullgrind', 'grindout', 'flex', 'instafitness', 'gym', 'trainhard', 'eatclean', 'grow', 'focus', 'dedication', 'strength', 'ripped', 'swole', 'fitnessgear', 'muscle', 'shredded', 'squat', 'cardio', 'sweat', 'grind', 'lifestyle', 'pushpullgrind', 'football', 'ball', 'pass', 'envywear', 'footballgame', 'footballseason', 'footballgames', 'footballplayer', 'instagood', 'pass', 'jersey', 'stadium', 'field', 'yards', 'photooftheday', 'yardline', 'pads', 'touchdown', 'catch', 'quarterback', 'fit', 'grass', 'nfl', 'superbowl', 'kickoff', 'run', 'basketball', 'basket', 'ball', 'envywear', 'baller', 'hoop', 'balling', 'sports', 'sport', 'court', 'net', 'rim', 'backboard', 'instagood', 'game', 'photooftheday', 'active', 'pass', 'throw', 'shoot', 'instaballer', 'instaball', 'jump', 'nba', 'bball', 'travel', 'traveling', 'envywear', 'vacation', 'visiting', 'instatravel', 'instago', 'instagood', 'trip', 'holiday', 'photooftheday', 'fun', 'travelling', 'tourism', 'tourist', 'instapassport', 'instatraveling', 'mytravelgram', 'travelgram', 'travelingram', 'igtravel', 'cars', 'car', 'ride', 'drive', 'envywear', 'driver', 'sportscar', 'vehicle', 'vehicles', 'street', 'road', 'freeway', 'highway', 'sportscars', 'exoticcar', 'exoticcars', 'speed', 'tire', 'tires', 'spoiler', 'muffler', 'race', 'racing', 'wheel', 'wheels', 'rims', 'engine', 'horsepower', 'motorcycle', 'motorcycles', 'bike', 'envywear', 'ride', 'rideout', 'bike', 'biker', 'bikergang', 'helmet', 'cycle', 'bikelife', 'streetbike', 'cc', 'instabike', 'instagood', 'instamotor', 'motorbike', 'photooftheday', 'instamotorcycle', 'instamoto', 'instamotogallery', 'supermoto', 'cruisin', 'cruising', 'bikestagram', 'skateboarding', 'skating', 'skater', 'envywear', 'instaskater', 'sk8', 'sk8er', 'sk8ing', 'sk8ordie', 'photooftheday', 'board', 'longboard', 'longboarding', 'riding', 'kickflip', 'ollie', 'instagood', 'wheels', 'skatephotoaday', 'skateanddestroy', 'skateeverydamnday', 'skatespot', 'skaterguy', 'skatergirl', 'skatepark', 'skateboard', 'skatelife', 'food', 'foodporn', 'yum', 'instafood', 'envywear', 'yummy', 'amazing', 'instagood', 'photooftheday', 'sweet', 'dinner', 'lunch', 'breakfast', 'fresh', 'tasty', 'food', 'delish', 'delicious', 'eating', 'foodpic', 'foodpics', 'eat', 'hungry', 'foodgasm', 'hot', 'foods', 'drink', 'drinks', 'slurp', 'pub', 'bar', 'liquor', 'yum', 'yummy', 'thirst', 'thirsty', 'instagood', 'cocktail', 'cocktails', 'drinkup', 'glass', 'can', 'photooftheday', 'beer', 'beers', 'wine', 'envywear', 'PleaseForgiveMe', 'coffee', 'cafe', 'instacoffee', 'cafelife', 'caffeine', 'hot', 'mug', 'drink', 'coffeeaddict', 'coffeegram', 'coffeeoftheday', 'cotd', 'coffeelover', 'coffeelovers', 'coffeeholic', 'coffiecup', 'coffeelove', 'coffeemug', 'envywear', 'coffeeholic', 'coffeelife', 'dessert', 'food', 'desserts', 'envywear', 'yum', 'yummy', 'amazing', 'instagood', 'instafood', 'sweet', 'chocolate', 'cake', 'icecream', 'dessertporn', 'delish', 'foods', 'delicious', 'tasty', 'eat', 'eating', 'hungry', 'foodpics', 'sweettooth', 'love', 'envywear', 'photooftheday', 'envywear', 'instamood', 'cute', 'igers', 'picoftheday', 'girl', 'guy', 'beautiful', 'fashion', 'instagramers', 'follow', 'smile', 'pretty', 'followme', 'friends', 'hair', 'swag', 'photo', 'life', 'funny', 'cool', 'hot', 'portrait', 'baby', 'girls', 'videogames', 'games', 'gamer', 'envywear', 'gaming', 'instagaming', 'instagamer', 'playinggames', 'online', 'photooftheday', 'onlinegaming', 'videogameaddict', 'instagame', 'instagood', 'gamestagram', 'gamerguy', 'gamergirl', 'gamin', 'video', 'game', 'igaddict', 'winning', 'play', 'playing']

def get_post_image_url(post):
	"""
	Récupère l'adresse URL dans le post.

			Args:
				post (dict) : Un dictionnaire de champs qui décrit le post.
			
			Returns:
				(str) : L'adresse Instagram de la photo du post.
	"""

	if post['media_type'] == 8:
		return post['carousel_media'][0]['image_versions2']['candidates'][1]['url']
	return post['image_versions2']['candidates'][1]['url']