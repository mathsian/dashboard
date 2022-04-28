import os
from flask import Flask
from flask_mailman import Mail
import dash
import dash_bootstrap_components as dbc
from configparser import ConfigParser

server = Flask(__name__)
mail = Mail()

config_object = ConfigParser()
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config_object.read(config_file)
mail_config = config_object['SMTP']

server.config['MAIL_SERVER'] = mail_config['server']
server.config['MAIL_PORT'] = mail_config['port']
server.config['MAIL_USERNAME'] = mail_config['username']
server.config['MAIL_PASSWORD'] = mail_config['password']
server.config['MAIL_USE_TLS'] = True
server.config['MAIL_USE_SSL'] = False
server.config['MAIL_TIMEOUT'] = 10
server.config['MAIL_DEFAULT_SENDER'] = mail_config['username']
server.config['MAIL_BACKEND'] = 'smtp'

mail.init_app(server)

# Create dash app
app = dash.Dash(__name__,
                server=server,
                url_base_pathname="/",
                external_stylesheets= [dbc.themes.LITERA],
                suppress_callback_exceptions=True)
app.title = "data@ada"

#app.enable_dev_tools(debug=True, dev_tools_ui=True, dev_tools_props_check=True, dev_tools_serve_dev_bundles=True, dev_tools_hot_reload=True,)
