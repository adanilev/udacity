# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import webapp2
import jinja2
import re
import hmac
import random
import string
import hashy
import time

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


def checkSecureCookie(cookieVal):
    '''Confirms it's a valid cookie, returns None if not'''
    #if you got something
    if cookieVal:
        #break it into bits: [val, hash, salt]
        cookieVal = cookieVal.split("|")
        #check it's valid
        if isValidHash(cookieVal[0],cookieVal[1],cookieVal[2]):
            return cookieVal[0]


##############################################################
# Shared Handlers
##############################################################

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def setCookie(self, user_id):
        cookieVal = '%s|%s' % (str(user_id), hashAndSalt(str(user_id)))
        self.response.headers.add_header('Set-Cookie',
                                         'user_id=%s; Path=/' % cookieVal)

    def readCookie(self, cookieName):
        cookie_val = self.request.cookies.get(cookieName)
        return cookie_val and checkSecureCookie(cookie_val)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.readCookie('user_id')
        self.currUser = uid and User.get_by_id(int(uid))


class MainPage(Handler):
    def get(self):
        self.redirect('/blog')


class BlogHandler(Handler):
    """Common Handler for any page that shows a blog post"""
    def get(self):
        self.initBlogErrors()
        #what link was clicked? Ideally would have done this via post but didn't
        #want to mess around with the JavaScript. Should hash at least
        likePost = self.request.get("likePost")
        editPost = self.request.get("editPost")
        deletePost = self.request.get("deletePost")
        deleteComment = self.request.get("deleteComment")


        #what action to handle?
        if likePost:
            if not self.currUser:
                self.redirect('/signup')
                return
            likePost = int(likePost)
            #liking their own post?
            if self.currUser.key().id() == BlogEntry.get_by_id(likePost).authorID:
                self.errors['errorOnPost'] = likePost
                self.errors['likeError'] = "Sorry narcissist, you can't like your own posts"
            else:
                #increment numLikes
                be = BlogEntry.get_by_id(likePost)
                be.numLikes += 1
                be.put()
                time.sleep(0.5)
        elif editPost:
            if not self.currUser:
                self.redirect('/signup')
                return
            editPost = int(editPost)
            if self.currUser.key().id() != BlogEntry.get_by_id(editPost).authorID:
                self.errors['errorOnPost'] = editPost
                self.errors['editError'] = "You can only edit your own posts"
            else:
                self.redirect('/blog/newpost?editPost=' + str(editPost))
        elif deletePost:
            if not self.currUser:
                self.redirect('/signup')
                return
            deletePost = int(deletePost)
            if self.currUser.key().id() != BlogEntry.get_by_id(deletePost).authorID:
                self.errors['errorOnPost'] = deletePost
                self.errors['deleteError'] = "You can only delete your own posts"
            else:
                #TODO: put in a "are you sure" dialogue
                BlogEntry.get_by_id(deletePost).delete()
                time.sleep(1)
        elif deleteComment:
            if not self.currUser:
                #User is not logged in
                self.redirect('/signup')
                return
            else:
                #They are logged in, so check the comment to delete exists
                deleteComment = int(deleteComment)
                expandPost = int(self.request.get("postID"))
                if Comment.get_by_id(deleteComment):
                    #Are they deleting their own comment?
                    if self.currUser.key().id() == Comment.get_by_id(deleteComment).authorID:
                        #Delete the comment and show a success message
                        Comment.get_by_id(deleteComment).delete()
                        time.sleep(1)
                        self.errors['errorOnPost'] = deleteComment
                        self.errors['commentError'] = "Comment deleted!"
                        self.renderBlogPage(expandPost=expandPost)
                    else:
                        #Show error if not their comment
                        self.errors['errorOnPost'] = deleteComment
                        self.errors['commentError'] = "You can only delete your own comments!"
                        self.renderBlogPage(expandPost=expandPost)
                        return
                else:
                    #else the comment doesn't exist, so show an error
                    #TODO should check for the postID too....
                    self.errors['errorOnPost'] = deleteComment
                    self.errors['commentError'] = "Error: that comment doesn't exist!"
                    self.renderBlogPage(expandPost=expandPost)
                    return


        #finally, render the page
        self.renderBlogPage()

    def post(self):
        #if here, someone added a comment
        self.initBlogErrors()
        expandPost = int(self.request.get("postID"))
        if self.currUser:
            # check they entered something
            if self.request.get("comment"):
                self.addComment()
            else:
                self.errors['errorOnPost'] = int(self.request.get("postID"))
                self.errors['commentError'] = "Please enter a comment"
        else:
            self.errors['errorOnPost'] = int(self.request.get("postID"))
            self.errors['commentError'] = "Please login to add a comment"
        self.renderBlogPage(expandPost=expandPost)

    def renderBlogPage(self, posts='', expandPost=''):
        """Convenience method to render any page showing a blog entry"""
        if not posts:
            posts = self.getPosts()
        self.render("blog_posts.html", posts=posts, expandPost=expandPost,
                                       currUser=self.currUser, Comment=Comment,
                                       User=User, errors=self.errors)

    def addComment(self):
        comment = self.request.get("comment")
        postID = int(self.request.get("postID"))
        authorID = int(self.currUser.key().id())
        Comment.addComment(comment, postID, authorID)
        #TODO: find a more elegant way to deal with this instead of sleeping.
        #The latest comment was not being returned immediately when reloading
        time.sleep(1)

    def getPosts(self):
        postObjs = BlogEntry.all().order('-created')
        posts = []
        for post in postObjs:
            posts.append(post)
        return posts

    def initBlogErrors(self):
        """Avoid errors (pun intended) by creating an array now and setting all
        possible errors to blank"""
        self.errors = {}
        self.errors['errorOnPost'] = ''
        self.errors['commentError'] = ''
        self.errors['likeError'] = ''
        self.errors['editError'] = ''
        self.errors['deleteError'] = ''


