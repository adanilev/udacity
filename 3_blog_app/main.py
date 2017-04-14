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
from functools import wraps

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


##############################################################
# Decorators
##############################################################
def check_post_exists(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if BlogEntry.get_by_id(int(kwargs['post_id']), parent=fancy_blog):
            return fn(self, *args, **kwargs)
        else:
            return self.handle_404()
    return wrapper


def user_logged_in(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if self.currUser:
            return fn(self, *args, **kwargs)
        else:
            return self.redirect('/signup')
    return wrapper


##############################################################
# Global function
##############################################################
def check_secure_cookie(cookie_val):
    """Confirms it's a valid cookie, returns None if not"""
    # If you got something
    if cookie_val:
        # Break it into bits: [val, hash, salt]
        cookie_val = cookie_val.split("|")
        # Then check it's valid
        if is_valid_hash(cookie_val[0], cookie_val[1], cookie_val[2]):
            return cookie_val[0]


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

    def set_cookie(self, user_id):
        cookie_val = '%s|%s' % (str(user_id), hash_and_salt(str(user_id)))
        self.response.headers.add_header('Set-Cookie',
                                         'user_id=%s; Path=/' % cookie_val)

    def read_cookie(self, cookie_name):
        cookie_val = self.request.cookies.get(cookie_name)
        return cookie_val and check_secure_cookie(cookie_val)

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_cookie('user_id')
        self.currUser = uid and User.get_by_id(int(uid))

    def handle_404(self):
        self.response.set_status(404)
        self.response.write('Error 404: Page not found.')


class MainPage(Handler):
    def get(self):
        self.redirect('/blog')


class BlogHandler(Handler):
    """This class has common functions used by other handlers that deal with
    blog entries. It also handles comment functionality.
    """
    errs = {}

    def __init__(self, *args, **kwargs):
        self.errors = {}
        super(BlogHandler, self).__init__(*args, **kwargs)

    """Deal with comments"""
    def get(self):
        self.init_blog_errors()
        # What link was clicked? Ideally would have done this via post but
        # didn't want to mess around with the JavaScript. Should hash at least
        delete_comment = self.request.get("delete_comment")

        # what action to handle?
        if delete_comment:
            if not self.currUser:
                # User is not logged in
                self.redirect('/signup')
                return
            else:
                # They are logged in, so check the comment to delete exists
                delete_comment = int(delete_comment)
                expand_post = int(self.request.get("post_id"))
                if Comment.get_by_id(delete_comment):
                    # Are they deleting their own comment?
                    if self.currUser.key().id() == \
                            Comment.get_by_id(delete_comment).author_id:
                        # Delete the comment and show a success message
                        Comment.get_by_id(delete_comment).delete()
                        self.errs['error_on_post'] = delete_comment
                        time.sleep(1)
                        self.errs['comment_error'] = "Comment deleted!"
                        self.render_blog_page(expand_post=expand_post)
                    else:
                        # Show error if not their comment
                        self.errs['error_on_post'] = delete_comment
                        self.errs['comment_error'] = "You can only delete" \
                                                     " your own comments!"
                        self.render_blog_page(expand_post=expand_post)
                        return
                else:
                    # else the comment doesn't exist, so show an error
                    # TODO should check for the post_id too....
                    self.errs['error_on_post'] = delete_comment
                    self.errs['comment_error'] = "Error: that comment" \
                                                 "doesn't exist!"
                    self.render_blog_page(expand_post=expand_post)
                    return

        show_comments = self.request.get("showComments")
        if show_comments:
            self.render_blog_page(expand_post=int(show_comments))
        else:
            self.render_blog_page()



    def render_blog_page(self, posts='', expand_post=0):
        """Convenience method to render any page showing a blog entry"""
        if not posts:
            posts = self.get_posts()

        self.render("blog_posts.html",
                    posts=posts, expand_post=expand_post,
                    currUser=self.currUser, Comment=Comment, User=User,
                    Like=Like, errors=self.errs)
        self.errs.clear()

    def get_posts(self):
        post_objs = BlogEntry.all().ancestor(fancy_blog).order('-created')
        posts = []
        for post in post_objs:
            posts.append(post)
        return posts

    def init_blog_errors(self):
        """Initialise error message list"""
        self.errors = {}
        self.errors['error_on_post'] = ''
        self.errors['comment_error'] = ''
        self.errors['like_error'] = ''
        self.errors['edit_error'] = ''
        self.errors['delete_error'] = ''

    def user_owns_post(self, blog_entry):
        """Assumes post exists. Returns true if currUser owns blog_entry"""
        if blog_entry.author_id == self.currUser.key().id():
            return True
        else:
            return False


##############################################################
# Handlers
##############################################################


class BlogNewPostHandler(BlogHandler):
    def get(self):
        if not self.currUser:
            self.redirect('/signup')
        else:
            new_post_args = {'subject': '', 'content': '', 'error': ''}
            edit_post = self.request.get("edit_post")
            if edit_post:
                # if wanting to edit the post
                edit_post = int(edit_post)
                # double check identity
                if self.currUser.key().id() == \
                        BlogEntry.get_by_id(
                            edit_post, parent=fancy_blog).author_id:
                    new_post_args['subject'] = BlogEntry.\
                        get_by_id(edit_post, parent=fancy_blog).subject
                    new_post_args['content'] = BlogEntry.\
                        get_by_id(edit_post, parent=fancy_blog).content
                else:
                    new_post_args['error'] = "You can only edit your own posts"

            self.render("new_post.html", new_post_args=new_post_args,
                        currUser=self.currUser)

    def post(self):
        # Are they logged in?
        if not self.currUser:
            self.redirect('/signup')
        else:
            # Get data the user input
            new_post_args = {}
            new_post_args['subject'] = self.request.get("subject")
            new_post_args['content'] = self.request.get("content")
            new_post_args['error'] = ''
            # If it's a valid post
            if new_post_args['subject'] and new_post_args['content']:
                # is it an update?
                if self.request.get("edit_post"):
                    be = BlogEntry.get_by_id(
                        int(self.request.get("edit_post")), parent=fancy_blog)
                    be.subject = new_post_args['subject']
                    be.content = new_post_args['content']
                else:
                    # else create a new entry
                    be = BlogEntry(parent=fancy_blog,
                                   subject=new_post_args['subject'],
                                   content=new_post_args['content'],
                                   author_id=self.currUser.key().id())
                be.put()
                # And then redirect to the single post page
                self.redirect('/blog/' + str(be.key().id()))
                self.render("new_post.html", new_post_args=new_post_args,
                            currUser=self.currUser)
            else:
                new_post_args['error'] = "Please complete both fields to post!"
                self.render("new_post.html", new_post_args=new_post_args,
                            currUser=self.currUser)


class BlogEntryHandler(BlogHandler):
    def get(self, entry_id):
        self.init_blog_errors()
        post = BlogEntry.get_by_id(int(entry_id), parent=fancy_blog)
        if post:
            self.render_blog_page([post])
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

        values = verify_signup_input(values)

        if values["success"]:
            user_id = create_user(values)
            self.set_cookie(user_id)
            self.redirect("/welcome")
        else:
            # blank the passwords and let them try again
            values["password"] = ""
            values["verify"] = ""
            self.render("signup.html", **values)


class WelcomeHandler(BlogHandler):
    def get(self):
        if self.currUser:
            username = self.currUser.username
            self.render("welcome.html", username=username,
                        currUser=self.currUser)
        else:
            self.redirect('/signup')


class AddCommentHandler(BlogHandler):
    @check_post_exists
    @user_logged_in
    def post(self, **kwargs):
        blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                         parent=fancy_blog)

        if self.request.get("comment"):
            comment_text = self.request.get("comment")
            new_comment = Comment(parent=blog_entry, comment_text=comment_text,
                                  author=self.currUser)
            new_comment.put()
        else:
            self.errs['error_on_post'] = int(self.request.get("post_id"))
            self.errs['comment_error'] = "Please enter a comment"

        self.redirect('/blog?showComments=' + kwargs['post_id'] +
                      '#post-' + kwargs['post_id'])


class EditCommentHandler(BlogHandler):
    def get(self):
        if self.currUser:
            comment_id = self.request.get("comment_id")
            if comment_id:
                comment_id = int(comment_id)
                if self.currUser.key().id() == Comment.\
                        get_by_id(comment_id).author_id:
                    # get the comment
                    comment_text = Comment.get_by_id(comment_id).comment_text
                    edit_comment_error = ''
                    self.render("editcomment.html", comment_text=comment_text,
                                edit_comment_error=edit_comment_error)
                else:
                    comment_text = ''
                    edit_comment_error = 'Whoa there, Nelly! You can only ' \
                                         'edit your own comments.'
                    self.render("editcomment.html", comment_text=comment_text,
                                edit_comment_error=edit_comment_error)
        else:
            self.redirect('/signup')

    def post(self):
        if self.currUser:
            comment_id = self.request.get("comment_id")
            if comment_id:
                comment_id = int(comment_id)
                if self.currUser.key().id() == Comment.\
                        get_by_id(comment_id).author_id:
                    comment_text = self.request.get("comment_text")
                    if comment_text:
                        c = Comment.get_by_id(comment_id)
                        c.comment_text = comment_text
                        c.put()
                        time.sleep(1)
                        self.redirect('/blog')
                    else:
                        comment_text = Comment.get_by_id(
                            comment_id).comment_text
                        edit_comment_error = 'Please enter a comment ' \
                                             'to update.'
                        self.render("editcomment.html",
                                    comment_text=comment_text,
                                    edit_comment_error=edit_comment_error)
                else:
                    comment_text = ''
                    edit_comment_error = 'Whoa there, Nelly! You can only ' \
                                         'edit your own comments.'
                    self.render("editcomment.html", comment_text=comment_text,
                                edit_comment_error=edit_comment_error)
        else:
            self.redirect('/signup')


class LoginHandler(Handler):
    def get(self):
        self.render("login.html")

    def post(self):
        # Get the details from the form.
        values = ({"username": self.request.get("username"),
                   "password": self.request.get("password"),
                   "loginError": ""})

        # Set cookie and redirect if login details are correct.
        if validate_login(values):
            user_id = get_user_id(values["username"])
            self.set_cookie(user_id)
            self.redirect("/blog")
        else:
            self.render("login.html", **values)


class LogoutHandler(Handler):
    def get(self):
        # set user_id cookie to ''
        self.response.headers.add_header('Set-Cookie', 'user_id=''; Path=/')
        # and redirect
        self.redirect("/signup")


class LikeHandler(BlogHandler):
    @check_post_exists
    @user_logged_in
    def get(self, **kwargs):
        blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                         parent=fancy_blog)
        liked_by = User.get_by_id(self.currUser.key().id())
        like = db.Query(Like).ancestor(blog_entry.key())\
            .filter("liked_by =", liked_by)\
            .get()

        # Show error if they are trying to like their own post
        if self.user_owns_post(blog_entry):
            BlogHandler.errs['error_on_post'] = int(kwargs['post_id'])
            BlogHandler.errs['like_error'] = 'Sorry, you can''t like your ' \
                                             'own posts. Narcissist.'
            return self.redirect("/blog#post-" + kwargs['post_id'])

        # Like it if they haven't liked before
        if like is None:
            like = Like(parent=blog_entry, liked_by=liked_by)
            like.put()
        # Unlike if they did like before
        else:
            like.delete()

        self.redirect("/blog#post-" + kwargs['post_id'])


