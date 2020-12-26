import pandas as pd
import itertools
import collections
import os
import pickle
import numpy as np
from collections import defaultdict

'''
Function to compute the cooccurences between words across the list of list.

Input: list of lists describing tweets

Output: bigram_counts= count of cooccurrences

        words= list of unique words

        counts= count of words 
'''


def compute_cooccurrences(list_of_tweets):
    
    # all words with repetition
    all_words = list(itertools.chain(*list_of_tweets))

    # Create counter
    counts = collections.Counter(all_words)

    # all words without repetition
    words=list(counts.keys())

    #create list of tuples for wach combination between 2 words in a tweet
    big=[(x,y) for tweet in list_of_tweets for (x,y) in list(itertools.product(tweet,repeat=2)) if x!=y ]
   
    #count the combination across whole list. It results in an object describing cooccurrences between words
    bigram_counts = collections.Counter(big)
    
    return bigram_counts,words,counts




'''
Function to compute correlation vector. It returns a dict for each word showing how it's correlated with the other ones.

Input: df= Dataframe

       cutoff= threshold used to thin the graph (default=.1). The higher less words are correlated, the less                  more. If chosen a small threshold, it might be that the whole graph is strongly connected. 

Output:  corr= normalized correlation, dict of dict

         diz= correlation, dict of dict
'''
def compute_corr_vector(df,cutoff=.1):
    
    #extract tweets column from df
    tweets=df.text

    #compute cooccurrences
    bigram_counts, words , count= compute_cooccurrences(tweets)
    
    #initialize defaultdict
    diz = defaultdict(dict)

    #iterate over pairs and values of bigram_counts
    for p, v in bigram_counts.items():
        
        
        rkz=v #cooccurence between k and z
        nz=count[p[1]] #count of how many times z appears in tweets
        rk=count[p[0]] #count of how many times k appears in tweets
        N=len(df) #number of tweets

        # avoid these values
        if (nz==rkz or rk==rkz or rkz==0 or p[0]==p[1]):
            continue

        #coefficient computation
        ckz=np.log((rkz/(rk-rkz))/((nz-rkz)/(N-nz-rk+rkz)))*np.abs(rkz/rk - (nz-rkz)/(N-rk))

        #associate coefficient to pair 
        diz[p[0]][p[1]]=ckz
            
    #initialize defaultdict        
    correlation=defaultdict(dict)

    #iterate over words in diz
    for word1 in list(diz.keys()):  #list(set())

        #set temporary array of all correlation value per word
        temp=np.array(list(diz[word1].values()))

        #compute norm
        norm=np.linalg.norm(temp)    

        #iterate over words correlated with first
        for word2 in list(diz[word1].keys()):

            #for each word normalize score
            temp2=diz[word1][word2]/norm

            #keep only strong relationship
            if np.abs(temp2)>=cutoff:
                correlation[word1][word2]=temp2
                    
    return correlation


if __name__ == '__main__':
    
    path=os.getcwd()
    
    path=f'{path}/Utils/pickled_data/2020-04-07-2020-04-16_lemma1.pkl'
    
    with open(path, 'rb') as f:

        dfs_list = pickle.load(f)  
    
    df=dfs_list[0]
    
    correlation=compute_corr_vector(df,cutoff=.3)
    
    temp1=correlation['sepulveda']
    temp2=correlation['virus']
    
    print(f'{temp1}')
    print('\n')
    print(f'{temp2}')
    
