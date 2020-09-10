"""
Contains the dash app definition 
"""
# dash
from flask import Flask
import dash
import dash_bootstrap_components as dbc
import index
import store
import dialog
import dispatch
from pages import cohort, team, subject, student
from configparser import ConfigParser
from dash_google_auth import GoogleOAuth

config_object = ConfigParser()
config_object.read("config.ini")
oauth_config = config_object["OAUTH"]
client_id = oauth_config["client_id"]
client_secret = oauth_config["client_secret"]
server = Flask(__name__)
server.config.update({
    'GOOGLE_OAUTH_CLIENT_ID': client_id,
    'GOOGLE_OAUTH_CLIENT_SECRET': client_secret
    })
server.secret_key = oauth_config["flask_secret_key"]

# create dash app
app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=False,
    #    external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
    external_stylesheets=[dbc.themes.LUX],
)

additional_scopes = ['openid']
authorized_emails = ['ian@ada.ac.uk']
auth = GoogleOAuth(app, authorized_emails, additional_scopes)

app.layout = index.layout
store.register_callbacks(app)
dialog.register_callbacks(app)
cohort.register_callbacks(app)
team.register_callbacks(app)
subject.register_callbacks(app)
student.register_callbacks(app)
dispatch.register_callbacks(app)
if __name__ == "__main__":
    app.run_server(debug=True)
