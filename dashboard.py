"""
Contains the dash app definition 
"""
# dash
import dash
import dash_bootstrap_components as dbc
from callbacks import register_callbacks
import index

# create dash app
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.LUX],
)
app.layout = index.layout
register_callbacks(app)
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
