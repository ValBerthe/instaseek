import webbrowser
import os
import sys
import math

sys.path.append(os.path.dirname(__file__))

from sql_client import SqlClient

if __name__ == "__main__":
    sys.path.append(os.path.dirname(__file__))

    sqlClient = SqlClient()

    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    insta_path = 'http://www.instagram.com/'

    sqlClient.openCursor()
    users = sqlClient.getUsernameUrls(labeled=False)
    print('Fetched %s users.' % str(len(users)))
    sqlClient.closeCursor()

    labels = list()

    for index, user in enumerate(users):
        # if not math.isnan(xlfile.at[index, 'label']):
        #		continue
        webbrowser.get(chrome_path).open(user)
        label = -1

        while label not in ['0', '1']:
            label = input('Label pour cette page ? %s : ' % user)
        sqlClient.openCursor()
        sqlClient.setLabel(user.split(insta_path)[1], label)
        sqlClient.closeCursor()
        #xlfile.at[index, 'label'] = label
        #xlfile.to_excel(writer, 'iguserssample')
        # writer.save()
