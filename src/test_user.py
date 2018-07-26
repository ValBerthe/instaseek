import sys
import os

import pytest
from unittest.mock import MagicMock, Mock
from PIL import Image
from colormath.color_objects import LabColor

sys.path.append(os.path.dirname(__file__))

from user import User

image_test_path = os.path.join(os.path.dirname(__file__), '../res/exemple_feed_influenceur.PNG')

##############################
## _______ FIXTURES _______ ##
##############################

@pytest.fixture
def user():
    return User()

@pytest.fixture
def smallInt():
    return 80

@pytest.fixture
def mediumInt():
    return 8000

@pytest.fixture
def bigInt():
    return 8000000

@pytest.fixture
def ilya():
    return 1532526308

@pytest.fixture
def numberOfPosts():
    return 18

@pytest.fixture
def oldestPost():
    return 1532526308

@pytest.fixture
def labArray():
    return [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ]

@pytest.fixture
def imageTest():
    return Image.open(image_test_path)

@pytest.fixture
def postTest():
    return {
        "taken_at": 1526291552,
        "pk": 1778984940287174928,
        "id": "1778984940287174928_1423877615",
        "device_timestamp": 7648945199145,
        "media_type": 1,
        "code": "BiwOWCylikQ",
        "client_cache_key": "MTc3ODk4NDk0MDI4NzE3NDkyOA==.2",
        "filter_type": 0,
        "image_versions2": {
            "candidates": [
            {
                "width": 780,
                "height": 975,
                "url": "https://scontent-cdg2-1.cdninstagram.com/vp/8d80e0f9e3ccf4c5833478115f92bdfc/5B762EED/t51.2885-15/e35/31709142_1981153598581536_7102637204656095232_n.jpg?ig_cache_key=MTc3ODk4NDk0MDI4NzE3NDkyOA%3D%3D.2"
            },
            {
                "width": 240,
                "height": 300,
                "url": "https://scontent-cdg2-1.cdninstagram.com/vp/6b5096053425a1165a67448902739a46/5B766904/t51.2885-15/e35/p240x240/31709142_1981153598581536_7102637204656095232_n.jpg?ig_cache_key=MTc3ODk4NDk0MDI4NzE3NDkyOA%3D%3D.2"
            }
            ]
        },
        "original_width": 780,
        "original_height": 975,
        "user": {
            "pk": 1423877615,
            "username": "nishikch",
            "full_name": "nishikch",
            "is_private": False,
            "profile_pic_url": "https://scontent-cdg2-1.cdninstagram.com/vp/db92855a74ac891018d482d9b670c153/5B856118/t51.2885-19/s150x150/23595003_369777986808642_4002706681451511808_n.jpg",
            "profile_pic_id": "1572662310642808594_1423877615",
            "friendship_status": {
            "following": False,
            "outgoing_request": False,
            "is_bestie": False
            },
            "has_anonymous_profile_picture": False,
            "is_unpublished": False,
            "is_favorite": False
        },
        "can_viewer_reshare": True,
        "caption": {
            "pk": 17926115968082468,
            "user_id": 1423877615,
            "text": "Life isnt perfect but your outfit can be..... Hello guys,  I truly believer of this quote \"dress how you want to be addressed\"...\nYour attire definitely defines your personality & it gives you confidence,  if you're dressing smart.... I m a shopoholic girl, I never miss a day to chk out, nykaa, myntra,  flipkart & amazon..but sometimes before I came in touch with @shaans_gallery , & I was told to just scroll through their website, which amazed me & pushed me to shop... They are having jaw dropping \ud83d\ude30collection... I also want to talk about the prices of the product, which is comparatively lower than other well known sites... You should chk out  @shaans_gallery For best fashion attires at reasonable price...\nWebsite's link \ud83d\udd17 in bio\n.\n.\n#sponsored \n#fashionbloggers#indianlifestylebloggers#slaying#olive#jumpsuit#offshoulderdress#fashionoutfits#indianfashioninfluencers#gogirl",
            "type": 1,
            "created_at": 1526291553,
            "created_at_utc": 1526291553,
            "content_type": "comment",
            "status": "Active",
            "bit_flags": 0,
            "user": {
            "pk": 1423877615,
            "username": "nishikch",
            "full_name": "nishikch",
            "is_private": False,
            "profile_pic_url": "https://scontent-cdg2-1.cdninstagram.com/vp/db92855a74ac891018d482d9b670c153/5B856118/t51.2885-19/s150x150/23595003_369777986808642_4002706681451511808_n.jpg",
            "profile_pic_id": "1572662310642808594_1423877615",
            "friendship_status": {
                "following": False,
                "outgoing_request": False,
                "is_bestie": False
            },
            "has_anonymous_profile_picture": False,
            "is_unpublished": False,
            "is_favorite": False
            },
            "did_report_as_spam": False,
            "media_id": 1778984940287174928
        },
        "caption_is_edited": False,
        "like_count": 5,
        "has_liked": False,
        "likers": [],
        "comment_likes_enabled": False,
        "comment_threading_enabled": False,
        "has_more_comments": False,
        "max_num_visible_preview_comments": 2,
        "preview_comments": [
            {
            "pk": 17929214743124569,
            "user_id": 3298495976,
            "text": "Zhakkkaaaaaaaaa\u00e0a\u00e0aaaaaaaaaas",
            "type": 0,
            "created_at": 1526291631,
            "created_at_utc": 1526291631,
            "content_type": "comment",
            "status": "Active",
            "bit_flags": 0,
            "user": {
                "pk": 3298495976,
                "username": "ali_suratwala",
                "full_name": "jimmy",
                "is_private": True,
                "is_verified": False,
                "profile_pic_url": "https://instagram.fbsb1-1.fna.fbcdn.net/vp/856b9478629f7c2f4ae549c4c8cc5dd7/5B94597A/t51.2885-19/11906329_960233084022564_1448528159_a.jpg"
            },
            "did_report_as_spam": False,
            "media_id": 1778984940287174928
            }
        ],
        "comment_count": 1,
        "photo_of_you": False,
        "fb_user_tags": {
            "in": []
        },
        "can_viewer_save": True,
        "organic_tracking_token": "eyJ2ZXJzaW9uIjo1LCJwYXlsb2FkIjp7ImlzX2FuYWx5dGljc190cmFja2VkIjp0cnVlLCJ1dWlkIjoiMTg1MDY3NzA3MjQ3NGI1MGFmYzQwMTI1YTU0YTJlMzgxNzc4OTg0OTQwMjg3MTc0OTI4Iiwic2VydmVyX3Rva2VuIjoiMTUyNjI5MTYzNTgyMnwxNzc4OTg0OTQwMjg3MTc0OTI4fDEzMzg4NTEwNzd8MTI0ZmI1ODhiNWFlYmFmZTEwYWM1M2ZiMTEwYTQ2ZTZlODNiYTU1NzlmMDI3NmU0OGRhMGNjZTcxN2FkMmUyMSJ9LCJzaWduYXR1cmUiOiIifQ==",
        "usertags": {
        "in": [
            {
            "user": {
                "pk": 184378318,
                "username": "shaans_gallery",
                "full_name": "MEN'S FASHION & STYLE",
                "is_private": False,
                "is_verified": False,
                "profile_pic_url": "https://scontent-cdg2-1.cdninstagram.com/vp/c1a7d360ac96fa984c113b90266c276d/5B86602E/t51.2885-19/s150x150/12750372_585568998283714_1627786605_a.jpg"
            },
            "position": [
                0.8937198068000001,
                0.5966183575
            ],
            "start_time_in_video_in_sec": None,
            "duration_in_video_in_sec": None
            }]
        }
    }

