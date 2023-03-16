#!/bin/false

from flask import Flask, request, make_response
import db
import json
from base64 import urlsafe_b64decode
from uuid import UUID

app = Flask(__name__)

APP_TITLE="SecuDo"

TEMPLATE_HEADER = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{title}</title>
</head>
<body>
"""

TEMPLATE_FOOTER = """<div id='footer'>
<p>Made with &#128161; by <a href="https://www.linu.pl/">Linu.pl</a></p>
</div> <!--footer div-->
</body>
</html>
"""

TEMPLATE_GREETING = """<div id="main">
<h1>{title}</h1>
<p>Tired of having to create yet another account just to share a grocery list with your friend? <b>We are too!</b></p>
<p>We decided to design yet another to-do app with ease-of-use in mind. Say NO! to throw-away accounts!</p>
<ol>
<li>Provide a secure passphrase in the field below.</li>
<li>Click the "Take me to my list!" button.</li>
<li>That's it!</li>
</ol>
<p>Isn't it beautiful? No emails, no accounts! Just a passphrase and voila!</p>
<p>Are you wondering how to collaborate with your friend? Well, wonder no more! Just share them your passphrase and let them do their part!</p>
<form action="/list" method='post'>
  <label for="passphrase">Secure passphrase:</label><br>
  <input type="password" id="passphrase" name="passphrase"><br>
  <input type="submit" value="Take me to my list!">
</form> 
</div> <!--main div-->
"""

TEMPLATE_LIST = """<div id="main">
<h1>{title} list: {list_name}</h1>
<p>Boink!</p>
<a href="/">Return to the homepage</a>
</div> <!--main div-->
"""

@app.route("/")
def greeting():
    return make_page(TEMPLATE_GREETING.format(title=APP_TITLE))

@app.route("/list/<uid>")
def view_list(uid):
    if request.method == "GET":
        s_list = db.get_list_by_uuid(UUID(uid))
        return make_page(TEMPLATE_LIST.format(title=APP_TITLE, list_name=s_list.name))

@app.route("/lists")
def get_lists():
    body="""<div id="main">
<h1>{title} lists</h1>
<ul>
""".format(title=APP_TITLE)
    lists = db.get_lists()
    for slist in lists:
        body += """<li><a href="/list/{uid}">{name}</a></li>""".format(
            uid=UUID(bytes=urlsafe_b64decode(slist.uuid)), name=slist.name
        )
    body+="""</ul>
<a href="/">Return to the homepage</a>
</div> <!--main div-->
"""
    return make_page(body)

def make_page(content_body):
    html=TEMPLATE_HEADER.format(title=APP_TITLE)
    html+=content_body
    html+=TEMPLATE_FOOTER
    return make_response(html)
