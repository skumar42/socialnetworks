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
from collections import defaultdict
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import re
import numpy as np
from itertools import islice, chain
import itertools

'''
pos_instance =     ' \n'
neg_instance =     ' \n'
neutral_instance = ' \n'
pos_example = 0
neg_example = 0
net_example = 0
'''
# Load the affinity of words
def load_affin(afinn_file):
    afinn = {}
    for line in afinn_file:
        parts = line.strip().split()
        if len(parts) == 2:
            afinn[parts[0].decode("utf-8")] = int(parts[1])
    return afinn


def lines_fetch_per_json(fil, n):
    for line in fil:
        yield ''.join(chain([line], itertools.islice(fil, n - 1)))

# returns score as sum of over all affinity including +ve and -Ve
def afinn_sentiment_score(terms, afinn, verbose=False):
    pos = 0
    neg = 0
    for t in terms:
        if t in afinn:
            if verbose:
                print('\t%s=%d' % (t, afinn[t]))
            if afinn[t] > 0:
                pos += afinn[t]
            else:
                neg += afinn[t]
    return pos+neg


#tokenize the text
def tokenize(text):
    return re.sub('\W+', ' ', text.lower()).split()

#custom to read json from file and slie out extra part
def lines_per_n(f, n):
    for line in f:
        yield ''.join(chain([line], itertools.islice(f, n - 1)))

#tokenize all tweets
def tokenize_all_tweets():
    tweets = []
    outf = open('tweets_to_input.json')
    index = 0
    for chunk in lines_per_n(outf, 6):
        d_json = json.loads(chunk)
        tweets.append(d_json['text'])
        index = index+1
        if(index>99):
            break
    outf.close()
    return tweets

# polarity output of tweets with +ve -ve and netural
def results_for_polarity(predict):
    tweets = []
    outf = open('tweets_to_input.json')
    inf = open('twt_classified.json', 'w')
    res = open('res_instances.json','w')
    rec = open('res_classify.json','w')
    index = 0
    pos_instance =     ' \n'
    neg_instance =     ' \n'
    net_instance = ' \n'
    pos_example = 0
    neg_example = 0
    net_example = 0
    for chunk in lines_per_n(outf, 6):
        d_json = json.loads(chunk)
        if(predict[index] == 1):
           d_json['polarity'] = 'POSITIVE'
           pos_example = pos_example + 1
           if pos_example == 1:
               pos_instance = str(d_json)
        if(predict[index] == 0):
           d_json['polarity'] = 'NEUTRAL'
           net_example = net_example+1
           if net_example == 1:
               net_instance = str(d_json)
        if(predict[index] == -1):
           d_json['polarity'] = 'NEGATIVE'
           neg_example = neg_example + 1
           if neg_example == 1:
               neg_instance = str(d_json)

        #print(d_json)
        inf.write(json.dumps(d_json, indent=1))
        inf.write("\n")
        index = index+1
        if(index>99):
            break
    res.write("Pos_Tweet: "+str(pos_example)+"\n"+"Neutral_Tweet: "+str(net_example)+"\n"+"Negative_Tweet: "+str(neg_example)+"\n")
    rec.write("Positive Tweet:\n")
    if pos_example == 0:
        rec.write("Not Found")
    else:
        rec.write(pos_instance)
    rec.write("\nNeutral Tweet:\n")
    if net_example == 0:
        rec.write("Not Found")
    else:
        rec.write(net_instance)
    rec.write("\nNegative Tweet:\n")
    if neg_example == 0:
        rec.write("Not Found")
    else:
        rec.write(neg_instance)
    res.close()
    rec.close()
    outf.close()
    inf.close()
    print("Positive Tweet: ", pos_example)
    print("Negative Tweet: ", neg_example)
    print("Neutral  Tweet: ", net_example)
    print("For detailed report please see twt_classiifed.json file\n");

def fetch_tweets_for_classification():
    f = open('tweets_collect.json')
    inp = open('tweets_to_input.json', 'w')
    #out = open('tweets_classified.json','w')
    index = 0
    for chunk in lines_fetch_per_json(f, 5):
        d_json = json.loads(chunk)
        d_json['polarity'] = "testing"
        inp.write(json.dumps(d_json, indent=1))
        inp.write("\n")
        index = index+1
        if(index>99):
            break
    inp.close()
    f.close()

def main():
    url = urlopen('http://www2.compute.dtu.dk/~faan/data/AFINN.zip')
    zipfile = ZipFile(BytesIO(url.read()))
    afinn_file = zipfile.open('AFINN/AFINN-111.txt')
    tweets = []
    pos_tweets = 0
    net_tweets = 0
    neg_tweets = 0
    fetch_tweets_for_classification()
    predict = np.array([0]*100)
    actual  = np.array([1]*100)
    tweets = tokenize_all_tweets()
    tokens = [tokenize(t) for t in tweets]
    #print(tweets)
    #print(" ")
    #print(tokens)
    index = 0
    afinn = load_affin(afinn_file)
    print(len(tokens))
    for twt  in tokens:
        score = afinn_sentiment_score(twt, afinn)
        if(score > 0):
            predict[index] = 1
            pos_tweets +=1
        elif(score < 0):
            predict[index] = -1
            neg_tweets +=1
        elif score == 0:
            predict[index] = 0
            net_tweets +=1
        index += 1

    
    results_for_polarity(predict)

if __name__ == '__main__':
    main()
