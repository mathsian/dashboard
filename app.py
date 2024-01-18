from flask import Flask
import dash
import dash_bootstrap_components as dbc

server = Flask(__name__)

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

# Create dash app
app = dash.Dash(__name__,
                server=server,
                url_base_pathname="/",
                external_stylesheets=[dbc.themes.LITERA, dbc_css],
                suppress_callback_exceptions=True)
app.title = "data@ada"

app.enable_dev_tools(debug=True,
                     dev_tools_ui=True,
                     dev_tools_props_check=True,
                     dev_tools_serve_dev_bundles=True,
                     dev_tools_hot_reload=True,)