class EditPostHandler(BlogHandler):
    @check_post_exists
    @user_logged_in
    def get(self, **kwargs):
        blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                         parent=fancy_blog)
        if self.user_owns_post(blog_entry):
            self.redirect('/blog/newpost?editPost=' + kwargs['post_id'])
        else:
            BlogHandler.errs['error_on_post'] = int(kwargs['post_id'])
            BlogHandler.errs['edit_error'] = 'You can only edit your own posts'
            return self.redirect('/blog')


class DeletePostHandler(BlogHandler):
    @check_post_exists
    @user_logged_in
    def get(self, **kwargs):
        blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                         parent=fancy_blog)
        if self.user_owns_post(blog_entry):
            blog_entry.delete()
            return self.redirect('/blog')
        else:
            BlogHandler.errs['error_on_post'] = int(kwargs['post_id'])
            BlogHandler.errs['delete_error'] = 'You can only delete your '\
                                               'own posts'
            return self.redirect('/blog')


##############################################################
# User and login things
##############################################################

# regexs
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")


class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.TextProperty(required=True)
    email = db.StringProperty(required=False)
    joined = db.DateTimeProperty(auto_now_add=True)


def create_salt():
    letters = string.ascii_letters
    result = ""
    for i in range(5):
        result += letters[random.randint(0, 51)]
    return result


