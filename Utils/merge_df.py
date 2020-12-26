import pandas as pd
import os
import pickle
from os import listdir,getcwd
from os.path import isfile, join
from tqdm import tqdm
from Utils.preprocessing import preprocess


'''
Function to collect and preprocess the tweets csvs into list of dataframe, of more or less same length

Input: folder, where the csvs are saved (should be in same path as this script)

       lemma, [0,1,2] flag allowing to lemmatize or not (default=0, not lemmatized) 
       
       stop, [0,1] flag to decide whether reading stopwords from pickle (0 case) or txt (1 case). Both files are of type italian_stopwords.pkl/txt
       
       shuffle, Boolean flag used to decide whether to shuffle the dataframes and cut them to the length of the shortest one in order to preserve statistics, but losing data on the other hand 
       
       num, Boolean flag to decide whether or not to remove numbers
       
       window, day in the list of csvs to start from

       n, number of csvs to consider
       
       to_pickle, Boolean to decide if serialize the list into a pickle file
       
Output: list of df preprocessed dfs
'''

def merge_df(folder,shuffle=True,lemma=0,stop=0,num=True, window=0,n=0,to_pickle=False):

    #mypath=os.path.join(os.getcwd(),folder)
    mypath=f'{os.getcwd()}{folder}'
    name_list = sorted([mypath+'/'+f for f in listdir(mypath) if isfile(join(mypath, f))],reverse=True) 
    
    if n==0:
        n=len(name_list)
   
        
    if (n+window)>len(name_list):
        max_n=len(name_list)-window
        raise ValueError(f'With this window you can select at most n={max_n}')

    name_list=name_list [window:(n+window)]

    if shuffle:
        #We should have same length dfs, in order to maintain word statistics

        #For this reason we look for the least rows df and select filter the other ones 

        length=[]
        for i in name_list:
            length.append(len(pd.read_csv(i)))

        #minimum length across dfs    
        min_length=min(length)

        #list in which we collect dfs
        dfs_list=[]

        #iterate over csvs
        for i in tqdm(range(len(name_list))):

            df=pd.read_csv(name_list[i]).sample(frac=1,random_state=42).reset_index(drop=True).iloc[:min_length]
            #read csvs, apply mod to them after shuffling them and taking only min_length rows
            temp=preprocess(df,stop=stop,lemma=lemma,num=num)
            
            dfs_list.append(temp)
            
    else:
        
        dfs_list=[]

        #iterate over csvs
        for i in tqdm(range(len(name_list))):

            df=pd.read_csv(name_list[i])
            #read csvs, apply mod to them after shuffling them and taking only min_length rows
            temp=preprocess(df,stop=stop,lemma=lemma,num=num)
            
            dfs_list.append(temp)
        
        
    date0=dfs_list[0].date[0][:10] #first date
    date1=dfs_list[-1].date[0][:10] #last date
    
    if to_pickle:
        
        path=f'{os.getcwd()}/pickled_data'   
        
        
        with open(f'{path}/{date1}-{date0}_num={num}_lemma={lemma}.pkl', 'wb') as f:

            pickle.dump(dfs_list, f)
                
            
    return dfs_list


if __name__ == '__main__':
  
  
    folder='/data'
    
    lemma=[0,1]
    
    num=[False,True]
    
    for el1 in lemma:
        for el2 in num:
            
    
            dfs_list=merge_df(folder,lemma=el1,num=el2,stop=1,window=0,n=30,to_pickle=True)
    
    print(dfs_list[0].head())
    




        
        
        
        


