import os
from flask import Flask
import dash
import dash_bootstrap_components as dbc
# Third party library for authenticating with google
# https://github.com/mathsian/dash-google-auth
from dash_google_auth_email import GoogleOAuth
from configparser import ConfigParser

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
# Create dash app
app = dash.Dash(__name__, server=server, external_stylesheets= [dbc.themes.LITERA], suppress_callback_exceptions=True)
app.title = "data@ada"
# wrap in google oauth
auth = GoogleOAuth(app, authorized_emails, ['openid'])
