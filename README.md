# edu-cater  

## catering your education to your needs!  

This repository contains the code for my Insight Data Science project.

### Introduction:  

edu-cater is a tool for custom course recommendations on Coursera. Course recommendations are often based on courses with highly similar content, but students may wish to select courses that are *somewhat* related to a skillset that they already possess, while also learning a new set of skills. This is where edu-cater comes in.  
 
Using topic modeling, users can get an understanding of specific course topics that are not only based on general topics and skills, but also other features from the syllabus and student reviews of the course. Course length and difficulty are also factors that can be considered when making course requests.

Users can make requests for features that they would like to see in the recommended courses. Then, an optimization algorithm selects the courses that best match the user's criteria.
  
### Setup and installation:  

Run the following code to set up edu-cater:

`cd edu-cater`  
`pip install -r requirements.txt`  
`python setup.py`

### How does edu-cater work?  

edu-cater involves the following steps:  

1) Preprocessing  

Each course "document" consists of the course title, description, and syllabus. Each document is then preprocessed. Preprocessing steps involve removing stopwords, lemmatizing, and stemming.  

Next, a bag-of-words corpus is generated. A dictionary of unique terms is then defined. Terms appearing in fewer than 10 documents or more than 25% of documents are removed.  

2) Topic modeling  

Topic modeling is then performed using Latent Dirichlet Allocation (LDA) in python.  

12 topics were defined.  

Topics were then visualized using pyLDAvis.  

3) Graph theory 

A network of courses was then created. Each course is represented as a node in the network. Edges, or connections, between courses are defined as the cosine similarity of the topic scores.  The graph is threshold at 0.7 so that a course will not be recommended unless the cosine similarity between the recommended course and the current course is at least 0.7. A more stringent threshold of 0.95 is used to visualize the graph.  

4) Course recommendations  

<b>User input</b>: The user inputs a topic that is familiar to them, and a topic they wish to learn. The user can determine these topics by using the interactive `pyLDAvis` plot and by browsing the topic names that were defined for each topic. The user can also rate the importance of course similarity, ratings, popularity, and length (number of hours it takes to complete the course).  

<b>Behind the scenes</b>: The edges (weights) between courses are adjusted to be a weighted sum of course similarity, ratings, popularity, and length. These variables are first normalized between 0 and 1, and adjusted so that values closer to 1 indicate a higher cost (i.e. lower course similarity, lower ratings, lower popularity, and more hours required to complete the course are more costly). Then, the <b>shortest path</b>, a graph theory metric, is used to show the user the optimal path from the familiar topic to the new topic. The first and last courses in the path are defined by similarity to the familiar and new topics respectively, weighted by the weights that the user defines for course similarity, ratings, popularity, and length. 

<b>Output</b>: The web app returns the "path" or curriculum of courses that has been optimized for the user. This path is also visualized on the course network graph.  