@pytest.fixture
def userTest():
    return {
        "include_direct_blacklist_status": True,
        "pk": 5539569547,
        "username": "thecolorful_traveller",
        "full_name": "By Christine",
        "has_anonymous_profile_picture": False,
        "is_private": False,
        "is_verified": False,
        "profile_pic_url": "https://scontent-cdg2-1.cdninstagram.com/vp/7af145a80fd5d8bad582cd490709b5dc/5B8CAE3A/t51.2885-19/s150x150/30591208_223839018363775_5960793412843077632_n.jpg",
        "profile_pic_id": "1760320595859520721_5539569547",
        "media_count": 126,
        "follower_count": 8892,
        "following_count": 2564,
        "geo_media_count": 0,
        "is_business": True,
        "biography": "\u2741 Content Creative\n\u2741 Forever chasing light; it turns the ordinary into the   magical \u3002\u00b7 \u00b0  \u00b7 \uff0e\u3002\u22c6\n\u2741 Explore #thecolorsofisrael\nFollow me on Travelibro\u21ca",
        "external_url": "https://travelibro.app.link/thecolorfultraveler-instagram",
        "external_lynx_url": "https://l.instagram.com/?u=https%3A%2F%2Ftravelibro.app.link%2Fthecolorfultraveler-instagram&e=ATMssvyAHGNam47BnD5cAuAnuAbksyaRAlvb_0pKWupBNoDnaL11ZQL_aRSXZX0U0JlTqHu3gJ13ZeNt",
        "hd_profile_pic_url_info": {
        "height": 1080,
        "url": "https://scontent-cdg2-1.cdninstagram.com/vp/188ea21c0fcf29de54c3b5b5a7103128/5B80A9C0/t51.2885-19/30591208_223839018363775_5960793412843077632_n.jpg",
        "width": 1080
        },
        "hd_profile_pic_versions": [
        {
            "height": 320,
            "url": "https://scontent-cdg2-1.cdninstagram.com/vp/6456d1e387e658f398b66b76f141a01c/5B998ECA/t51.2885-19/s320x320/30591208_223839018363775_5960793412843077632_n.jpg",
            "width": 320
        },
        {
            "height": 640,
            "url": "https://scontent-cdg2-1.cdninstagram.com/vp/948d0115fb4e964edd2d5169bd26f875/5B8434A5/t51.2885-19/s640x640/30591208_223839018363775_5960793412843077632_n.jpg",
            "width": 640
        }
        ],
        "usertags_count": 73,
        "has_chaining": True,
        "is_favorite": False,
        "profile_context": "Followed by thewininghills, dutch.traveller, theseagullfly + 1 more",
        "profile_context_links_with_user_ids": [
        {
            "end": 26,
            "start": 12
        },
        {
            "end": 43,
            "start": 28
        },
        {
            "end": 58,
            "start": 45
        },
        {
            "end": 67,
            "start": 61
        }
        ],
        "profile_context_mutual_follow_ids": [
        5610511480,
        5591467545,
        6413867268
        ],
        "reel_auto_archive": "on",
        "has_highlight_reels": True,
        "public_email": "thecolorfultraveller@gmail.com",
        "public_phone_number": "",
        "public_phone_country_code": "",
        "contact_phone_number": "",
        "city_id": 106371992735156,
        "city_name": "Tel Aviv, Israel",
        "address_street": "",
        "direct_messaging": "UNKNOWN",
        "latitude": 32.0667,
        "longitude": 34.7667,
        "category": "Blogger",
        "business_contact_method": "TEXT",
        "is_call_to_action_enabled": False,
        "fb_page_call_to_action_id": "",
        "zip": "",
        "school": {},
        "has_unseen_besties_media": False,
        "auto_expand_chaining": False
    }
        

