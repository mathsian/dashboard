"""
Starts the database connection and contains the top level layout.

Content is then grabbed from page layouts based on the pathname of the current url.
"""
# dash
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# config
from configparser import ConfigParser
# couchdb
from cloudant.client import CouchDB
from cloudant.error import CloudantClientException
# internal
from pages import student, subject, top, report

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


# create dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Top level container
app.layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])

# Only one callback required. When the url changes, replace the layout
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    response = html.Div([f'404 I guess on {pathname}'])
    if pathname == '/pages/student':
        response = student.layout
    elif pathname == '/pages/subject':
        response = subject.layout
    elif pathname == '/pages/top':
        response = top.layout
    elif pathname == '/pages/report':
        response = report.layout
    return response

if __name__ == '__main__':
    app.run_server(debug=True)
