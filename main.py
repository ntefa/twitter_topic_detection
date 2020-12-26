
import pandas as pd
import numpy as np
import os
import time
import datetime
from datetime import datetime as dt
from Analytics.topic_finder import topic_detection
from Analytics.hot_terms_computing import compute_hot_terms
from Analytics.correlation import compute_corr_vector
import pickle
from Utils.merge_df import merge_df



if __name__ == '__main__':
    
    time1=time.time()
    
    ###parameter settings
    
    #system parameters
    preprocess=False #parameter to decide if preprocess data or not (alternative is reading pickles)
    lemma=0
    stop_words_flag= None
    num_flag=True
    shuffle=True
    
    ###algorithm parameters
    
    date='2020-04-19' 
    s=15
    sigma=100
    cutoff=.25
    threshold=6
    draw=False
    draw_graph=False
    
    path=os.getcwd()
    
    if preprocess:
                
        folder=f'{path}/Utils/data'
        
        dfs_list=merge_df(folder,shuffle=shuffle,lemma=lemma,n=s)
    
    else:

    
        name='2020-03-21-2020-04-19_num=True_lemma=0.pkl' #pickle file
            
        data=f'{path}/Utils/pickled_data/{name}'
        
        with open(data, 'rb') as f:

            dfs_list = pickle.load(f)   
            
    date2window={dfs_list[i].date[0][:10] : i for i in range(len(dfs_list))}
    
    window=date2window[date]
            
    final_path=topic_detection(dfs_list,window=window,s=s,sigma=sigma,cutoff=cutoff,threshold=threshold)
    time2=time.time()
    ex_time=str(datetime.timedelta(seconds=time2-time1))
    
    print(f'Execution Time: {ex_time}')
    #aggiungi orario inizio fine processamento
    with open(f"{final_path}/parameters.txt", "w") as file:
        file.write(f"Start Time: {dt.fromtimestamp(time1)}\n")
        file.write(f"End Time: {dt.fromtimestamp(time2)}\n")
        file.write(f"Execution Time: {ex_time}\n\n")
        file.write(f"Here the parameters for this analysis are stored:\n\n")
        file.write(f"preprocess= {preprocess}\n")
        file.write(f"lemma= {lemma}\n")
        file.write(f"window= {window}\n")
        file.write(f"s= {s}\n")
        file.write(f"sigma= {sigma}\n")
        file.write(f"cutoff= {cutoff}\n")
        file.write(f"threshold= {threshold}\n")
    
