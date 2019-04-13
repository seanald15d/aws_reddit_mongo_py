# aws_reddit_mongo_py
A script designed to run as an AWS Lambda function on a schedule to continuously update a MongoDB database with reddit comments.

The script begins by taking in AWS Lambda's "event" and "context" arguments in the "handler_name" function (line 63).

Then it connects to a MongoDB database with a mongo uri string and a user password. **Important: This script implements MongoDB Atlas, a cloud database (the free tier) and requires registration. You can host locally, but you'll need to determine how much space you actually need.

After connecting to Mongo, the script then implements python's praw (python-reddit-api-wrapper) with appropriate credentials and then reddit's Push Shift API wrapper.

Dates to query comments are then discerned based on whether or not entries exist in a database already. **If data does not exist, the script will start running from when the subreddit you want to query had its first comment. If planning to implement AWS, I would first run the script on your local machine to get caught up to date on all comments until the current day (otherwise, you could see a large AWS bill...). Then, you should be good to run it on AWS, as the script will only be getting a day's worth of comments from that point on.

Finally, results are queried using date-time and subreddit information and then collected and stored as json objects in Mongo.
