import networkx as nx
from Analytics.hot_terms_computing import compute_hot_terms
from Analytics.correlation import compute_corr_vector
from collections import defaultdict
import numpy as np
import os
import matplotlib.pyplot as plt
import pickle

'''
Function to transform a correlation vector, stored as a defaultdict of dict, in a dict of lists

Input: corr= correlation dict of dict

Output: G= graph, associates to each node a list of neighbours
        subG= subgraph, composed only by nodes of G being hot terms
'''

def build_graph(corr,hot_terms):

    #initialize defaultdict
    graph=defaultdict(dict)
    
    #iterate over words
    for word in list(corr.keys()):

        #transform dict in list
        graph[word]=list(corr[word])
    
    #transform defaultdict in dict
    graph=dict(graph)

    #initialize subgraph
    subgraph=defaultdict(dict)

    #iterate over hot terms
    for word in hot_terms:
        
        try:
            #subgraph is only composed by the elements of graph included in hot terms list
            subgraph[word]=graph[word]
            
        except:
            continue

    #create graphs
    G =nx.DiGraph(graph)
    subG=nx.DiGraph(subgraph)

    return G,subG


'''
Function to compute the strongly connected components in a graph.
After computing we only consider the ones including hot terms.

Input: corr= correlation dict of dict
       hot_terms= list of hot terms

Output: components= strongly connected components retrieved by whole graph
        sub_components= strongly connected components retrieved by subgraph
'''
def scc(corr, hot_terms):
    
    #build graph
    G, subG=build_graph(corr,hot_terms)


    #compute components if not composed just by 1 element and in hot terms. we need set because b this list comprehension every tuple is added twice
    components=set([tuple(c) for c in nx.strongly_connected_components(G) if (len(c)!=1) for el in c if (el in hot_terms)])
    
    #compute subcomponents
    sub_components=set([tuple(c) for c in nx.strongly_connected_components(subG) if (len(c)>1) for el in c if (el in hot_terms)])

    
    return components,sub_components


'''
Function used to draw the subgraph, for each component a different colour is used.

Input: corr= correlation dict of dict
       hot_terms= list of hot terms
       energy= terms energy
       flag= flag used to decide whether plot the subgraph (default) or the whole graph 

Output: graph plot
'''

#def draw_components(corr,hot_terms,energy,flag=1):
def draw_components(dfs,s=10,window=0,sigma=100,cutoff=.3,flag=1):

    df=dfs[window]
    corr=compute_corr_vector(df,cutoff=cutoff)
    
    hot_terms,energy,average=compute_hot_terms(dfs_list,s=s,window=window,sigma=sigma)
    #if default, build subgraph
    date=dfs_list[window].date[0][:10]
    name=f'subgraph_{date}.pdf'
    title= f'COMPONENTS OF COVID DATASET - {date}'

    #other case, build graph
    if flag==0:

        name=f'graph_{date}.pdf'

    #sort components from larger to smaller
    components= sorted(scc(corr,hot_terms) [flag] ,key=len,reverse=True)

    n=len(components)

    G=build_graph(corr,hot_terms)[flag]

    pos=nx.nx_agraph.graphviz_layout(G)

    gradient = np.linspace(0, 1, n+1)

    cs=list(range(n))

    #node_list=list(G.nodes())

    zipped=dict(zip(cs,gradient[:-1]))

    val_map={}

    for i in range(n):
        for e in components[i]:

            val_map[e]=zipped[i]


    values = [val_map.get(node, gradient[-1]) for node in G.nodes()]

    #node_size=[energy[node] for node in G.nodes()]
    #norm=max(node_size)
    #node_size= [item/norm*1000 for item in node_size]
    
    node_size=[500 if (node in hot_terms) else 200 for node in G.nodes()]

    fig, ax = plt.subplots()
    nx.draw(G, pos=pos,cmap=plt.get_cmap('viridis'), node_color=values,  font_color='white',node_size=node_size,width=.4, alpha=.8, arrowsize=3)


    #initialize label dicts
    labels1={}
    labels2={}

    #Assign label to hot terms and else to others
    for node in list(G.nodes()):
        
        if node in hot_terms:
            
            labels1[node]=node
            
        else:
            
            labels2[node]=node
        
    #hot terms plot larger
    nx.draw_networkx_labels(G,pos,labels1,font_size=4.5,alpha=1)

    #other terms
    nx.draw_networkx_labels(G,pos,labels2,font_size=2,alpha=1)

    title_obj=plt.title(title)
    plt.setp(title_obj, color='firebrick')         #set the color of title to blue

    path=os.getcwd()
    path=f'{path}/Analytics/draw_graph/{name}'
    
    
    #save figure in pdf
    plt.savefig(path,bbox_inches="tight")
    
    plt.show()
    
    return components 

if __name__ == '__main__':
    
    ###parameters to set
    name='2020-03-21-2020-04-19_num=False_lemma=1.pkl'
    s=6
    window=3
    sigma=100
    cutoff=.25
    flag=1
    ###
    
    path=os.getcwd()
    
    path=f'{path}/Utils/pickled_data/{name}'
    
    with open(path, 'rb') as f:

        dfs_list = pickle.load(f)   
    
    draw_components(dfs_list,window= window,s= s,sigma= sigma,cutoff= cutoff,flag=flag)
 
        
    
