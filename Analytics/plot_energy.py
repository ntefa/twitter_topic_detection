import matplotlib.pyplot as plt
import numpy as np
import os
import pickle
from collections import defaultdict
from sklearn.preprocessing import minmax_scale

'''
Function used to plot the energy of a word over time

Input: window_energy= energy of all words over N windows, retrieved by collecting_emerging_terms
       
       word_list= list of words whose energy has to be plotted

Output: plot
'''


### Note that this works if all the words are in the days dicts, if not crashes
import matplotlib.pyplot as plt

def plot_energy_over_time(energy_dict,word_list):
    
    path=os.getcwd()

    
    for word in word_list:
    
        energy_list=[]
        date_list=[]
        #create energy list starting from first day to last
        for key in energy_dict.keys():
            energy_list.append(energy_dict[key][word])
            date_list.append(key)
        energy_list=minmax_scale(energy_list)
        
        date_list=list(reversed(date_list))
        e=np.array(list(reversed(energy_list)))
        plt.figure(figsize=(20,15))
        plt.plot(date_list,e,color='black')
        #fill according to whether it's higher than 0 or not
        plt.fill_between(date_list, 0, e, where=e>=0,interpolate=True)
        plt.fill_between(date_list, 0, e, where=e<=0,facecolor='red',interpolate=True)
        plt.xticks(fontsize=16)
        plt.yticks(fontsize=16)

        plt.xticks(rotation=55)
        plt.xlabel('Date',fontsize=20)
        plt.ylabel('Word Energy',fontsize=20)
        plt.title(f'Energy variation for word "{word}" over time',fontsize=20)
        plt.grid(axis='x')
        plt.savefig(f'{path}/Analytics/energies/{word}.pdf')

        #plt.show()
    
if __name__ == '__main__':
    
    name='nutrition_2020-03-21-2020-04-19.pkl'
    words=['salvini','boris','vaccino','corona','conte','borrelli','trump','emergenza','mes','meloni']

    path=os.getcwd()

    path=f'{path}/Analytics/pickled_energies/{name}'
    
    with open(path, 'rb') as f:

        en_dict = pickle.load(f)   
    
    words=['salvini','boris','vaccino','corona','conte','borrelli','trump','emergenza','mes','meloni']
    plot_energy_over_time(en_dict,words)
        
 

