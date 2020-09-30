"""
Instantiates the dash app and registers callbacks for all sections 
"""
import os
from flask import Flask
import dash
import dash_bootstrap_components as dbc
# Third party library for authenticating with google
# https://github.com/mathsian/dash-google-auth
from dash_google_auth import GoogleOAuth

from configparser import ConfigParser

# Layouts and callbacks for the tabs/pages
import index, store, dispatch
from pages import cohort, team, subject, student
from forms import kudos, concern

# Get configuration
config_object = ConfigParser()
config_object.read("config.ini")
oauth_config = config_object["OAUTH"]
client_id = oauth_config["CLIENT_ID"]
client_secret = oauth_config["CLIENT_SECRET"]
authorized_emails = oauth_config["AUTHORIZED_EMAILS"]

# We need the flask instance to run google oauth
server = Flask(__name__)
server.config.update({
    "GOOGLE_OAUTH_CLIENT_ID": client_id,
    "GOOGLE_OAUTH_CLIENT_SECRET": client_secret
})
server.secret_key = os.urandom(24) 

# Once we have https we can remove this in production
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'

# create dash app
app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/',
    suppress_callback_exceptions=False,
    #external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
    external_stylesheets=[dbc.themes.FLATLY],
)
# wrap in google oauth
auth = GoogleOAuth(app, authorized_emails, ['openid'])

# register the layout
# index.layout contains the layouts of all the other sections
app.layout = index.layout
# register the callbacks
for section in [index, store, dispatch, cohort, team, subject, student, kudos, concern]:
    section.register_callbacks(app)

if __name__ == "__main__":
    # If we're running via __main__ then we're in development
    app.run_server(debug=True, port=8001)
