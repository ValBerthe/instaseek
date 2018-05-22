from sql_client import *
import matplotlib.pyplot as plt
import pprint

pp = pprint.PrettyPrinter(indent=2)

sqlClient = SqlClient()
sqlClient.openCursor()

'''sqlClient.getAverageFollowersPerUser()
sqlClient.getAverageFollowingsPerUser()
sqlClient.getAverageLikesPerPost()
sqlClient.getAverageCommentsPerPost()'''
hashtag_details = sqlClient.getHashtagsDetails()
pp.pprint(hashtag_details)

labels = hashtag_details.keys()
n = hashtag_details.values()
 
patches, texts = plt.pie(n, shadow=True, startangle=90)
plt.legend(patches, labels, loc="best")
plt.axis('equal')
#plt.tight_layout()
plt.show()

sqlClient.close()