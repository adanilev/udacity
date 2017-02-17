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
        n = self.request.get("n")
        if n:
            n = int(n)
        self.render("index.html", n=n)

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
        self.render("signup.html")

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/fizzbuzz', FizzBuzzHandler),
    ('/shoppinglist', ShoppingListHandler),
    ('/rot13', ROT13Handler),
    ('/signup', SignupHandler)],
    debug=True)
