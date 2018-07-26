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
import random

### Installed libs. ###
import networkx as nx
import matplotlib.pyplot as plt
import pprint

sys.path.append(os.path.dirname(__file__))

### Custom libs. ###
from sql_client import SqlClient

pp = pprint.PrettyPrinter(indent = 2)

if __name__ == "__main__":

    ### Définition du graphe. ###
    G = nx.DiGraph()

    sqlClient = SqlClient()

    ### Récupère tous les likes pour effectuer un graphe de liker/liké. ###
    sqlClient.openCursor()
    likes = sqlClient.getAllLikes(500)
    sqlClient.closeCursor()

    ### Ajout des nodes et des edges via. la requête à la BDD. ###
    G.add_edges_from(likes)

    '''d_in=G.in_degree(G)
    d_out=G.out_degree(G)
    g2 = G.copy()
    for n in g2.nodes():
        if d_in[n]==0 and d_out[n] == 1: 
            G.remove_node(n)'''

    ### Show Graph. ###

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