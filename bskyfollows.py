#!/usr/bin/env python3
#title           :bskyfollows.py
#description     :This will follow anyone who's following you that you haven't
#                 followed back. It will also unfollow anyone who you've
#                 followed but who hasn't followed you back.
#author          :tellynumner
#date            :01/24/25
#version         :0.2
#usage           :./bskyfollows.py
#notes           :
#python_version  :3.12.3
#=============================================================================

import ast
from atproto import Client
import time
from my_data import user, pasw

client = Client()
client.login(user, pasw)

def getFollowers():
    followers = []
    cursor = None
    while True:
        params = {'actor': user, 'limit': 100}
        if cursor:
            params['cursor'] = cursor
        response = client.app.bsky.graph.get_followers(params)
        followers.extend([follower.model_dump() for follower in response.followers])
        if not response.cursor:
            break
        cursor = response.cursor
        time.sleep(0.5)
    return followers

def getFollows():
    follows = []
    cursor = None
    while True:
        params = {'actor': user, 'limit': 100}
        if cursor:
            params['cursor'] = cursor
        response = client.app.bsky.graph.get_follows(params)
        follows.extend([follow.model_dump() for follow in response.follows])
        if not response.cursor:
            break
        cursor = response.cursor
        time.sleep(0.5)
    return follows

def fixDict(getfol_list):
    new_list = []
    for item in getfol_list:
        temp_dict = {}
        item = str(item)
        this_dict = ast.literal_eval(item)
        temp_dict['did'] = this_dict.get('did', None)
        temp_dict['handle'] = this_dict.get('handle', None)
        viewer = this_dict.get('viewer', None)
        temp_dict['following'] = viewer.get('following', None)
        temp_dict['followed_by'] = viewer.get('followed_by', None)
        new_list.append(temp_dict)
    return new_list

def followBack(follower_list):
    for i in follower_list:
        if i['following'] == None:
            print("Following " + i['handle'] + " back.")
            client.follow(i['did'])
    print("I followed everyone back!")

def unfollow(follows_list):
    for i in follows_list:
        if i['followed_by'] == None:
            print(i['handle'] + " doesn't follow me back.")
            if i['following'] is not None:
                client.delete_follow(i['following'])
                print("Unfollowed " + i['handle'] + "!")
    print("I unfollowed everyone!")

def main():
    followers = fixDict(getFollowers())
    followBack(followers)
    follows = fixDict(getFollows())
    unfollow(follows)

if __name__ == '__main__':
    main()
