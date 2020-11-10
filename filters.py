import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from app import app
import data

cohort = html.Div(
    id={"type": "filter-div", "filter": "cohort"},
    children=[
        "Cohort",
        dcc.Dropdown(
            id={"type": "filter-dropdown", "filter": "cohort"},
            placeholder="Select a cohort",
            options=[{"label": s, "value": s} for s in ["1921", "2022"]],
            value="1921",
            clearable=False,
            persistence=True,
            persistence_type="local",
            searchable=False,
            
        ),
    ],
)
team = html.Div(
    id={"type": "filter-div", "filter": "team"},
    children=[
        "Team",
        dcc.Dropdown(
            id={"type": "filter-dropdown", "filter": "team"},
            placeholder="Select a team",
            persistence=True,
            persistence_type="local",
            searchable=False,
        ),
    ],
)
subject = html.Div(
    id={"type": "filter-div", "filter": "subject"},
    children=[
        "Subject ",
        dcc.Dropdown(
            id={"type": "filter-dropdown", "filter": "subject"},
            placeholder="Select a subject",
            persistence=True,
            persistence_type="local",
            searchable=False,
        ),
    ],
)
layout = html.Div([cohort, team, subject], id="filter-div", style={"padding": "10px"})

url_map = {
    "/": [True, True, True, True],
    "/pastoral": [False, False, False, True],
    "/academic": [False, False, True, False],
    "/student": [False, False, False, True],
}


@app.callback(
    [
        Output({"type": "filter-dropdown", "filter": "team"}, "options"),
        Output({"type": "filter-dropdown", "filter": "subject"}, "options"),
    ],
    [Input({"type": "filter-dropdown", "filter": "cohort"}, "value")],
)
def update_filters(cohort_value):
    teams = data.get_teams(cohort_value)
    subjects = ["1", "2", "3"]
    return [
        [{"label": t, "value": t} for t in teams],
        [{"label": s, "value": s} for s in subjects],
    ]


@app.callback(
    [
        Output("filter-div", "hidden"),
        Output({"type": "filter-div", "filter": "cohort"}, "hidden"),
        Output({"type": "filter-div", "filter": "team"}, "hidden"),
        Output({"type": "filter-div", "filter": "subject"}, "hidden"),
    ],
    [Input("url", "pathname")],
)
def hide_dropdowns(pathname):
    return url_map.get(pathname, [True, True, True, True])
