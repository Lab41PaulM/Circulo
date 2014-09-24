import igraph
from igraph import VertexCover
import os
import sys
import urllib.request
from circulo.utils.downloader import download_with_notes
import shutil

GRAPH_NAME = 'karate'
DOWNLOAD_URL = 'http://www-personal.umich.edu/~mejn/netdata/karate.zip'
GRAPH_TYPE = '.gml'

def __download__(data_dir):
    """
    downloads the graph from DOWNLOAD_URL into data_dir/GRAPH_NAME
    """
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)
    download_with_notes(DOWNLOAD_URL, GRAPH_NAME, data_dir)


def __prepare__(data_dir, graph_path):
    """
    """
    shutil.copy(os.path.join(data_dir, GRAPH_NAME + GRAPH_TYPE), graph_path)


def get_graph():
    """
    Downloads and prepares a graph
    """
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    graph_path = os.path.join(os.path.dirname(__file__), "..", "GRAPHS", GRAPH_NAME + GRAPH_TYPE)

    if not os.path.exists(data_dir):
        __download__(data_dir)
    if not os.path.exists(graph_path):
        __prepare__(data_dir, graph_path)

    return igraph.load(graph_path)


def get_ground_truth(G=None):
    """
    returns a VertexClustering object of the
    ground truth of the graph G.
    """
    if G is None:
        G = get_graph()

    #ground truth table
    groups = {
            "1":0,
            "2":0,
            "3":0,
            "4":0,
            "5":0,
            "6":0,
            "7":0,
            "8":0,
            "9":1,
            "10":1,
            "11":0,
            "12":0,
            "13":0,
            "14":0,
            "15":1,
            "16":1,
            "17":0,
            "18":0,
            "19":1,
            "20":0,
            "21":1,
            "22":0,
            "23":1,
            "24":1,
            "25":1,
            "26":1,
            "27":1,
            "28":1,
            "29":1,
            "30":1,
            "31":1,
            "32":1,
            "33":1,
            "34":1,
            }

    clusters_list = [[],[]]

    for idx, k_id in enumerate(G.vs['id']):
        str_lbl = str(int(k_id))
        clusters_list[groups[str_lbl]].append(idx)

    return VertexCover(G, clusters_list)

def main():
    G = get_graph()
    get_ground_truth(G)

if __name__ == "__main__":
    main()
