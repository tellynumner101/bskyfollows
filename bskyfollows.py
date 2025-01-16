#!/usr/bin/env python3
#title           :bskyfollows.py
#description     :This will follow anyone who's following you that you haven't
#                 followed back. 
#author          :tellynumner
#date            :01/15/25
#version         :0.1
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

def fixFollowers(getfol_list):
    new_list = []
    for item in getfol_list:
        temp_dict = {}
        item = str(item)
        this_dict = ast.literal_eval(item)
        temp_dict['did'] = this_dict.get('did', None)
        temp_dict['handle'] = this_dict.get('handle', None)
        viewer = this_dict.get('viewer', None)
        temp_dict['following'] = viewer.get('following', None)
        new_list.append(temp_dict)
    return new_list

def followBack(follower_list):
    for i in follower_list:
        if i['following'] == None:
            print("Following " + i['handle'] + " back.")
            client.follow(i['did'])
    print("I followed everyone back!")

def main():
    followers = fixFollowers(getFollowers())
    followBack(followers)

if __name__ == '__main__':
    main()
