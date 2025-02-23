#!/usr/bin/env python3
#title           : bskyfollows.py
#description     : Follow a user's followers.
#author          : tellynumner
#date            : 02/22/25
#version         : 1.0
#usage           : ./bskyyourfollows.py
#notes           :
#python_version  : 3.12.3
#==================================================================================================

import argparse
from atproto import Client
import datetime
from my_data import *
import sys
import time

bsky_user = sys.argv[1]
client = Client()
client.login(user, pasw)

def logger(level, message):
    '''Logs a message to a file and prints it to the screen.'''
    now = datetime.datetime.now()
    ts = '[' + now.strftime("%d %b %Y %H:%M:%S") + ']'
    copy = ts + ' ' + level + ' ' + message
    with open('bskyyourfollows.log', 'a') as lf:
        lf.write(copy + '\n')
    print(copy)
    return None

def get_followers():
    '''Collects profile data on the list of accounts following the user.'''
    followers = []
    response = client.get_followers(bsky_user, None, 100)
    followers.extend(response.followers)
    while response.cursor:
        response = client.get_followers(user, response.cursor, 100)
        followers.extend(response.followers)
    return followers

def follow_user(user):
    '''Follows a user'''
    try:
        client.follow(user.did)
        logger('FOLLOWED', 'Followed ' + user.handle + '.')
    except:
        logger('FAILED', 'Failed to follow ' + user.handle + '.' )
    return None

def follow_check(user):
    '''Checks to see if we follow a user.'''
    try:
        logger('INFO', 'Checking to see if we follow ' + user.handle + '.')
        follow = user.viewer['following']
    except:
        logger('FAILED', "We failed get the follow status for " + user.handle + '.')
    if follow is not None:
        logger('INFO', 'We follow ' + user.handle + '.')
        return "FOLLOWING"
    else:
        ('INFO', "We don't follow " + user.handle + '.')
        return None

def last_post_date(user, days_ago):
    """
    Gets the date of the last post of a user. Reports if the last post was more recent than some
    days ago or if it is older.
    """
    days_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_ago)
    try:
        response = client.get_author_feed(user.handle)
    except:
        logger('FAILED', "We failed to scan " + user.handle + " feed! Skipping the last post date check.")
        return 'CURRENT'
    if len(response.feed) > 0:
        try:
            last_post = datetime.datetime.fromisoformat(response.feed[1].post.indexed_at)
        except:
            logger('BOTALERT', user.handle + ' only has 1 post!')
            return 'BOTALERT'
    else:
        logger('BOTALERT', user.handle + ' has never posted!')
        return 'OLD'
    if last_post > days_ago:
        return 'CURRENT'
    else:
        return 'OLD'

def influencer_check(user, ratio):
    """Checks a user's profile for their follower/following count to try to determine their follower
       to follow ratio which determines whether or not they are an influencer.
    """
    profile = client.get_profile(user.did)
    followers = int(profile.followers_count)
    follows = int(profile.follows_count)
    if followers == 0 or follows == 0:
        logger('BOTALERT', user + ' has no follows or followers. Probable bot.')
        return 'BOTALERT'
    follower_ratio = followers / follows
    if follower_ratio >= ratio and followers > 10000:
        logger('INFLUENCER', user.handle + ' is an influencer.')
        return 'INFLUENCER'
    else:
        logger('INFO', user.handle + ' is not an influencer.')
        return 'REGULAR_JOE'
    
def manage_followers(follower_list):
    """
    Takes the follower list and, for each follwer, checks to see if we're following them.
    If not, checks to see if the most recent post date for the account is as recent as some days
    ago, and if so, it follows back.
    """
    for follower in follower_list:
        following = follow_check(follower)
        last_post = last_post_date(follower, 14)
        if following == 'FOLLOWING':
            logger('ALREADYFOLLOW', 'We already follow this person. Moving on.')
        else:
            logger('WEDONTFOLLOW', "We don't follow " + follower.handle + '.')
            if last_post == 'CURRENT':
                logger('INFO', 'Following ' + follower.handle + '.')
                follow_user(follower)
            else:
                logger('INFO', 'Not following ' + follower.handle + '.')
    return None

def main():
    '''Main processing function'''
    logger('INFO', 'Harvesting followers from ' + bsky_user + '.')
    followers = get_followers()
    manage_followers(followers)
    logger('DONE', 'Finished!')

if __name__ == '__main__':
    main()