def get_output(t1, t2, csim=.5, cstars=.15, cenr=.35, chours=0.0):

    import pickle
    from scipy.io import loadmat
    import numpy as np

    def normalize_cost(x,flip=0):
        import numpy as np
        x = np.array(x)
        if np.sum(np.isnan(x))>0:
            inds = np.where(np.isnan(x))[0]
            x[inds] = np.nanmedian(x)
        if flip==1:
            x = x*(-1)

        normx = (x-np.min(x))/np.ptp(x)
        return normx


    mat = loadmat('scoremat.mat')
    scoremat = mat['scoremat']
    # numeric course info
    mat = loadmat('course_numeric_info.mat')
    stars = mat['stars']
    hours = mat['hours']
    enrollment = mat['enrollment']

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

    # new method: weighted recs

    scores_old = scoremat[:,old_topic]
    scores_new = scoremat[:,new_topic]

    stars_norm = normalize_cost(stars,1) # higher = better
    enrollment_norm = normalize_cost(np.log10(enrollment),1) # higher = better
    hours_norm = normalize_cost(hours) # lower = better

    print('testing:')
    print(np.sum(np.isnan(stars_norm)))
    print(np.sum(np.isnan(hours_norm)))

    rank_old = csim*scores_old + cstars*stars_norm + cenr*enrollment_norm + chours*hours_norm
    rank_new = csim*scores_new + cstars*stars_norm + cenr*enrollment_norm + chours*hours_norm
    print('new ranks:', rank_new[0:10])

    best_old = np.argsort(-rank_old); best_old = best_old.T
    best_new = np.argsort(-rank_new); best_new = best_new.T

    old1 = best_old[0][0]
    new1 = best_new[0][0]
    print(best_old[0:10])
    print('old1', old1)
    print('new1', new1)

    shortpath = get_graph_d3(old1, new1, csim, cstars, cenr, chours)
    titles_new = []
    for p in shortpath:
        titles_new.append(titles_all[p])
    return titles_old, titles_new

def get_graph_d3(old1, new1, csim, cstars, cenr, chours):

    import pickle
    import networkx as nx
    from networkx.algorithms import shortest_path
    import csv
    from scipy.io import loadmat, savemat
    from sklearn.metrics.pairwise import cosine_similarity as cos_sim
    import numpy as np

    def normalize_cost(x,flip=0):
        import numpy as np
        x = np.array(x)
        if np.sum(np.isnan(x))>0:
            inds = np.where(np.isnan(x))[0]
            x[inds] = np.nanmedian(x)
        if flip==1:
            x = x*(-1)

        normx = (x-np.min(x))/np.ptp(x)
        return normx

    # load Graph
    file = open('networkx_graph.pkl', 'rb')
    G = pickle.load(file)
    file.close()

    # load positions
    file = open('networkx_pos.pkl', 'rb')
    pos = pickle.load(file)
    file.close()

    # load node values
    file = open('networkx_values.pkl', 'rb')
    values = pickle.load(file)
    file.close()

    # load titles
    file = open('course_titles.pkl', 'rb')
    titles = pickle.load(file)
    file.close()

    # topic scores
    mat = loadmat('scoremat.mat')
    scoremat = mat['scoremat']
    scorecorrs = cos_sim(scoremat)

    # numeric course info
    mat = loadmat('course_numeric_info.mat')
    stars = mat['stars']
    hours = mat['hours']
    enrollment = mat['enrollment']

    list_edges = list(G.edges)

    # add weighted costs to edges

    stars_norm = normalize_cost(stars,1)
    enrollment_norm = normalize_cost(np.log10(enrollment),1)
    hours_norm = normalize_cost(hours)
    print('test star norm', np.sum(np.isnan(stars_norm)))

    weighted_costs = cstars*stars_norm + cenr*enrollment_norm + chours*hours_norm
    if np.shape(weighted_costs)[0] == 1:
        weighted_costs = weighted_costs.T

    # original graph G is binary: 1 if cos_sim =.5; 0 if <=.5
    list_weighted_costs = []
    list_weights = []
    for edge in G.edges:
        sim = scorecorrs[edge[0], edge[1]]
        dissim = 1-sim
        edge_cost = weighted_costs[edge[1]] + csim*dissim
        G.edges[edge[0], edge[1]]['weighted_cost'] = edge_cost
        G.edges[edge[0], edge[1]]['weight'] = 1 - edge_cost
        list_weighted_costs.append(edge_cost)
        list_weighted_costs.append(1-edge_cost)

    edgelist = list(G.edges)
    thresh_weights = np.percentile(list_weighted_costs,95)
    for edge in edgelist:
        if G.edges[edge[0], edge[1]]['weighted_cost'] > thresh_weights:
            G.remove_edge(edge[0], edge[1])

    edge_weights = [G[u][v]['weight']-.4 for u,v in G.edges()] # min is .5; -.4 so that min is .1

    # new values based on 1 - weighted_cost
    weights = dict(G.degree(weight='weights'))
    values = [weights.get(node, 0.25) for node in G.nodes()]

    # shortest path
    shortpath = shortest_path(G, old1, new1, weight='weighted_cost')
    mytuples = []
    for i in range(len(shortpath)-1):
        if shortpath[i] < shortpath[i+1]:
            newlink = (shortpath[i], shortpath[i+1])
        else:
            newlink = (shortpath[i+1], shortpath[i])
        mytuples.append(newlink)

    # write nodes.csv
    with open('static/nodes_tmp.csv', mode='w') as fp:
        fwriter = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        fwriter.writerow(['x', 'y', 'strength', 'radius','title'])
        for i in range(len(pos)):
            fwriter.writerow([pos[i][0], pos[i][1], int(values[i]), 2, titles[i]])

    # write edges.csv
    with open('static/edges_tmp.csv', mode='w') as fp:
        fwriter = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        fwriter.writerow(['x1', 'x2', 'y1', 'y2', 'width', 'color'])
        for i in range(len(list_edges)):
            x1 = pos[list_edges[i][0]][0]
            x2 = pos[list_edges[i][1]][0]
            y1 = pos[list_edges[i][0]][1]
            y2 = pos[list_edges[i][1]][1]
            if list_edges[i] in mytuples:
                fwriter.writerow([x1, x2, y1, y2, 2, '#ff0000'])
            else:
                pass
                # fwriter.writerow([x1, x2, y1, y2, .2, '#000000'])

    # write edges.csv
    with open('static/edges_tmp_all.csv', mode='w') as fp:
        fwriter = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        fwriter.writerow(['x1', 'x2', 'y1', 'y2', 'width', 'color'])
        for i in range(len(list_edges)):
            x1 = pos[list_edges[i][0]][0]
            x2 = pos[list_edges[i][1]][0]
            y1 = pos[list_edges[i][0]][1]
            y2 = pos[list_edges[i][1]][1]
            if list_edges[i] in mytuples:
                fwriter.writerow([x1, x2, y1, y2, 1, '#000000'])
                pass
                # fwriter.writerow([x1, x2, y1, y2, .2, '#000000'])

    return shortpath
