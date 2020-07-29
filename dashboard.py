"""
Gives out database connections and contains the dash app definition 
"""
# dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
# config
from configparser import ConfigParser
# couchdb
from cloudant.client import CouchDB
from cloudant.error import CloudantClientException


def get_db():
    # read the config
    config_object = ConfigParser()
    config_object.read("config.ini")
    # and get couchdb settings
    couchdb_config = config_object["COUCHDB"]
    couchdb_user = couchdb_config["user"]
    couchdb_pwd = couchdb_config["pwd"]
    couchdb_ip = couchdb_config["ip"]
    couchdb_port = couchdb_config["port"]
    # create connection
    client = CouchDB(couchdb_user,
                    couchdb_pwd,
                    url=f'http://{couchdb_ip}:{couchdb_port}',
                    connect=True,
                    autorenew=True)
    # and select database
    db = client['testing']
    return db


# create dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
