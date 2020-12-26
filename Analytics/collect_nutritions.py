import os
from pathlib import Path
from Analytics.hot_terms_computing import nut
import pickle
from tqdm import tqdm
'''
Function used to collect energies over different days

INPUT: dfs, list of dataframes
       n, number of days (default=len(dfs))
'''

def collect_nutritions(dfs,n=30,to_pickle=True):
    
    if n>len(dfs):

        maximum=len(dfs)
        n=len(dfs)
     
        
    if n<=0:

        raise ValueError(f'n must be greater!')


    #initialize variables
    nutr_squared=[]
    energy={}
    date_list=[]
    
    #compute nutrition for each df and square it, appending it to a list       
    for i in tqdm(range(n)):
        
        date_list.append(dfs[i].date[0][:10])
        temp=nut(dfs[i],.1)

        #nutr_square is a list of dict
        nutr_squared.append({k: pow(v,2.) for k, v in temp.items()})
        
    
    #normalized_nutr=minmax_scale(nutr_squared) normalizza nel plot

    nutr_dict=dict(zip(date_list,nutr_squared))

    if to_pickle:
        
        path=os.getcwd()
        path=f'{path}/Analytics/pickled_energies'
        date0=date_list[0] #last date
        date1=date_list[-1] #first date
        
        with open(f'{path}/nutrition_{date1}-{date0}.pkl', 'wb') as f:        
            pickle.dump(nutr_dict, f)
        
    return nutr_dict

if __name__ == '__main__':
    
    name='2020-03-21-2020-04-19_num=True_lemma=0.pkl' #name of pickle file where dfs are stored
    
    path=os.getcwd()
    path=f'{path}/Utils/pickled_data/{name}'
    
    with open(path, 'rb') as f:

        dfs_list = pickle.load(f)   
        
    result=collect_nutritions(dfs_list,n=30)

 
