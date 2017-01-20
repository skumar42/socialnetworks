#imports needed 
from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
from TwitterAPI import TwitterAPI
from itertools import combinations
import itertools
import time
import os
import sys
import json
import argparse
import glob
import random
from matplotlib import pylab
from networkx import edge_betweenness_centrality as betweenness
import itertools


def draw_graph(edge_list):
    graph = nx.Graph()
    graph.add_edges_from(edge_list)
    print("Drawing graph for visulaziation: ")
    plt.figure(num=None, figsize=(20, 20), dpi=80)
    plt.axis('off')
    fig = plt.figure(1)
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph,pos)
    nx.draw_networkx_edges(graph,pos)

    cut = 1.00
    xmax = cut * max(xx for xx, yy in pos.values())
    ymax = cut * max(yy for xx, yy in pos.values())
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)

    plt.savefig("graph_original.png",bbox_inches="tight")
    pylab.close()
    nx.write_gpickle(graph, './graph.txt')
    del fig
    return graph



def jaccard(frn1, follow1,frn2, follow2):
    f1 = set(frn1)
    f2 = set(frn2)
    fw1 = set(follow1)
    fw2 = set(follow2)
    j1 = len(f1 & f2) / len(f1 | f2)
    j2 = len(fw1 & fw2) / len(fw1 | fw2)

    if( j1 > j2):
        return j1
    else:
        return j2




def get_all_uid():
    dic = {}
    i = 0
    for f in glob.glob('user_*.json'):
        rf = open(f)
        data = json.load(rf)
        uid = data['id']
        dic[uid] = i
        i = i+1
        rf.close()
    return dic




def generate_graph(uid_list):
    edge_list = []
    i = 0
    nodes_comb = list(combinations(list(uid_list.keys()), 2))
    #print("Combinations are:" ,nodes_comb)
    uid_frnds ={}
    uid_flwrs ={}
    for f in glob.glob('user_*.json'):
        rf = open(f)
        #print('inside')
        data = json.load(rf)
        uid = data['id']
        uid_frnds[uid] = data['friends']
        uid_flwrs[uid] = data['followers']

        frnds = data['friends']
        follwers = data['followers']
        
        for frnd in frnds[0:random.randint(1, 5)]:
            edge_list.append((uid, frnd))
        for flw in follwers[0:random.randint(1, 5)]:
            edge_list.append((flw, uid))
        
        rf.close()
        i = i+1
        #if(i>3):
        #    break
    for item in nodes_comb:
        uid_1 = item[0]
        uid_2 = item[1]
        frn1 = uid_frnds[uid_1]
        frn2 = uid_frnds[uid_2]
        follow1 = uid_frnds[uid_1]
        follow2 = uid_frnds[uid_2]
        sim = jaccard(frn1, follow1,frn2, follow2)
        if(sim > 0.0001):
            print("Similarity found between [%d , %d] user, form an edge <Jaccard threshold .0001> " %(uid_1, uid_2))
            edge_list.append((uid_1, uid_2))
    return edge_list




def most_central_edge(G):
    centrality = betweenness(G, weight='weight')
    return max(centrality, key=centrality.get)



def girvan_newman(G, most_valuable_edge=None):
    # If the graph is already empty, simply return its connected component
    if G.number_of_edges() == 0:
        yield tuple(nx.connected_components(G))
        return
    # If no function is provided, consider between centrality
    if most_valuable_edge is None:
        def most_valuable_edge(G):
            """Returns the edge with the highest betweenness centrality
            in the graph `G`.

            """
            # Non empty.
            betweenness = nx.edge_betweenness_centrality(G)
            return max(betweenness, key=betweenness.get)
    g = G.copy().to_undirected()
    # the connected components of the graph, self loop excluded
    g.remove_edges_from(g.selfloop_edges())
    while g.number_of_edges() > 0:
        yield _without_most_central_edges(g, most_valuable_edge)




def _without_most_central_edges(G, most_valuable_edge):
    
    original_num_components = nx.number_connected_components(G)
    num_new_components = original_num_components
    while num_new_components <= original_num_components:
        edge = most_valuable_edge(G)
        G.remove_edge(*edge)
        new_components = tuple(nx.connected_components(G))
        num_new_components = len(new_components)
    return new_components




def main():
    uid_dic = get_all_uid()
    print(uid_dic)
    ed=generate_graph(uid_dic)
    draw_graph(ed)
    k=5
    G=nx.read_gpickle('./graph.txt')
    #print(G.number_of_nodes())
    comp = girvan_newman(G, most_valuable_edge=most_central_edge)

    limited = itertools.takewhile(lambda c: len(c) <= k, comp)

    #print("Communities detected are %d", len(limited))
    
    for communities in limited:
        x = tuple(sorted(c) for c in communities)
    for i in range(len(x)):
        print("communitiy is:")
        print(x[i])
        print("  ")
    f = open('inetrmediate.json', 'w')
    f.write(str(len(x)))
    f.write('\n')
    #print(G.number_of_nodes())
    f.write(str(G.number_of_nodes()/k*1.0))
    f.close()

if __name__ == '__main__':
    main()