def hash_and_salt(sometext, salt=''):
    """Inputs: sometext = text to hash. salt = defaults to something random
       Outputs: hashedString|salt
       """
    if not salt:
        salt = create_salt()
    h = hmac.new(hashy.getHashKey(), '%s%s' % (sometext, salt)).hexdigest()
    return '%s|%s' % (h, salt)


def is_valid_hash(value, hashed, salt):
    rehash = hash_and_salt(value, salt)
    if rehash.split("|")[0] == hashed:
        return True
    else:
        return False


def create_user(values):
    new_usr = User(username=values["username"],
                   password=hash_and_salt(values["password"]))
    new_usr.put()
    return new_usr.key().id()


def get_user_id(username):
    """return the user_id belonging to username, if not there, return None"""
    theuser = db.Query(User).filter("username =", username).get()
    if theuser:
        return theuser.key().id()
    else:
        return False


def validate_login(values):
    # does the username exist?
    if get_user_id(values["username"]):
        # check the password
        db_pw = db.Query(User).filter("username =",
                                      values["username"]).get().password
        if hash_and_salt(values["password"], db_pw.split("|")[1]) == db_pw:
            return True
    # if here, username or password didn't match
    values["loginError"] = "Invalid login details"
    return False


def verify_signup_input(values):
    # innocent until proven guilty
    values["success"] = True

    # does the username exist already?
    if get_user_id(values["username"]):
        values["usernameError"] = "Sorry, that username is already taken"
        values["success"] = False

    # verify username
    if USER_RE.match(values["username"]) is None:
        values["usernameError"] = "Invalid username"
        values["success"] = False

    # test the email
    if values["email"]:
        if EMAIL_RE.match(values["email"]) is None:
            values["emailError"] = "Invalid email"
            values["success"] = False

    # test the password conforms
    if PASSWORD_RE.match(values["password"]) is None:
        values["passwordError"] = "Invalid password"
        values["success"] = False
    # and match
    if values["password"] != values["verify"]:
        values["verifyError"] = "Passwords don't match"
        values["success"] = False

    return values


