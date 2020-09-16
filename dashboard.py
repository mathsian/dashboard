"""
Contains the dash app definition 
"""
# dash
import os
from flask import Flask
import dash
import dash_bootstrap_components as dbc
from dash_google_auth import GoogleOAuth
from configparser import ConfigParser
import index
import store
import dialog
import dispatch
from pages import cohort, team, subject, student

config_object = ConfigParser()
config_object.read("config.ini")
oauth_config = config_object["OAUTH"]
client_id = oauth_config["CLIENT_ID"]
client_secret = oauth_config["CLIENT_SECRET"]
flask_secret_key = oauth_config["FLASK_SECRET_KEY"]
authorized_emails = oauth_config["AUTHORIZED_EMAILS"]

server = Flask(__name__)
server.config.update({
    "GOOGLE_OAUTH_CLIENT_ID": client_id,
    "GOOGLE_OAUTH_CLIENT_SECRET": client_secret
})
server.secret_key = flask_secret_key

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = '1'

# create dash app
app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=False,
    #external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
    external_stylesheets=[dbc.themes.FLATLY],
)

auth = GoogleOAuth(app, authorized_emails, ['openid'], "http://172.26.14.11/login/google/authorized")

app.layout = index.layout
index.register_callbacks(app)
store.register_callbacks(app)
dialog.register_callbacks(app)
cohort.register_callbacks(app)
team.register_callbacks(app)
subject.register_callbacks(app)
student.register_callbacks(app)
dispatch.register_callbacks(app)
if __name__ == "__main__":
    app.run_server(debug=True)
