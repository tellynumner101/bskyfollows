#!/usr/bin/env python3
#title           :bskyfollows.py
#description     :This will follow anyone who's following you that you haven't
#                 followed back. It will also unfollow anyone who you've
#                 followed but who hasn't followed you back.
#author          :tellynumner
#date            :01/31/25
#version         :0.3
#usage           :./bskyfollows.py
#notes           :
#python_version  :3.12.3
#=============================================================================

from atproto import Client
from my_data import *

client = Client()
client.login(user, pasw)

def get_followers():
    '''Collects profile data on the list of accounts following you'''
    followers = []
    response = client.get_followers(user, None, 100)
    followers.extend(response.followers)
    while response.cursor:
        response = client.get_followers(user, response.cursor, 100)
        followers.extend(response.followers)
    return followers

def get_following():
    '''Collects profile data on the list of accounts you follow'''
    follows = []
    response = client.get_follows(user, None, 100)
    follows.extend(response.follows)
    while response.cursor:
        response = client.get_follows(user, response.cursor, 100)
        follows.extend(response.follows)
    return follows

def follow_back(follower_list):
    '''Follows back any account following us'''
    count = 0
    for i in follower_list:
        if i.viewer['following'] == None:
            count += 1
            print("Following " + i.handle + " back.")
            client.follow(i.did)
    if count != 0:
        print("I followed back " + str(count) + " accounts!")
    return None

def unfollow(follows_list):
    '''Unfollows any account not following us'''
    count = 0
    for i in follows_list:
        if i.viewer['followed_by'] == None:
            count += 1
            print(i.handle + " hasn't followed me back.")
            if i.viewer['following'] is not None:
                client.delete_follow(i.viewer['following'])
                print("Unfollowed " + i.handle + "!")
            else:
                print(i.handle + " doesn't have a following link! Manually remove!")
    if count != 0:
        print("I unfollowed " + str(count) + " accounts!")
    return None

def main():
    '''Main processing function'''
    print('Processing followers...')
    followers = get_followers()
    follow_back(followers)
    print('')
    print('Processing follows...')
    following = get_following()
    unfollow(following)
    print('')
    print('All done!')

if __name__ == '__main__':
    main()