##############################################################
# Handlers
##############################################################


class BlogNewPostHandler(BlogHandler):
    def get(self):
        if not self.currUser:
            self.redirect('/signup')
        else:
            newPostArgs = {'subject': '', 'content': '', 'error': ''}
            editPost = self.request.get("editPost")
            if editPost:
                #if wanting to edit the post
                editPost = int(editPost)
                #double check identity
                if self.currUser.key().id() == BlogEntry.get_by_id(editPost).authorID:
                    newPostArgs['subject'] = BlogEntry.get_by_id(editPost).subject
                    newPostArgs['content'] = BlogEntry.get_by_id(editPost).content
                else:
                    newPostArgs['error'] = "You can only edit your own posts"

            self.render("new_post.html", newPostArgs=newPostArgs, currUser=self.currUser)

    def post(self):
        #Are they logged in?
        if not self.currUser:
            self.redirect('/signup')
        else:
            #Get data the user input
            newPostArgs = {}
            newPostArgs['subject'] = self.request.get("subject")
            newPostArgs['content'] = self.request.get("content")
            newPostArgs['error'] = ''
            #If it's a valid post
            if newPostArgs['subject'] and newPostArgs['content']:
                #is it an update?
                if self.request.get("editPost"):
                    be = BlogEntry.get_by_id(int(self.request.get("editPost")))
                    be.subject = newPostArgs['subject']
                    be.content = newPostArgs['content']
                else:
                    #else create a new entry
                    be = BlogEntry(subject=newPostArgs['subject'],
                                   content=newPostArgs['content'],
                                   authorID = self.currUser.key().id())
                be.put()
                #And then redirect to the single post page
                self.redirect('/blog/' + str(be.key().id()))
                self.render("new_post.html", newPostArgs=newPostArgs, currUser=self.currUser)
            else:
                newPostArgs['error'] = "Please complete both fields to post!"
                self.render("new_post.html", newPostArgs=newPostArgs, currUser=self.currUser)


class BlogEntryHandler(BlogHandler):
    def get(self, entry_id):
        self.initBlogErrors()
        post = BlogEntry.get_by_id(int(entry_id))
        if post:
            self.renderBlogPage([post])
        else:
            self.error(404)

class SignupHandler(Handler):
    def get(self):
        self.render("signup.html", currUser=self.currUser)

    def post(self):
        values = ({"username": self.request.get("username"),
                   "usernameError": "",
                   "password": self.request.get("password"),
                   "passwordError": "",
                   "verify": self.request.get("verify"),
                   "verifyError": "",
                   "email": self.request.get("email"),
                   "emailError": "",
                   "success": ""})

        values = verifySignupInput(values)

        if values["success"]:
            user_id = createUser(values)
            self.setCookie(user_id)
            self.redirect("/welcome")
        else:
            #blank the passwords and let them try again
            values["password"] = ""
            values["verify"] = ""
            self.render("signup.html", **values)


class WelcomeHandler(BlogHandler):
    def get(self):
        if self.currUser:
            username = self.currUser.username
            self.render("welcome.html",username=username, currUser=self.currUser)
        else:
            self.redirect('/signup')

