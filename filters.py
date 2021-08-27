import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app
import data

cohort = dcc.Dropdown(
    id={
        "type": "filter-dropdown",
        "filter": "cohort"
    },
    placeholder="Select a cohort",
    options=[{
        "label": s,
        "value": s
    } for s in ["1921", "2022", "2123"]],
    value="1921",
    clearable=False,
    persistence=True,
    persistence_type="local",
    searchable=False,
)
team = dcc.Dropdown(
    id={
        "type": "filter-dropdown",
        "filter": "team"
    },
    placeholder="All",
    searchable=False,
)

subject = dcc.Dropdown(
    id={
        "type": "filter-dropdown",
        "filter": "subject"
    },
    placeholder="Select a subject",
    searchable=False,
)
