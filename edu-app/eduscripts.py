def get_output(t1, t2):
    import pickle
    from scipy.io import loadmat
    import numpy as np
    mat = loadmat('scoremat.mat')
    scoremat = mat['scoremat']

    file = open('course_titles.pkl', 'rb')
    titles_all = pickle.load(file)
    file.close()

    old_topic = int(t1.split('topic')[1])-1
    new_topic = int(t2.split('topic')[1])-1

    rec_old = np.where(scoremat[:,old_topic]==np.max(scoremat[:,old_topic]))[0][0]
    rec_new = np.where(scoremat[:,new_topic]==np.max(scoremat[:,new_topic]))[0][0]

    recs_old = np.argsort(-scoremat[:,old_topic])
    recs_new = np.argsort(-scoremat[:,new_topic])

    recs_old = recs_old[0:5]
    recs_new = recs_new[0:5]

    titles_old = []
    titles_new = []
    for i in range(5):
        titles_old.append(titles_all[recs_old[i]])
        titles_new.append(titles_all[recs_new[i]])

    old1 = recs_old[0]
    new1 = recs_new[0]

    #get_graph(old1, new1)
    return titles_old, titles_new

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
