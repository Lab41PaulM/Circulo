import sys
import igraph as ig
import itertools

def radicchi_wrapper(G):
    g = G.copy()
    g.vs['id'] = list(range(g.vcount()))

    return radicchi(G, g, 0)

def radicchi(G, g, level):
    """
    Uses the Radicchi et al. algorithm to find the communities in a graph. Returns a list of the splits in the graph.
    """
    # Caching some global graph information and updating it manually. Because igraph
    # tends to recalculate this stuff on the whole graph every time, 
    # storing it and manipulating only the parts that change will make things faster.
    degree = g.degree()
    neighbors = [set(g.neighbors(v)) for v in g.vs]
    edges = {e.tuple for e in g.es}



    print("------------------")
    print("At level %s" % level)
    while True:
        if len(edges) == 0:
            break

        min_edge = None; min_ecc = None
        for edge in edges:
            ecc = edge_clustering_coefficient(edge[0], edge[1], degree, neighbors)
            if not min_edge or ecc < min_ecc:
                min_edge = edge
                min_ecc = ecc

        g.delete_edges(min_edge); edges.discard(min_edge)
        u, v = min_edge
        neighbors[u].discard(v); neighbors[v].discard(u)
        degree[u] -= 1; degree[v] -= 1
        
        if g.edge_connectivity(source=u, target=v) == 0:

            result = prune_components(G, g, community_measure='weak')
            if result['pruned']:
                orig_communities = result['orig_communities']
                new_communities = result['new_communities']
                remaining = result['remaining']

                for i,c in enumerate(new_communities):
                    print("Found a community: %s" % orig_communities[i])
                    print("Leaving level %s" % level)
                    s = g.subgraph(c)
                    radicchi(G, s, level+1)
                    print("Back to level %s" % level)

                r = g.subgraph(remaining)
                radicchi(G, r, level+1)

                break

    print("Done with level %s" % level)
    print("------------------")

def prune_components(orig, new, community_measure='strong'):
    components = new.components()
    ids = new.vs['id']

    new_components = [c for c in components]
    orig_components = [[ids[v] for v in component] for component in new_components]

    is_community = is_strong_community if (community_measure=='strong') else is_weak_community
    community_indices = [i for i, component in enumerate(orig_components) if is_community(orig, component)]

    orig_communities = [orig_components[i] for i in community_indices]
    new_communities = [new_components[i] for i in community_indices]

    result_pruned = False
    result_remaining_nodes = None
    result_orig_communities = None
    result_new_communities = None
    if len(community_indices) > 1:
        all_new_community_nodes = sum(new_communities, [])
        all_new_nodes = range(new.vcount())
        all_new_remaining_nodes = list(set(all_new_nodes) - set(all_new_community_nodes))

        result_pruned = True
        result_remaining_nodes = all_new_remaining_nodes
        result_new_communities = new_communities
        result_orig_communities = orig_communities

    return {"pruned": result_pruned, "orig_communities": result_orig_communities, 
            "new_communities": result_new_communities, "remaining": result_remaining_nodes}

def is_strong_community(G, nodes):
    """
    Checks whether the provided set of nodes form a strong community in the graph G.
    """
    # precondition: nodes must be sorted
    subgraph = G.subgraph(nodes)
    degree = G.degree(nodes)
    community_degree = subgraph.degree()
    for i in range(len(nodes)):
        if community_degree[i] <= (degree[i] - community_degree[i]):
            return False

    return True

def is_weak_community(G, nodes):
    """
    Checks whether the provided set of nodes form a weak community in the graph G.
    """
    # precondition: nodes must be sorted
    subgraph = G.subgraph(nodes)
    degree = G.degree(nodes)
    indegree = subgraph.degree()
    tsum = sum(degree)
    insum = sum(indegree)
    outsum = tsum - insum

    return insum > outsum

def edge_clustering_coefficient(u, v, degree, neighbors):
    """
    Computes the "edge clustering coefficient" of the given edge, defined as the number of triangles
    in which it participates compared to the maximum number of triangles of which it could be a part.
    """
    udeg = degree[u]
    vdeg = degree[v]
    mdeg = min(udeg-1, vdeg-1)
    if mdeg == 0:
        return float('inf')
    else:
        cdeg = len(neighbors[u] & neighbors[v])
        return (cdeg + 1.0) / mdeg

def main(argv):
    g = ig.Graph.Read_GML('netscience.gml')
    communities = radicchi_wrapper(g)
    print(communities)
    return communities

if __name__ == "__main__":
    main(sys.argv[1:])
