import pandas as pd
import itertools
import collections
from collections import defaultdict
import pickle
import numpy as np
import os
import plotly.graph_objects as go


'''

Function to compute the augmented term frequency for each tweet.

Input: list of dfs

Output: List of dict associating to each word in tweets a score

'''

def tf_eval(df):
    
    #get a list of all words
    all_words = list(itertools.chain(*df.text))

    # Create counter. The word occurrences are computed
    count= collections.Counter(all_words)
    
    #Here we create a list of lists with the related count for each term in tweet
    temp=[]
    TF=[]
    for tweet in df.text:
        temp=[]

        for token in tweet:
            temp.append(count[token])

        TF.append(temp)
        

    #Here we compute the augmented term frequency

    temp=[]
    tf=[]

    #iterate over TF and compute maximum value per tweet
    for tweet in TF:
        temp=[]
        max_value=max(tweet)
        
        #here we modify the score according to the new formula, after getting the maximum score
        for token in tweet:
            temp.append(0.5+0.5*token/max_value)

        tf.append(temp)

    #Create list of dict by zipping the new score to each term
    tf=[dict(zip(df.text[i],tf[i])) for i in range(len(df))]

    
    return tf,count



###authority

def nut(df, hashtag_burst=.1):

    #apply tf eval to get augmented term frequency and words count    
    tf,count=tf_eval(df)
    
    #create dict associating to each user its influence score
    auth=dict(zip(df.name,df.followers/(df.following+df.followers)))

    #replace nans with zero. This happens if a user doesn't follow anyone, as well as not being followed back
    auth= {k: 0 if np.isnan(v) else v for k, v in auth.items() }
    
    #hashtags series. If a word is found in hashtag, its energy gets burst by 5%
    tags=df.hashtags
    
    nutr={}
    
    #iterate over unique words
    for token in  count.keys():

        temp=[]

        #iterate over tweets
        for i in range(len(tf)):
            
            #if considered word is in tweet
            if token in tf[i]:
                #new score computed (N.B. the order is preserved within tf and auth, i.e. they relates to                       same tweets)
                score=tf[i][token]*auth[df.name[i]]

                if token in tags[i]:
                    #50% increment if hashtag
                    score=score+score*(hashtag_burst)

                temp.append(score)
  
        #final score for each word is computed by summing up
        somma=sum(temp)

        #and then added to dict
        nutr[token]=somma   
    
    return nutr



'''
Function that computes hot terms.

Input: dfs=list of dataframes, indexed from newest (0) to oldest (5 in our case)

       s= number of windows to consider (default= 6, i.e. all)

       sigma= dropoff value used as threshold to detect hot terms; the higher the less the terms are, and viceversa
       
       hashtag_burst= energy increment as % if term is hashtagged

Output: hot terms= list of retrieved terms

        energy= energy of terms
'''

def compute_hot_terms(dfs,s=10,window=0,sigma=100, hashtag_burst=.1,draw=False): 

    if (s+window)>(len(dfs)-1):

        maximum=len(dfs)-window-1

        #raise ValueError(f'Number of windows out of length. For this window, s can be at most {maximum}!')
        s=maximum
        
    if s<0:

        raise ValueError(f's must be greater or equal to 0!')


    #initialize variables
    nutr_squared=[]
    energy={}
    
    #compute nutrition for each df and square it, appending it to a list       
    for i in range(window, window+s+1):
        
        temp=nut(dfs[i],hashtag_burst)

        #nutr_square is a list of dict
        nutr_squared.append({k: pow(v,2.) for k, v in temp.items()})

    #set new energy terms
    new=nutr_squared[0]

    #set initial dict values to 0    
    energy={k: 0 for k in new.keys()}

    #if 0 it wouldn't iterate and set the value
    if s>0:
        #iterate over dfs
        for i in range(1,s+1):
            
            #set old energy terms, it changes at each iteration
            old=nutr_squared[i]

            #compute difference and divide by window shift. If word not in previous time windows, just use                  energy value of new
            
            diff_temp={k: (new[k] - old[k])/i if k in old else new[k]/i for k in new}

            #sum the energy with diff_temp. It gets updated at each iteration   
            energy={k: energy[k]+diff_temp[k] for k in energy.keys() if k in diff_temp}

    else: #if 0 or negative(?)

        energy=new

    average= np.array(list(energy.values())).mean()

    if average<=0:

        pos_values=[v for v in energy.values() if v>0]    

        #Compute the average between them
        average=np.array(pos_values).mean()
        
    #dropoff value
    drop=sigma*average 
    
    #emergent terms are the one whose energy is higher than drop
    hot_terms=[k for k,v in energy.items() if  v>= drop]
    
    date=[]
    
    for j in range(len(hot_terms)):

            date.append(dfs[0].date[0] [:10])
    if draw:
        
        draw_emerging_terms(hot_terms,energy,average,date,sigma)
    
    return hot_terms,energy,average


'''
Function used to draw the hot terms within all single windows and relative energies

Input: dfs, list of dfs
       
       sigma, dropoff value used as threshold to detect hot terms; the higher the less the terms are, and                    viceversa

     

Output: table

'''

def draw_emerging_terms(hot_terms,en,av,date,sigma):
    
    #apply previous function

        energy=[]

        for term in hot_terms:

            #create energy list for each window
            energy.append(en [term])
            
        diz=dict(zip(hot_terms,energy))
            
        hot_terms=[k for k,v in sorted(diz.items(), key=lambda item: item[1], reverse=True)]
        energy=sorted(energy,reverse=True)

        fig = go.Figure(data=[go.Table(columnorder = [1,2,3],
                                    columnwidth = [20,20,20],
                                    
                                    header=dict(values=['<b>DATE</b>', '<b>EMERGING TERMS</b>',f'<b>ENERGY</b> (average = {int(av)})'],
                                    
                                    line_color='white',
                                    fill_color='midnightblue',

                                    font=dict(color='white', size=10),
                                    height=18),
                                    cells=dict(values=[date, hot_terms,energy],
                                    line_color='white',
                                    fill=dict(color=['gainsboro', 'gainsboro','gainsboro'])
                                    ,align= 'center',
                                    height=18))
                            ])

        fig.update_layout(title=f"Emerging Terms - sigma={sigma}",font=dict(
                family="Courier New, monospace",
                size=10,
                color="darkslategray"
            ))

        time=date[0][:10]
        
        

        fig.write_image(f"Analytics/emerging_terms/terms_{time}_sigma={sigma}.pdf")

        fig.show()

if __name__ == '__main__':
    
    s=10
    window=0
    sigma=100
    burst=.1
    
    path=os.getcwd()
    
    path=f'{path}/Utils/pickled_data/2020-04-07-2020-04-16_lemma1.pkl'
    
    with open(path, 'rb') as f:

        dfs_list = pickle.load(f)     
        
    hot_terms,energy,average=compute_hot_terms(dfs_list,s=s,window=window,sigma=sigma, hashtag_burst=burst,draw=True)   
    
    
