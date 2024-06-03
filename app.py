from flask import Flask
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# loads the "litera" template and sets it as the default
load_figure_template("litera")

server = Flask(__name__)

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

# required for dash_mantine_components==0.14.0
dash._dash_renderer._set_react_version('18.2.0')

# Create dash app
app = dash.Dash(__name__,
                server=server,
                url_base_pathname="/",
                external_stylesheets=[dbc.themes.LITERA, dbc_css],
                suppress_callback_exceptions=True)
app.title = "data@ada"


if __name__ == '__main__':
    app.enable_dev_tools(debug=True,
                         dev_tools_ui=True,
                         dev_tools_props_check=True,
                         dev_tools_serve_dev_bundles=True,
                         dev_tools_hot_reload=True, )
    app.run(debug=True, port=8001)
