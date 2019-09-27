# old function: not used
def get_graph(old1, new1):
    import pickle
    import networkx as nx
    from networkx.algorithms import shortest_path
    from matplotlib import pyplot as plt

    file = open('networkx_graph.pkl','rb')
    G = pickle.load(file)
    file.close()

    file = open('networkx_values.pkl', 'rb')
    values = pickle.load(file)
    file.close()

    pos = nx.spring_layout(G)
    shortpath = shortest_path(G, old1, new1)
    mytuples = []
    for i in range(len(shortpath)-1):
        mytuples.append((shortpath[i], shortpath[i+1]))

    print('drawing figure')
    plt.figure(1, figsize=(12,12))
    # nodes
    nx.draw(G, pos, node_size=20, node_color = values, width=.1, cmap='plasma')

    # edges
    nx.draw_networkx_edges(G, pos,
                           edgelist=mytuples,
                           width=8, edge_color='r')

    plt.savefig("static/coursera_lda_network_output.png", format="PNG")
