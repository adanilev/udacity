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
def user_logged_in(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if self.currUser:
            return fn(self, *args, **kwargs)
        else:
            return self.redirect('/signup')
    return wrapper


def check_post_exists(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        if BlogEntry.get_by_id(int(kwargs['post_id']), parent=fancy_blog):
            return fn(self, *args, **kwargs)
        else:
            return self.handle_404()
    return wrapper


def check_user_owns_post(fn):
    @wraps(fn)
    @user_logged_in
    @check_post_exists
    def wrapper(self, *args, **kwargs):
        blog_entry = BlogEntry.get_by_id(
            int(kwargs['post_id']), parent=fancy_blog)
        if blog_entry.author.key().id() == self.currUser.key().id():
            return fn(self, *args, **kwargs)
        else:
            self.errs['error_on_post'] = blog_entry.key().id()
            self.errs['post_error'] = 'Whoa there, Nelly! You\'re not the ' \
                                      'rightful owner of that there post!'
            self.redirect('/blog#post-' + kwargs['post_id'])
    return wrapper


def check_comment_exists(fn):
    @wraps(fn)
    @check_post_exists
    def wrapper(self, *args, **kwargs):
        if Comment.get_by_id(
                int(kwargs['comment_id']),
                parent=BlogEntry.get_by_id(
                    int(kwargs['post_id']), parent=fancy_blog)):
            return fn(self, *args, **kwargs)
        else:
            return self.handle_404()
    return wrapper


def check_user_owns_comment(fn):
    @wraps(fn)
    @user_logged_in
    @check_comment_exists
    def wrapper(self, *args, **kwargs):
        blog_entry = BlogEntry.get_by_id(
            int(kwargs['post_id']), parent=fancy_blog)
        comment = Comment.get_by_id(
            int(kwargs['comment_id']), parent=blog_entry)
        if comment.author.key().id() == self.currUser.key().id():
            return fn(self, *args, **kwargs)
        else:
            self.errs['error_on_post'] = blog_entry.key().id()
            self.errs['comment_error'] = 'Whoa there, Nelly! That''s not '\
                                         'your comment.'
            self.redirect('/blog?showComments=' + kwargs['post_id'] +
                          '#post-' + kwargs['post_id'])
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
    blog entries.
    """
    errs = {}

    def get(self):
        """Display the main blog page list. Expand the comments section of one 
        post if asked to"""
        show_comments = self.request.get("showComments")
        if show_comments:
            if BlogEntry.get_by_id(int(show_comments), parent=fancy_blog):
                self.render_blog_page(expand_post=int(show_comments))
            else:
                self.handle_404()
        else:
            self.render_blog_page()

    def render_blog_page(self, posts=None, expand_post=0):
        """Convenience method to render any page showing a blog entry"""
        if posts is None:
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

    @check_post_exists
    def user_owns_post(self, blog_entry):
        """Returns true if currUser owns blog_entry. Keeping in addition to 
        the decorator because it's convenient to use in one place"""
        if blog_entry.author.key().id() == self.currUser.key().id():
            return True
        else:
            return False

##############################################################
# Handlers
##############################################################


class NewPostHandler(BlogHandler):
    @user_logged_in
    def get(self):
        new_post_args = {'subject': '', 'content': '', 'error': ''}
        self.render("new_post.html", new_post_args=new_post_args,
                    currUser=self.currUser)

    @user_logged_in
    def post(self):
        # Get the data the user put in
        new_post_args = {'subject': self.request.get("subject"),
                         'content': self.request.get("content")}
        # If it's a valid post
        if new_post_args['subject'] and new_post_args['content']:
            blog_entry = BlogEntry(parent=fancy_blog,
                                   subject=new_post_args['subject'],
                                   content=new_post_args['content'],
                                   author=self.currUser)
            blog_entry.put()
            # And then redirect to the single post page
            self.redirect('/blog/post/' + str(blog_entry.key().id()))
        else:
            new_post_args['error'] = "Please complete both fields to post!"
            self.render("new_post.html", new_post_args=new_post_args,
                        currUser=self.currUser)


class EditPostHandler(BlogHandler):
    @check_user_owns_post
    def get(self, **kwargs):
        blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                         parent=fancy_blog)
        new_post_args = {'subject': blog_entry.subject,
                         'content': blog_entry.content}
        self.render("new_post.html",
                    new_post_args=new_post_args, currUser=self.currUser)

    @check_user_owns_post
    def post(self, **kwargs):
        new_post_args = {'subject': self.request.get("subject"),
                         'content': self.request.get("content")}

        if new_post_args['subject'] and new_post_args['content']:
            blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                             parent=fancy_blog)
            blog_entry.subject = new_post_args['subject']
            blog_entry.content = new_post_args['content']
            blog_entry.put()
            self.redirect('/blog#post-' + kwargs['post_id'])
        else:
            new_post_args['error'] = "Please complete both fields to post!"
            self.render("new_post.html", new_post_args=new_post_args,
                        currUser=self.currUser)


class DeletePostHandler(BlogHandler):
    @check_user_owns_post
    def get(self, **kwargs):
        blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                         parent=fancy_blog)
        blog_entry.delete()
        return self.redirect('/blog')


