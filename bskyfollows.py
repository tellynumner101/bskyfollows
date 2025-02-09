#!/usr/bin/env python3
#title           :bskyfollows.py
#description     : Automated follows management
#author          :tellynumner
#date            :02/08/25
#version         :0.5
#usage           :./bskyfollows.py
#notes           :
#python_version  :3.12.3
#=============================================================================

from atproto import Client
import datetime
from my_data import *
import time

client = Client()
client.login(user, pasw)

def logger(level, message):
    '''Logs a message to a file and prints it to the screen.'''
    now = datetime.datetime.now()
    ts = '[' + now.strftime("%d %b %Y %H:%M:%S") + ']'
    copy = ts + ' ' + level + ' ' + message
    with open('bskyfollows.log', 'a') as lf:
        lf.write(copy + '\n')
    print(copy)
    return None

def get_followers():
    '''Collects profile data on the list of accounts following us.'''
    followers = []
    response = client.get_followers(user, None, 100)
    followers.extend(response.followers)
    while response.cursor:
        response = client.get_followers(user, response.cursor, 100)
        followers.extend(response.followers)
    return followers

def get_follows():
    '''Collects profile data on the list of accounts we follow.'''
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
    for follower in follower_list:
        if follower.viewer['following'] == None:
            count += 1
            logger('INFO', "Following " + follower.handle + " back.")
            client.follow(follower.did)
            time.sleep(0.5)
    logger('INFO', "I followed back " + str(count) + " accounts!")
    return None

def last_post_date(user):
    """
    Gets the date of the last post of a user. Reports if the last post was more recent than 15
    days ago.
    """
    fifteen_days_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=15)
    last_post = ''
    try:
        response = client.get_author_feed(user.handle)
    except:
        last_post = datetime.datetime.fromisoformat('2001-01-01 01:01:01.858000+00:00')
    if last_post == '':
        if len(response.feed) > 0:
            try:
                last_post = datetime.datetime.fromisoformat(response.feed[1].post.indexed_at)
            except:
                last_post = datetime.datetime.fromisoformat('2001-01-01 01:01:02.858000+00:00')
        else:
            last_post = datetime.datetime.fromisoformat('2001-01-01 01:01:03.858000+00:00')
    if last_post > fifteen_days_ago:
        return 'current'
    else:
        return 'older than 15 days'

def manage_follows(follows_list):
    '''
    Unfollows the accounts we follow based on whether or not they follow us, their follower ratio, 
    and the last time they posted. IF an account has not posted in 15 days, whether or not they 
    follow us, they are deleted. IF an account does not follow us AND IF their follower ratio is 
    not better than 1, they are deleted. 
    '''
    for follow in follows_list:
        flag = 'n'
        last_post = last_post_date(follow)
        profile = client.get_profile(follow.did)
        followers = int(profile.followers_count)
        follows = int(profile.follows_count)
        if followers != 0 and follows != 0:
            follower_ratio = followers / follows
        else:
            follower_ratio = .5
        logger('INFO', 'Scrutinizing following relationship: ' + follow.handle + '...')
        logger('INFO', 'Checking to see if ' + follow.handle + ' has posted recently...')
        logger('INFO', 'Post history is ' + last_post + '.')
        if last_post != 'current':
            logger('DELETEFOLLOW', follow.handle + " hasn't posted in the last 15 or more days.")
            flag = 'y'
        logger('INFO', 'Checking to see if ' + follow.handle + ' follows us...')
        if follow.viewer['followed_by'] == None:
            logger('INFO', follow.handle + " doesn't follow us. Let's check if they're an influencer.")
            if follower_ratio > 1:
                logger('INFO', follow.handle + ' is an influencer.')
                flag = 'n'
            else:
                logger('DELETEFOLLOW', follow.handle + " isn't an influencer.")
                flag = 'y'
        else:
            logger('INFO', follow.handle + ' follows us.')
        if flag == 'n':
            logger('INFO', 'Preserving following relationship with ' + follow.handle + '.')
        else:
            client.delete_follow(follow.viewer['following'])
            logger('FOLLOWDELETED', follow.handle + ' unfollowed.')
    return None

def main():
    '''Main processing function'''
    logger('INFO', 'Beginning follower management for ' + user + '.')
    logger('INFO', 'Processing followers list...')
    followers = get_followers()
    follow_back(followers)
    logger('INFO', 'Processing following list...')
    following = get_follows()
    manage_follows(following)
    logger('DONE', 'Finished!')

if __name__ == '__main__':
    main()