class EditCommentHandler(BlogHandler):
    def get(self):
        if self.currUser:
            commentID = self.request.get("commentID")
            if commentID:
                commentID = int(commentID)
                if self.currUser.key().id() == Comment.get_by_id(commentID).authorID:
                    #get the comment
                    commentText = Comment.get_by_id(commentID).commentText
                    editCommentError = ''
                    self.render("editcomment.html", commentText=commentText, editCommentError=editCommentError)
                else:
                    commentText = ''
                    editCommentError = 'Whoa there, Nelly! You can only edit your own comments.'
                    self.render("editcomment.html", commentText=commentText, editCommentError=editCommentError)
        else:
            self.redirect('/signup')

    def post(self):
        if self.currUser:
            commentID = self.request.get("commentID")
            if commentID:
                commentID = int(commentID)
                if self.currUser.key().id() == Comment.get_by_id(commentID).authorID:
                    commentText = self.request.get("commentText")
                    if commentText:
                        c = Comment.get_by_id(commentID)
                        c.commentText = commentText
                        c.put();
                        time.sleep(1)
                        self.redirect('/blog')
                    else:
                        commentText = Comment.get_by_id(commentID).commentText
                        editCommentError = 'Please enter a comment to update.'
                        self.render("editcomment.html", commentText=commentText, editCommentError=editCommentError)
                else:
                    commentText = ''
                    editCommentError = 'Whoa there, Nelly! You can only edit your own comments.'
                    self.render("editcomment.html", commentText=commentText, editCommentError=editCommentError)
        else:
            self.redirect('/signup')


class LoginHandler(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        #Get the details from the form.
        values = ({"username": self.request.get("username"),
                   "password": self.request.get("password"),
                   "loginError": ""})

        #Set cookie and redirect if login details are correct.
        if validateLogin(values):
            user_id = getUserID(values["username"])
            self.setCookie(user_id)
            self.redirect("/blog")
        else:
            self.render("login.html", **values)


class LogoutHandler(Handler):
    def get(self):
        #set user_id cookie to ''
        self.response.headers.add_header('Set-Cookie','user_id=''; Path=/')
        #and redirect
        self.redirect("/signup")




##############################################################
# Blog and Comment Models
##############################################################

#this defines the DataStore Model. ~an object that can be added to the DataStore
class BlogEntry(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    numLikes = db.IntegerProperty(default = 0)
    authorID = db.IntegerProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    modified = db.DateTimeProperty(auto_now = True)

#define comments
class Comment(db.Model):
    commentText = db.TextProperty(required = True)
    postID = db.IntegerProperty(required = True)
    authorID = db.IntegerProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

    @classmethod
    def addComment(cls, commentText, postID, authorID):
        newComment = Comment(commentText=commentText, postID=postID,
                             authorID=authorID)
        newComment.put()



##############################################################
# User and login things
##############################################################

#regexs
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.TextProperty(required = True)
    email = db.StringProperty(required = False)
    joined = db.DateTimeProperty(auto_now_add = True)


def createSalt():
    letters = string.ascii_letters
    result = ""
    for i in range(5):
        result += letters[random.randint(0,51)]
    return result


def hashAndSalt(sometext, salt=''):
    """Inputs: sometext = text to hash. salt = defaults to something random
       Outputs: hashedString|salt
       """
    if not salt:
        salt = createSalt()
    h = hmac.new(hashy.getHashKey(), '%s%s' % (sometext, salt)).hexdigest()
    return '%s|%s' % (h, salt)


def isValidHash(value,hashed,salt):
    rehash = hashAndSalt(value,salt)
    if rehash.split("|")[0] == hashed:
        return True
    else:
        return False


def createUser(values):
    new_usr = User(username = values["username"],
                   password = hashAndSalt(values["password"]))
    new_usr.put()
    return new_usr.key().id()


def getUserID(username):
    """return the user_id belonging to username, if not there, return None"""
    theuser = db.Query(User).filter("username =",username).get()
    if theuser:
        return theuser.key().id()
    else:
        return False


def validateLogin(values):
    #does the username exist?
    if getUserID(values["username"]):
        #check the password
        db_pw = db.Query(User).filter("username =",values["username"]).get().password
        if hashAndSalt(values["password"],db_pw.split("|")[1]) == db_pw:
            return True
    #if here, username or password didn't match
    values["loginError"] = "Invalid login details"
    return False


def verifySignupInput(values):
    #innocent until proven guilty
    values["success"] = True

    #does the username exist already?
    if getUserID(values["username"]):
        values["usernameError"] = "Sorry, that username is already taken"
        values["success"] = False

    #verify username
    if USER_RE.match(values["username"]) == None:
        values["usernameError"] = "Invalid username"
        values["success"] = False

    #test the email
    if values["email"]:
        if EMAIL_RE.match(values["email"]) == None:
            values["emailError"] = "Invalid email"
            values["success"] = False

    #test the password conforms
    if PASSWORD_RE.match(values["password"]) == None:
        values["passwordError"] = "Invalid password"
        values["success"] = False
    #and match
    if values["password"] != values["verify"]:
        values["verifyError"] = "Passwords don't match"
        values["success"] = False

    return values



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/signup', SignupHandler),
    ('/welcome', WelcomeHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/editcomment', EditCommentHandler),
    ('/blog', BlogHandler),
    ('/blog/newpost', BlogNewPostHandler),
    ('/blog/(\d+)', BlogEntryHandler)],
    debug=True)
