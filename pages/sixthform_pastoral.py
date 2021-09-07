import filters
import dash_bootstrap_components as dbc

layout = dbc.Row([
    dbc.Col([
        filters.cohort,
        ]),
    dbc.Col([
        filters.team
    ])
])
