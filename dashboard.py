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

# create dash app
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=False,
    #external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"],
    external_stylesheets=[dbc.themes.FLATLY],
)

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
