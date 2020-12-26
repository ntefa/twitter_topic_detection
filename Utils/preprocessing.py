 
import pandas as pd
import nltk
import numpy as np
import itertools
from collections import defaultdict
import treetaggerwrapper 
import ast
import os
import pickle
import re
import emoji


'''
Function to transform hashtag string of dict into list of words
'''
def hashtag_extrapolation(df):

    df1=df.copy()
    
    def hashtag_retrieval(hashtag_field):

        try:
            #convert hashtag field into list of dict
            temp=ast.literal_eval(hashtag_field)

            #we are interested in the text field, including the hashtag keyword, and transform it to lower case
            return [item['text'].lower() for item in temp] 

        except IndexError:
            return temp

    #apply it for all rows of the dataframe
    df1.hashtags=df1.hashtags.apply(lambda x: hashtag_retrieval(x))

    return df1


'''
Function to remove single chars after tokenization because not useful to our goal    
'''

def remove_single_char(tweet):
    
    for word in tweet.copy():
        
        #remove word if single char
        if len(word)==1:
            
            tweet.remove(word)
            
    return tweet

'''
Function to remove emojis from text
'''
# We use the emoji library, that allows us to do it in just one line of code

def no_emoji(df):
    
    df1=df.copy()
    def remove_emoji(text):
        return emoji.get_emoji_regexp().sub(u'', text)

    #apply it for all rows of dataframe
    df1.text = df1.text.apply(lambda x: remove_emoji(x))

    return df1

'''
Function used to lemmatize words.
Tretagger used, not easy to install, if problems skip and process without
'''

def lemmatize(df):
    
    current_path=os.path.abspath(os.getcwd())
    tree_path=f'{current_path}/Treetagger/'

    #setup tagger obj
    tagger = treetaggerwrapper.TreeTagger(TAGLANG="it",TAGDIR=tree_path)
    
    #get tweets
    tweets=df.text

    sep=' '

    #initialize output
    lemmatized_tweets=[]

    #iterate over tweets
    for tweet in tweets:

        temp=[]

        #tagger takes string of words as input and returns a Tag object for each word
        #here we transform the list of words into string, keeping the part of speech per tweet
        tags = tagger.tag_text(sep.join(tweet))

        #return Tag object
        tags2=treetaggerwrapper.make_tags(tags)

        #iterate over Tag: idx 0 original word, idx 1 part of speech, idx 2 lemma
        for word in tags2:

            if (word.__class__.__name__=='Tag'):
                
                # if original word within this list or number, whose lemma seems to be @card@, append original
                if (word[0] in ['lega','conte','meloni','salvini','cucchi'] or word [2]=='@card@'):

                    temp.append(word[0])

                #else append lemma
                else:
                    
                    temp.append(word[2])

        #append list for each tweet
        lemmatized_tweets.append(set(temp))

    return lemmatized_tweets

'''
2nd option to lemmatize with
Here the lemmatization is performed before tokenization, tweet per tweet maintaining the sense of speech.

Note: computational complexity much higher!
'''

def lemmatize2(df):

    df1=df.copy()
    
    current_path=os.path.abspath(os.getcwd())
    tree_path=f'{current_path}/Treetagger/'

    keywords=['conte','lega','meloni','salvini','renzi']
    tagger = treetaggerwrapper.TreeTagger(TAGLANG="it",TAGDIR=tree_path)
    
    tweets=df1.text
    lemma=[]
    new_tweets=[]
    for tweet in tweets:
        tags = tagger.tag_text(tweet)
        tags2=treetaggerwrapper.make_tags(tags)

        for word in tags2:
            if (word.__class__.__name__=='Tag' and word[0] not in keywords and word[2]!='@card@'):
                lemma.append(word[2])
            else:
                lemma.append(word[0])

        new_tweets.append(lemma)

    df1.text=pd.Series(new_tweets)

    return df1

