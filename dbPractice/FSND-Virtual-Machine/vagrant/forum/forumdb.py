#
# Database access functions for the web forum.
#

import psycopg2
import time
import bleach

## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    ## Database connection
    DB = psycopg2.connect("dbname=forum")
    c = DB.cursor()
    c.execute("SELECT content, time FROM posts ORDER BY time DESC;")
    rows = c.fetchall()
    posts = []
    for row in rows:
        posts.append({'content': row[0], 'time': row[1]})
    DB.close()
    return posts

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''
    ## Database connection
    DB = psycopg2.connect("dbname=forum")
    c = DB.cursor()
    # t = time.strftime('%c', time.localtime())
    # time gets a default value - now() - set by the DB
    # clean the input to escape html, javascript, etc commands
    c.execute("INSERT INTO posts (content) VALUES (%s)",
              (bleach.clean(content),))
    DB.commit()
    DB.close()
