import dash_bootstrap_components as dbc
from dash import html

update_button =  dbc.Button(children="Update",
                   id={
                       "type": "button",
                       "section": "apprenticeships",
                       "page": "info",
                       "name": "update"
                   },
                   outline=True,
                   color='primary')

layout = dbc.Card([
    dbc.CardHeader(),
    dbc.CardBody(html.Center(update_button)),
])

