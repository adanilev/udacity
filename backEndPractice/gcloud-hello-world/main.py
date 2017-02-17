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
import rot13
import signup

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    def get(self):
        self.render("index.html")

class SquaresHandler(Handler):
    def get(self):
        n = self.request.get("n",10)
        error = ""
        if n:
            n = int(n)
        if n > 100:
            n=0
            error="Slow down cowboy, enter a number <= 100"
        self.render("squares.html", n=n, error=error)

class FizzBuzzHandler(Handler):
    def get(self):
        n = self.request.get("n", 3)
        n = n and int(n)
        self.render("fizzbuzz.html", n=n)

class ShoppingListHandler(Handler):
    def get(self):
        items = self.request.get_all("food")
        self.render("shopping_list.html", items=items)

class ROT13Handler(Handler):
    def get(self):
        self.render("rot13.html")

    def post(self):
        text = self.request.get("text")
        converted = rot13.convert(text, 1)
        self.render("rot13.html", converted=converted)

class SignupHandler(Handler):
    def get(self):
        self.render("signup.html")

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

        values = signup.verify(values)

        if values["success"]:
            self.redirect("/welcome?username=%s" % values["username"])
        else:
            self.render("signup.html", **values)
            # i couldn't figure out the **kwargs notation before i wrote this part
            ########
            # self.render("signup.html", username=values["username"],
            #                            usernameError=values["usernameError"],
            #                            password=values["password"],
            #                            passwordError=values["passwordError"],
            #                            verify=values["verify"],
            #                            verifyError=values["verifyError"],
            #                            email=values["email"],
            #                            emailError=values["emailError"])

class SignupWelcomeHandler(Handler):
    def get(self):
        username = self.request.get("username")
        self.render("welcome.html",username=username)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/squares', SquaresHandler),
    ('/fizzbuzz', FizzBuzzHandler),
    ('/shoppinglist', ShoppingListHandler),
    ('/rot13', ROT13Handler),
    ('/signup', SignupHandler),
    ('/welcome', SignupWelcomeHandler)],
    debug=True)
