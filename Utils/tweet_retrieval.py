 ###importing libraries for tweets fetcher
import os

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import time
import csv
import sys


#Parameter
queries=['Salvini','Conte','PD','salvini','conte','pd','lega','Lega']


###Create a void csv file with the needed fields

filename = 'data'+'_'+time.strftime('%Y%m%d')+'.csv'
current_path=os.path.abspath(os.getcwd())
path=f'{current_path}/data/{filename}'
with open(path, 'w') as csvFile:

            # Create a csv writer
            csvWriter = csv.writer(csvFile)

            # Write a single row with the headers of the columns
            #headers=[["text",'id','hashtags',"date","name",'user_id','followers','following','lists','likes','tweets','creation_date']
            headers=["text",'id','hashtags',"date","name",'user_id','followers','following','lists','likes','tweets','creation_date']

            csvWriter.writerow(headers)



# Create a streamer object
class StdOutListener(StreamListener):
    
    # Define a function that is initialized when the miner is called
    def __init__(self, api = None):
        # That sets the api
        self.api = api
        # Create a file with 'data_' and the current time
        #self.filename = 'data'+'_'+time.strftime('%Y%m%d-%H%M%S')+'.csv'
        self.filename = 'data'+'_'+time.strftime('%Y%m%d')+'.csv'
        
        self.current_path=os.path.abspath(os.getcwd())
        
        self.path=f'{current_path}/data/{filename}'
       
    # When a tweet appears
    def on_status(self, status):
        
        # Open the csv file created previously
        csvFile = open(self.path, 'a')
        
        # Create a csv writer
        csvWriter = csv.writer(csvFile)
        
        # If the tweet is not a retweet
        if not 'RT @' in status.text:
            
            #if status.extended_tweet['full_text']:
                # Try to 
                try:
                    # Write the tweet's information to the csv file
                    csvWriter.writerow([status.extended_tweet['full_text'],
                                        status.id,
                                        status.entities['hashtags'],
                                        status.created_at,
                                        status.user.name,
                                        status.user.id,

                                        status.user.followers_count,
                                        status.user.friends_count,
                                        status.user.listed_count,
                                        status.user.favourites_count,
                                        status.user.statuses_count,
                                        status.user.created_at

                                       ])
                # If some error occurs, it means that the text is below 140 characters, and status doesn't have the extended_tweet field.
                
                except AttributeError:
                                      
                    csvWriter.writerow([status.text,
                                        status.id,
                                        status.entities['hashtags'],
                                        status.created_at,
                                        status.user.name,
                                        status.user.id,

                                        status.user.followers_count,
                                        status.user.friends_count,
                                        status.user.listed_count,
                                        status.user.favourites_count,
                                        status.user.statuses_count,
                                        status.user.created_at
                                       ])
            
            
        # Close the csv file
        csvFile.close()

        # Return nothing
        return

    # When an error occurs
    def on_error(self, status_code):
        # Print the error code
        print('Encountered error with status code:', status_code)
        
        # If the error code is 401, which is the error for bad credentials
        if status_code == 401:
            # End the stream
            return False

    # When a deleted tweet appears
    def on_delete(self, status_id, user_id):
        
        # Print message
        print("Delete notice")
        
        # Return nothing
        return

    # When reach the rate limit
    def on_limit(self, track):
        
        # Print rate limiting error
        print("Rate limited, continuing")
        
        # Continue mining tweets
        return True

    # When timed out
    def on_timeout(self):
        
        # Print timeout message
        print(sys.stderr, 'Timeout...')
        
        # Wait 10 seconds
        time.sleep(10)
        
        # Return nothing
        return
    



# Create a mining function
def start_mining(queries):
    '''
    Inputs list of strings. Returns tweets containing those strings.
    '''
    
    #Variables that contains the user credentials to access Twitter API
    consumer_key = 'O4bVqZEBEWcn7kNAM9Z6FQzYG'
    consumer_secret = '6x7GkAsh0MqKsF1bDBCWGznpHv0MPb9NRyDEK6UJf9nksFqys8'
    access_key= '380204462-akGRNmWHQBWKEPYnceNyO6hC0aGO5PsIqXoFB1qU'
    access_secret = 'oR3V1zF5i4fw4Q2F4zMnsAK5uqW1r8PciDrrxCzdSVxYq'


    # Create a listener
    l = StdOutListener()
    
    # Create authorization info
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    
    # Create a stream object with listener and authorization
    stream = Stream(auth, l)

    # Run the stream object using the user defined queries
    stream.filter(languages=['it'],track=queries)
    
    

start_mining(queries)