'''
def remove_num(tweet):
    
    string_no_numbers = re.sub("\d+", "", tweet)
    
    return string_no_numbers
'''
def remove_num(tweet):
    
    for word in tweet.copy():
        
        try:
            int(word)
            tweet.remove(word)
            
        except:
            continue
    
    return tweet
    
    

def stop_words_removal(df,stop=0):

    current_path=os.path.abspath(os.getcwd())
    path=f'{current_path}/italian_stopwords.pkl'

    #default, read from pickle
    with open(path, 'rb') as f:

        stop_words = pickle.load(f)    #aggiungi flag 0 per pickle e 1 per file di testo
    
    #if stop=1 read from txt
    if stop==1:
        path=f'{current_path}/italian_stopwords.txt'
        
        with open(path, 'r') as f:
            stop_words = [line.strip() for line in f]   
            
    #dataframe are mutable objects in python, better to modify a copy
    df1=df.copy()
    
    
    df1.text = df1.text.apply(lambda x: x.replace("'"," "))
    
    #remove symbols
    symbols = "'!\"#$%&()*+-./:;,<=>?@[\]^_`{|}~\…«»"
    
    for i in symbols:
        df1.text = df1.text.apply(lambda x: x.replace(i, ' '))
    
    #tokenize tweets
    df1.text = df1.text.apply(lambda x: nltk.word_tokenize(x))


    #remove stopwords
    filtered_list=[[ word for word in tweet if not word in stop_words] for tweet in df1.text.to_list()]
    
    #2nd run remove symbols
    symbols=['’',"'","n't",'‘',"'s","‘",'“','”','``','ã¨']
    filtered_list=[[ word for word in tweet if not word in symbols] for tweet in filtered_list]

    #filtered_list=[tweet for word in tweet if word!= 'eu' for tweet in filtered_list]

    df1.text=pd.Series(filtered_list)
    
    return df1


'''
Function that envelopes all previous functions and modifies the dataframe

Set stop to 1 if you want to read stopwords from text file instead of pickle

Set lemma=1 if you want to lemmatize

Set num=False if you want not to remove numbers


'''

def preprocess(df,stop=0,lemma=0,num=True):
    
    df=hashtag_extrapolation(df)
    
    df.text=df.text.apply(lambda x: np.char.lower(x))
    
    #remove links
    sep = 'https'
    
    df.text=df.text.apply(lambda x: x.split(sep,1)[0])
    
    #remove tags and hashtags
    df.text=df.text.apply(lambda x: " ".join(filter(lambda y:y[0] not in ['@','#'], x.split())))
     
    #apply function to remove emojis   
    df=no_emoji(df)
        
    if lemma==2:
        df=lemmatize2(df)
        
        
    #remove stopwords    
    df=stop_words_removal(df,stop)

    #add hashtags to text if aren't (risk of duplicate avoided by set hereunder)
    df.text=pd.Series(df.hashtags+df.text)

    #get only unique elements in tweet
    df.text=df.text.apply(lambda x: set(x))
    
    #remove single characters
    df.text=df.text.apply(lambda x: remove_single_char(x))
    
    if lemma==1:
       df.text=pd.Series(lemmatize(df))
       
    if num:
        df.text=df.text.apply(lambda x: remove_num(x))

    #remove no text or single word tweets
    no_text_idx= [i for i in range(len(df)) if (not df.text[i] or len(df.text[i])==1 or ('eu' in df.text[i]))] #I added eu because there was a mistake in writing keywords, so I collected some brazilian tweets with         common word eu, that we filter out

    df=df[~df.index.isin(no_text_idx)].reset_index(drop=True)

   
        
    return df


if __name__ == '__main__':
    
    current_path=os.path.abspath(os.getcwd())
    data_path=f'{current_path}/data/data_20200414.csv'
        
    df=pd.read_csv(data_path)
    
    #lemmatized
    df_new=preprocess(df,stop=0,lemma=0,num=True)
    
    #not lemmatized
    #df_new=mod(df)
    
    print(df.head(5).text)
    print(df_new.head(5).text)
    
