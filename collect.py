# Imports you'll need.
from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
import sys
import time
from TwitterAPI import TwitterAPI
from itertools import combinations
import itertools
import time
import os
import sys
import json
import argparse
import glob
from matplotlib import pylab
import pickle
from itertools import islice, chain
# Insert Keys and credentials 
consumer_key = ''
consumer_secret = ''
access_token = ''
access_token_secret = ''





# This method returns a Twitter Handle
def get_twitter():
    return TwitterAPI(consumer_key, consumer_secret, access_token, access_token_secret)



# should call this method whenever need to access the Twitter API.
def robust_request(twitter, resource, params, max_tries=5):
    """ If a Twitter request fails, sleep for 15 minutes.
    Do this at most max_tries times before quitting.
    Args:
      twitter .... A TwitterAPI object.
      resource ... A resource string to request; e.g., "friends/ids"
      params ..... A parameter dict for the request, e.g., to specify
                   parameters like screen_name or count.
      max_tries .. The maximum number of tries to attempt.
    Returns:
      A TwitterResponse object, or None if failed.
    """
    for i in range(max_tries):
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            print('Got error %s \nsleeping for 15 minutes.' % request.text)
            sys.stderr.flush()
            time.sleep(61 * 15)




def read_config(config_file):
    outf = open(config_file)
    data = json.load(outf)
    query = data['q']
    f_count = data['friends_count']
    fw_count = data['followers_count']
    central_nodes = data['subset_uids_for_graph']
    return query, f_count, fw_count, central_nodes

def lines_fetch_per_json(fil, n):
    for line in fil:
        yield ''.join(chain([line], itertools.islice(fil, n - 1)))


def fetch_users_for_graph():
    f = open('tweets_collect.json')
    count = 0
    uid_list = {}
    for chunk in lines_fetch_per_json(f, 5):
        d_json = json.loads(chunk)
        s = d_json['screen_name']
        if s not in uid_list:
            uid_list[s] = d_json['id']
            count = count+1
        if(count>15):
            break
    return uid_list
    f.close()



def main():
    
    twitter = get_twitter()
    total_count = 12 # total number of request for tweets
    total_tweet = 0
    # first fetching 200 tweets before going to collect data for long duration, it wll help in demo, to avoid data crunch problem.
    l=robust_request(twitter, 'search/tweets', {'q': 'football','count':100,'lang':'en'})
    count = 1
    js = l.json()
    uid_list={}
    idx = 0 
    print("Collecting tweets and user data.....")
    outf = open('tweets_collect.json', 'w')
    # now going in loop to get new tweets as well as users friend/follower data
    # This way it will ensure us that in begining itself we would be having enough data for demo.
    while count < total_count:
        l = len(js["statuses"])
        total_tweet += l
        since = js["search_metadata"]["max_id"]
        #print('len', len(js["statuses"]))       
        for i in range(l):
            #print('index', i)
            d_json ={'id': js["statuses"][i]["user"]["id"],'text':js["statuses"][i]["text"],'screen_name':js["statuses"][i]["user"]["screen_name"] }
            outf.write(json.dumps(d_json, indent=1))
            outf.write("\n")
        count += 1
        l=robust_request(twitter, 'search/tweets', {'q': 'football','count':100, 'since_id': since,'lang':'en' })
        js = l.json()
    outf.close()

    uid_list = fetch_users_for_graph()

    for key,value in uid_list.items():
        #print("Getting frnds for :", key)
        l=(robust_request(twitter, 'friends/ids', {'screen_name': key, 'count': 1000 }).json())['ids']
        m=(robust_request(twitter, 'followers/ids', {'screen_name': key, 'count': 1000 }).json())['ids']
        name = "user_"+str(idx)+".json"
        #print("File being created", name)
        outf_ = open(name, 'w')
        d_json_ = {'id': value,'screen_name':key, 'friends':l,'followers':m }
        outf_.write(json.dumps(d_json_, indent=1))
        idx= idx + 1
        if idx ==14:
            break
    outf_.close()

    print("Twitter data collection completed")
    print("Tweets are dumped into tweets_collect.json")
    print("User data dumped in user_*.json files")  
    print("%d tweets and %d user profiles are dumped on disk" %(total_tweet, len(uid_list)))

if __name__ == '__main__':
    main()
