import os
from flask import Flask, request, redirect
from flask_cors import CORS
import dash
import dash_bootstrap_components as dbc
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
    "GOOGLE_OAUTH_CLIENT_SECRET": client_secret,
    "GOOGLE_LOGIN_REDIRECT_SCHEME": "https",
    "GOOGLE_LOGIN_REDIRECT_URI": "https://testing.ada.ac.uk/login/google/authorized"
})
server.secret_key = os.urandom(24) 

# Create dash app
app = dash.Dash(__name__, server=server,
                url_base_pathname="/",
                external_stylesheets= [dbc.themes.LITERA],
                suppress_callback_exceptions=True)
app.title = "data@ada"

app.enable_dev_tools(debug=True, dev_tools_ui=True, dev_tools_props_check=True, dev_tools_serve_dev_bundles=True, dev_tools_hot_reload=True,)

# wrap in google oauth
auth = GoogleOAuth(app=app,
                   authorized_emails=authorized_emails,
                   additional_scopes=['openid'])

# fix cors problems resulting from the redirect below
CORS(server)
# Redirect if unauthorized
@server.before_request
def before_request_fun():
    #print(f"Accessing {request.path}")
    #print(f"Authorized: {auth.is_authorized()}")
    if not auth.is_authorized() and request.path != "/login/google/authorized":
        #print("Not authorized")
        if request.path != '/login/google':
            #print("Redirecting")
            return redirect('/login/google')
        else:
            pass
            #print("Not redirecting")
    #print("Authorized")
