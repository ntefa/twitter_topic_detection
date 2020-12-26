import pandas as  pd
from Analytics.hot_terms_computing import compute_hot_terms
from Analytics.correlation import compute_corr_vector
from Analytics.scc import scc
import plotly.graph_objects as go
from collections import defaultdict
import os
from os.path import normpath, basename
import matplotlib.pyplot as plt
import pickle
from datetime import datetime



'''
Function used to rank our topics energy-based

Input: components= list of strongly connected components
       energy= words energy
 Output: out= list of sorted strongly connected components       
'''

def comp_ranking(components, energy):

        #initialize ranking dict terms 
        ranking=defaultdict(dict)

        #iterate over topics
        for term in components:
        
                #initialize summ at 0 :
                summ=0

                for word in term:                       
        
                        #update it with current word energy 
                        summ+=energy[word]
                        
                #divide by length of current topic    
                summ/=len(term)
                
                #dict associating to each topic a value                   
                ranking[term]=summ 

        #sort ranking by value(term)
        out=[list(k) for k,v in sorted(ranking.items(), key=lambda item: item[1], reverse=True)]
        
        return out
    
            
            
            
'''
Function to cutoff topics according to word energy and number of words equal to threshold

Input: topics=list of topics
       energy= words energy
       threshold= number of maximum words per topic

Output: list_of_topics= final list of topics
'''

def topic_finder(topics,energy,threshold):
    
        #copy list_of_topics because lists are mutable objets in python
        list_of_topics=topics.copy()
        
        #iterate over topics
        for i in range(len(list_of_topics)):
            
            topic=list_of_topics[i]
            
            #if topic shorter than threshold, ok
            if len(topic)<=threshold:
                continue

            
            else:
                temp1={}

                #iterate over each word in topic
                for word in topic:
                    
                    #create temp dict per word
                    temp1[word]=energy[word]

                #sort dict per value in descending order   
                temp2=[k for k,v in sorted(temp1.items(), key=lambda item: item[1], reverse=True)]
            
            #select only elements until threshold
            list_of_topics[i]=temp2[:threshold]
            
        return list_of_topics
    
    
    
'''
Function to find topics

Input: corr= correlation dict of dicts
       energy= words energy
       hot_terms= list of emergent terms
       threshold=maximum number of words per topic

Output: List of topics
'''

def find_topic(corr, energy,hot_terms,threshold):
    
    components,sub_components=scc(corr, hot_terms)

    topics=comp_ranking(components,energy)    

    return topic_finder(topics,energy,threshold)




'''
Function to draw topic table

Input: topics= correlation dict of dicts
       date= string describing the date of the window

Output: Topics table
'''

def draw_topics(topics,date):

    #create list of dates 
    dates=[]
    for i in range(len(topics)):

        dates.append(date)

    fig = go.Figure(data=[go.Table(columnorder = [1,2],
                                columnwidth = [1,5],
                                
                                header=dict(values=['<b>DATE</b>', '<b>TOPICS</b>'],
                                
                                line_color='white',
                                fill_color='midnightblue',
                                #font_size=10,
                                font=dict(color='white', size=8),
                                height=15),
                                cells=dict(values=[dates, topics],
                                line_color='white',
                                fill=dict(color=['gainsboro', 'gainsboro'])
                                ,align=['center','left'],
                                font_size=5,
                                height=13))
                        ])
    fig.update_layout(width=400, height=500)
    '''
    fig.update_layout(
        title="Topics",font=dict(
            family="Courier New, monospace",
            size=10,
            color="darkslategray"
        ))
    '''
    time=int(dates[0][:4])
    

    path=os.getcwd()
    
    path=f'{path}/Results'
    
    date=datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    
    if not os.path.exists(f"{path}/analysis_{date}"):
        os.mkdir(f"{path}/analysis_{date}")

    #save to directory
    fig.write_image(f"{path}/analysis_{date}/topics.pdf")

    final_path=f"{path}/analysis_{date}"
    
    #fig.show()
    
    return final_path
    
'''
Function that process the dataframe and return topics and hot terms

Input: dfs_list= list with dfs
       window= which dataframe has to be used to detect topics
       s=number of dfs to use for the hot terms computation
       sigma=drop value for detecting hot terms
       cutoff=edge thinning threshold
       threshold=maximum number of words per topic
       plot, if True return subgraph plot

Output: Table of topics
'''


def topic_detection(dfs_list,window=0,s=6,sigma=10,cutoff=.25,threshold=7):

    #set reference dataframe
    df=dfs_list[window]

    date=df.date[0] [:10]

    hot_terms,energy,av=compute_hot_terms(dfs_list,s,window,sigma, draw=False)

    corr=compute_corr_vector(df,cutoff=cutoff)

    topics=find_topic(corr,energy,hot_terms,threshold=threshold)

    final_path=draw_topics(topics,date)
    
    return final_path
    
    

if __name__ == '__main__':
    
    path=os.getcwd()
    
    path=f'{path}/Utils/pickled_data/2020-04-07-2020-04-16_lemma1.pkl'
    
    with open(path, 'rb') as f:

        dfs_list = pickle.load(f)   
        
    final_path=topic_detection(dfs_list)  
    
    
        
      
