import re
import hmac
import random
import string
import hashy

from google.appengine.ext import db

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
