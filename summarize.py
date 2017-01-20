from itertools import islice, chain
import itertools
import json



out1 = "Number of users collected: "
out2 = "Number of messages collected: "
out3 = "Number of communities discovered: "
out4 = "Average number of users per community: "
out5 = "Number of instances per class found:(out of total 100) "
out6 = "One example from each class: "

final_output =''
def lines_fetch_per_json(fil, n):
    for line in fil:
        yield ''.join(chain([line], itertools.islice(fil, n - 1)))


def tweet_and_user_count(final_output):
    f = open('tweets_collect.json')
    unique_user ={}
    tweet_cnt = 0
    for chunk in lines_fetch_per_json(f, 5):
        d_json = json.loads(chunk)
        uid = d_json['id']
        tweet_cnt = tweet_cnt + 1
        if uid not in unique_user:
            unique_user[uid] = 1
    final_output=final_output + out1 + str(len(unique_user)) + "\n" + out2 + str(tweet_cnt)+"\n"
    f.close()
    return final_output


def community_data(final_output):
    f = open('inetrmediate.json')
    line = f.readlines()
    d = []
    i = 0
    for l in line:
        d.append(l)
        i = i+1
    final_output = final_output + out3+"\n"+d[0]+"\n"
    final_output = final_output + out4+"\n"+d[1]+"\n"
    return final_output

def classify_tweet(final_output):
    f = open('res_classify.json')
    fp= open('res_instances.json')
    s = open('summary.txt', 'w')
    data = ''

    line = f.readlines()
    for l in line:
        data = data + l
    final_output = final_output + out6 +"\n"+data+"\n"
    data = ''
    line = fp.readlines()
    for l in line:
        data = data + l
    final_output = final_output + out5+"\n"+data+"\n"
    s.write(final_output)
    f.close()
    fp.close()
    s.close()
    return final_output
               
final_output = tweet_and_user_count(final_output)
final_output = community_data(final_output)
final_output = classify_tweet(final_output)
print(final_output)
print("Report Has been dumped in summary.txt file too")