class ReadOnePostHandler(BlogHandler):
    @check_post_exists
    def get(self, **kwargs):
        blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                         parent=fancy_blog)
        self.render_blog_page([blog_entry])


class SignupHandler(Handler):
    def get(self):
        self.render("signup.html", currUser=self.currUser, values={})

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
            print values
            self.render("signup.html", values=values)


class WelcomeHandler(BlogHandler):
    @user_logged_in
    def get(self):
        username = self.currUser.username
        self.render("welcome.html", username=username,
                    currUser=self.currUser)


class NewCommentHandler(BlogHandler):
    @user_logged_in
    @check_post_exists
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
    @check_user_owns_comment
    def get(self, **kwargs):
        blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                         parent=fancy_blog)
        comment = Comment.get_by_id(int(kwargs['comment_id']),
                                    parent=blog_entry)
        print self.errs
        self.render("editcomment.html", comment_text=comment.comment_text,
                    errors=self.errs)

    @check_user_owns_comment
    def post(self, **kwargs):
        blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                         parent=fancy_blog)
        comment = Comment.get_by_id(int(kwargs['comment_id']),
                                    parent=blog_entry)
        comment_text = self.request.get("comment_text")
        if comment_text:
            comment.comment_text = comment_text
            comment.put()
            self.redirect('/blog?showComments=' + str(blog_entry.key().id()) +
                          '#post-' + str(blog_entry.key().id()))
        else:
            self.errs['edit_comment_error'] = 'Please enter a comment to ' \
                                              'update.'
            self.redirect('/blog/post/' + str(blog_entry.key().id()) +
                          '/comment/' + str(comment.key().id()) + '/edit')


class DeleteCommentHandler(BlogHandler):
    @check_user_owns_comment
    def get(self, **kwargs):
        blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                         parent=fancy_blog)
        comment = Comment.get_by_id(int(kwargs['comment_id']),
                                    parent=blog_entry)
        comment.delete()
        self.errs['comment_error'] = "Comment deleted!"
        self.redirect('/blog?showComments=' + str(blog_entry.key().id()) +
                      '#post-' + str(blog_entry.key().id()))


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
            login_error = 'Invalid login details. You shall not pass.'
            self.render("login.html", login_error=login_error)


class LogoutHandler(Handler):
    def get(self):
        # set user_id cookie to ''
        self.response.headers.add_header('Set-Cookie', 'user_id=''; Path=/')
        # and redirect
        self.redirect("/signup")


class LikeHandler(BlogHandler):
    @user_logged_in
    @check_post_exists
    def get(self, **kwargs):
        blog_entry = BlogEntry.get_by_id(int(kwargs['post_id']),
                                         parent=fancy_blog)
        liked_by = User.get_by_id(self.currUser.key().id())
        like = db.Query(Like).ancestor(blog_entry.key())\
            .filter("liked_by =", liked_by)\
            .get()

        # Show error if they are trying to like their own post
        # Not using a decorator here because that shows a generic error when
        # they DON'T own a post. This shows a specific error when they DO own
        # the post.
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
        values["username_error"] = "Sorry, that username is already taken"
        values["success"] = False

    # verify username
    if USER_RE.match(values["username"]) is None:
        values["username_error"] = "Invalid username"
        values["success"] = False

    # test the email
    if values["email"]:
        if EMAIL_RE.match(values["email"]) is None:
            values["email_error"] = "Invalid email"
            values["success"] = False

    # test the password conforms
    if PASSWORD_RE.match(values["password"]) is None:
        values["password_error"] = "Invalid password"
        values["success"] = False
    # and match
    if values["password"] != values["verify"]:
        values["verify_error"] = "Passwords don't match"
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
    author = db.ReferenceProperty(User, required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)


class Like(db.Model):
    liked_by = db.ReferenceProperty(User)


# Define Comment Model
class Comment(db.Model):
    comment_text = db.TextProperty(required=True)
    author = db.ReferenceProperty(User, required=True)
    created = db.DateTimeProperty(auto_now_add=True)


# Datastore entities are descendants of this blog
fancy_blog = Blog.get_or_insert('fancy_blog', name='Fancy Blog')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/signup', SignupHandler),
    ('/welcome', WelcomeHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/blog', BlogHandler),
    ('/blog/newpost', NewPostHandler),
    webapp2.Route(r'/blog/post/<post_id:\d+>', ReadOnePostHandler),
    webapp2.Route(r'/blog/post/<post_id:\d+>/edit', EditPostHandler),
    webapp2.Route(r'/blog/post/<post_id:\d+>/delete', DeletePostHandler),
    webapp2.Route(r'/blog/post/<post_id:\d+>/comment/add', NewCommentHandler),
    webapp2.Route(r'/blog/post/<post_id:\d+>/comment/<comment_id:\d+>/edit',
                  EditCommentHandler),
    webapp2.Route(r'/blog/post/<post_id:\d+>/comment/<comment_id:\d+>/delete',
                  DeleteCommentHandler),
    webapp2.Route(r'/blog/post/<post_id:\d+>/like', LikeHandler)],
    debug=True)
