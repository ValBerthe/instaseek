from sql_client import *
import matplotlib
import matplotlib.pyplot as plt
import pprint
import numpy as np

hist_limit = 200

pp = pprint.PrettyPrinter(indent=2)

sqlClient = SqlClient()
sqlClient.openCursor()

'''sqlClient.getAverageFollowersPerUser()
sqlClient.getAverageFollowingsPerUser()
sqlClient.getAverageLikesPerPost()
sqlClient.getAverageCommentsPerPost()'''
hashtag_details = sqlClient.getHashtagsDetails()
pp.pprint(hashtag_details)
print(sqlClient.getAverageFollowersPerUser())
print(sqlClient.getAverageCommentsPerPost())

likes_response = sqlClient.getAverageLikesPerPost()
avg_likes = likes_response['average']
histo_likes = likes_response['histogram']
_bars = []
heights = []
_counter = 0
for hist in histo_likes:
	if hist[0] < hist_limit:
		heights.append(hist[1])
		_bars.append(hist[0])
	else:
		_counter += hist[1]
heights.append(_counter)
_bars.append(hist_limit)
bars = tuple(_bars)
y_pos = np.arange(len(bars))

plt.bar(y_pos, heights)
plt.xticks(y_pos, bars)
plt.show()

labels = hashtag_details.keys()
n = hashtag_details.values()
 
#patches, texts = plt.pie(n, shadow=True, startangle=90)
#plt.legend(patches, labels, loc="best")
#plt.axis('equal')
#plt.tight_layout()
#plt.show()

sqlClient.close()