import dash_bootstrap_components as dbc

update_button =  dbc.Button(children="Update",
                   id={
                       "type": "button",
                       "section": "apprenticeships",
                       "page": "info",
                       "name": "update"
                   },
                   outline=True,
                   color='primary')

layout = [
    dbc.Row(dbc.Col(update_button)),
]