#####################################
## _______ TESTS UNITAIRES _______ ##
#####################################

def test_uiFormatInt_small(user, smallInt):
    result = user.uiFormatInt(smallInt)
    assert result == '80'

def test_uiFormatInt_med(user, mediumInt):
    result = user.uiFormatInt(mediumInt)
    assert result == '8.0K'

def test_uiFormatInt_big(user, bigInt):
    result = user.uiFormatInt(bigInt)
    assert result == '8.0M'

def test_uiGetIlya(user, ilya):
    result = user.uiGetIlya(ilya)
    assert type(result) is str
    assert 'second' in result

def test_calculateFrequency(user, numberOfPosts, oldestPost):
    result = user.calculateFrequency(numberOfPosts, oldestPost)
    assert type(result) is float

def test_calcCentroid3d(user, labArray):
    result = user.calcCentroid3d(labArray)
    assert type(result) is float

def test_getMostDominantColour(user, imageTest):
    result = user.getMostDominantColour(imageTest)
    assert hasattr(result, 'lab_l')
    assert hasattr(result, 'lab_a')
    assert hasattr(result, 'lab_b')

def test_getImageColorfulness(user, imageTest):
    result = user.getImageColorfulness(imageTest)
    assert type(result) is float

def test_getContrast(user, imageTest):
    result = user.getContrast(imageTest)
    assert type(result) is float

def test_getBrandPresence(user, postTest):
    result = user.getBrandPresence(postTest)
    assert all(type(brand) is str for brand in result)

def test_getBiographieScore(user, userTest):
    result = user.getBiographyScore(userTest['biography'])
    assert type(result) is float