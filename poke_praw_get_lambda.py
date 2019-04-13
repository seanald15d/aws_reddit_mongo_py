import urllib
import re
import datetime as dt

import praw
import pymongo
from psaw import PushshiftAPI


def save_comm(comment, db_cm):
    # function to insert relvant information from reddit comments into a mongodb database
    # in json form

    date = dt.datetime.fromtimestamp(comment.created_utc) - dt.timedelta(hours=6)
    comm = {
        'post_title': comment.submission.title,
        'post_date': date.strftime('%Y-%m-%d %H:%M:%S'),
        'comment_id': comment.id,
        'comments': comment.body,
        'comment_score': comment.score
    }
    db_cm.insert_one(comm)

def get_date_string(db_cm):
	# function to determine what datestrings to supply to reddit query
	# start datetime from the current date
    end = dt.datetime.now()
    # use regex to get datestring into usable form for reddit query
    new_end = re.findall(r'[\d]+', str(end))
    # for all string numbers returned from previous line, convert to integer
    end_numbers = [int(x) for x in new_end]
    # final "date string" is a time stamp but converted to an integer
    end_epoch = int(
        dt.datetime(end_numbers[0], end_numbers[1], end_numbers[2], 6, 0, 0).timestamp())
    # get the most recent time stamp of data entered into the mongo database
    rar = db_cm.find().sort([('timestamp', -1)]).limit(1)
    # initialize empty list
    item_list = []
    # if we have a most recent entry, try to get the post date
    try:
        for item in rar:
            item_list.append(item['post_date'])
    except KeyError:
        pass
    # Check if we returned a post date from the previous step and then
    # subtract 1 day from the end
    # if we didn't return a date in the previous step, we would just start grabbing data
    # from an initial date
    if len(item_list) > 0:
        start = end - dt.timedelta(days=1)
        new_start = re.findall(r'[\d]+', str(start))

        start_numbers = [int(x) for x in new_start]

        start_epoch = int(
            dt.datetime(start_numbers[0], start_numbers[1], start_numbers[2], 6, 0, 0).timestamp())

    else:
        start_epoch = int(dt.datetime(2001, 1, 1).timestamp())

    return end_epoch, start_epoch

def handler_name(event, context):
	# This is the defined function Lambda reads in
    password = urllib.parse.quote("p@sswordw!thsp&ci@lch@r@ct&rs")
    mng_client = pymongo.MongoClient(
        "mongodb-uri-string" % password)
    mng_db = mng_client['db_name']  # Replace mongo db name
    collection_name = 'collection_name'  # Replace mongo db collection name
    db_cm = mng_db[collection_name]

    # praw is reddit's api wrapper
    reddit = praw.Reddit(client_id='client_id',
                         client_secret='client_secret',
                         user_agent='user_agent',
                         username='username',
                         password='password')

    # now we need to wrap the around praw with Reddit's push shift api wrapper
    api = PushshiftAPI(reddit)

    # run function to get end and start datestrings
    end_epoch, start_epoch = get_date_string(db_cm)

    # query reddit's api for comments
    results = list(api.search_comments(after=start_epoch,
                                          before=end_epoch,
                                          subreddit='subreddit',
                                          filter=['url', 'author', 'title', 'subreddit']))

    # iterate over comments in result and save to database
    for comment in results:
        save_comm(comment, db_cm)