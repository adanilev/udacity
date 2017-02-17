import re

#regexs
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

def verify(values):
    #innocent until proven guilty
    values["success"] = True

    #verify username
    if USER_RE.match(values["username"]) == None:
        values["usernameError"] = "Invalid username"
        values["success"] = False

    #test the password conforms
    if PASSWORD_RE.match(values["password"]) == None:
        values["passwordError"] = "Invalid password"
        values["success"] = False
    #and match
    if values["password"] != values["verify"]:
        values["verifyError"] = "Passwords don't match"
        values["success"] = False
    #then blank them
    values["password"] = ""
    values["verify"] = ""

    #test the email
    if values["email"]:
        if EMAIL_RE.match(values["email"]) == None:
            values["emailError"] = "Invalid email"
            values["success"] = False

    return values