##############################################################
# Blog and Comment Models
##############################################################

class Blog(db.Model):
    name = db.StringProperty(required=True)


# this defines the DataStore Model / Object
class BlogEntry(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    author_id = db.IntegerProperty(required=True)
    # author_id = db.ReferenceProperty(User)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)


class Like(db.Model):
    liked_by = db.ReferenceProperty(User)


# Define Comment Model
class Comment(db.Model):
    comment_text = db.TextProperty(required=True)
    author = db.ReferenceProperty(User, required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    @classmethod
    def add_comment(cls, comment_text, post_id, author_id):
        new_comment = Comment(comment_text=comment_text, post_id=post_id,
                              author_id=author_id)
        new_comment.put()


# Datastore entities are descendants of this blog
fancy_blog = Blog.get_or_insert('fancy_blog', name='Fancy Blog')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/signup', SignupHandler),
    ('/welcome', WelcomeHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/editcomment', EditCommentHandler),
    ('/blog', BlogHandler),
    ('/blog/newpost', BlogNewPostHandler),
    webapp2.Route(r'/blog/post/<post_id:\d+>/like', LikeHandler),
    webapp2.Route(r'/blog/post/<post_id:\d+>/edit', EditPostHandler),
    webapp2.Route(r'/blog/post/<post_id:\d+>/delete', DeletePostHandler),
    webapp2.Route(r'/blog/post/<post_id:\d+>/comment/add', AddCommentHandler),
    ('/blog/(\d+)', BlogEntryHandler)],
    debug=True)
