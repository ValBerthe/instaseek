import sys
import os
import random

import networkx as nx
import matplotlib.pyplot as plt
import pprint

sys.path.append(os.path.dirname(__file__))

from sql_client import SqlClient

pp = pprint.PrettyPrinter(indent = 2)

G = nx.DiGraph()

sqlClient = SqlClient()

sqlClient.openCursor()
likes = sqlClient.getAllLikes(500)
sqlClient.closeCursor()

pp.pprint(likes[:10])

G.add_edges_from(likes)

'''d_in=G.in_degree(G)
d_out=G.out_degree(G)
g2 = G.copy()
for n in g2.nodes():
    if d_in[n]==0 and d_out[n] == 1: 
        G.remove_node(n)'''

### PRINT GRAPH ###

options = {
    'node_color': 'lightBlue',
    'node_size': 10,
    'width': 1,
    'with_labels': False
}

#plt.subplot(221)
#nx.draw_spring(G, **options)
#plt.subplot(222)
#nx.draw_circular(G, **options)
#plt.subplot(223)
nx.draw(G, **options)
#plt.subplot(224)
#nx.draw_shell(G, nlist=[range(5), range(5, 10), range(10, 15), range(15, 20), range(20, 25), range(25, 30)], **options)

plt.show()