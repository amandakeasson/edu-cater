import numpy as np
import pickle
from scipy.io import loadmat, savemat
import networkx as nx
from networkx.algorithms import shortest_path
import csv
from sklearn.metrics.pairwise import cosine_similarity as cos_sim

def normalize_cost(x,flip=0):
    """
    normalize an array to min=0, max=1.

    Parameters
    ----------
    x : array
    vector of values to be normalized

    Returns
    -------
    normx : array
    normalized values to be between 0 and 1
    """
    if flip==1:
        x = x*(-1)
    normx = (x-np.min(x))/(np.max(x)-np.min(x))
    return normx

def get_output(t1, t2, csim=.5, cstars=.15, cenr=.35, chours=0.0):
    """
    determines course path from familiar topic and new topic

    Parameters
    ----------

    t1 : string
    familiar topic

    t2 : string
    new topic

    csim : int or float
    weight for course similarity

    cstars : int or float
    weight for course rating

    cenr : int or float
    weight for course enrollment

    chours : int or float
    weight for course length

    Returns
    -------

    titles_new : list
    a list of recommended courses
    """

    csim = float(csim)
    cstars = float(cstars)
    cenr = float(cenr)
    chours = float(chours)

    ctotal = csim + cstars + cenr + chours

    csim = csim/ctotal
    cstars = cstars/ctotal
    cenr = cenr/ctotal
    chours = chours/ctotal
    print(csim,cstars, cenr, chours)

    # load topic scores per document
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

    # new method: weighted recs

    scores_old = scoremat[:,old_topic]
    scores_new = scoremat[:,new_topic]

    stars_norm = normalize_cost(stars,1) # higher = better
    enrollment_norm = normalize_cost(np.log10(enrollment),1) # higher = better
    hours_norm = normalize_cost(hours) # lower = better

    rank_old = csim*scores_old + cstars*stars_norm + cenr*enrollment_norm + chours*hours_norm
    rank_new = csim*scores_new + cstars*stars_norm + cenr*enrollment_norm + chours*hours_norm

    best_old = np.argsort(-rank_old); best_old = best_old.T
    best_new = np.argsort(-rank_new); best_new = best_new.T

    old1 = best_old[0][0]
    new1 = best_new[0][0]

    shortpath = get_graph_d3(old1, new1, csim, cstars, cenr, chours)
    titles_new = []
    course_scores = []
    for p in shortpath:
        titles_new.append(titles_all[p])
        course_scores.append(np.argmax(scoremat[p,:]))
    return titles_new

def get_graph_d3(old1, new1, csim, cstars, cenr, chours):
    """
    determines optimal path (shortest path)

    Parameters
    ----------

    old1 : int
    index of old topic

    new1 : int
    index of new topic

    csim : int or float
    weight for course similarity

    cstars : int or float
    weight for course rating

    cenr : int or float
    weight for course enrollment

    chours : int or float
    weight for course length

    Returns
    -------

    shortpath : array
    shortest path in the course graph
    """

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
    for d in range(len(scorecorrs)):
        scorecorrs[d,d] = 0
    print('corr test 1:', scorecorrs[old1,new1])

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

    weighted_costs = cstars*stars_norm + cenr*enrollment_norm + chours*hours_norm
    if np.shape(weighted_costs)[0] == 1:
        weighted_costs = weighted_costs.T

    list_weighted_costs = []
    list_weights = []
    counter = 0
    for edge in G.edges:
        sim = scorecorrs[edge[0], edge[1]]
        dissim = 1-sim
        edge_cost = weighted_costs[edge[1]] + csim*dissim
        if sim == 1:
            counter +=1
        G.edges[edge[0], edge[1]]['weighted_cost'] = edge_cost
        G.edges[edge[0], edge[1]]['weight'] = 1 - edge_cost
        list_weighted_costs.append(edge_cost)
        list_weights.append(1-edge_cost)
    print(np.min(np.array(list_weighted_costs)))
    print('corr:',scorecorrs[old1, new1])
    edge_weights = [G[u][v]['weight']-.4 for u,v in G.edges()] # min is .5; -.4 so that min is .1

    # shortest path
    shortpath = shortest_path(G, old1, new1, weight='weighted_cost')
    mytuples = []
    mytuples_directed = []
    for i in range(len(shortpath)-1):
        if shortpath[i] < shortpath[i+1]:
            newlink = (shortpath[i], shortpath[i+1])
        else:
            newlink = (shortpath[i+1], shortpath[i])
        mytuples.append(newlink)
        newlink = (shortpath[i], shortpath[i+1])
        mytuples_directed.append(newlink)

    # write nodes_output.csv
    # write nodes not in shortpath first so large nodes are drawn on top
    with open('static/nodes_output.csv', mode='w') as fp:
        fwriter = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        fwriter.writerow(['x', 'y', 'strength', 'radius','title'])
        for i in range(len(pos)):
            if i in shortpath:
                fwriter.writerow([pos[i][0], pos[i][1], int(values[i]), 4, titles[i]])
            else:
                pass

    # write edges_output.csv
    with open('static/edges_output.csv', mode='w') as fp:
        fwriter = csv.writer(fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        fwriter.writerow(['x1', 'x2', 'y1', 'y2', 'width', 'color'])
        for i in range(len(list_edges)):
            if list_edges[i] in mytuples:
                if list_edges[i] in mytuples_directed:
                    x1 = pos[list_edges[i][0]][0]
                    x2 = pos[list_edges[i][1]][0]
                    y1 = pos[list_edges[i][0]][1]
                    y2 = pos[list_edges[i][1]][1]
                else:
                    x1 = pos[list_edges[i][1]][0]
                    x2 = pos[list_edges[i][0]][0]
                    y1 = pos[list_edges[i][1]][1]
                    y2 = pos[list_edges[i][0]][1]
                fwriter.writerow([x1, x2, y1, y2, 2, '#ff0000'])

    return shortpath
