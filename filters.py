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
            placeholder="All",
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
            searchable=False,
            optionHeight=90,
            style={"font-size": "90%"},
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
        Output({"type": "filter-dropdown", "filter": "team"}, "value"),
        Output({"type": "filter-dropdown", "filter": "subject"}, "options"),
        Output({"type": "filter-dropdown", "filter": "subject"}, "value"),
    ],
    [Input({"type": "filter-dropdown", "filter": "cohort"}, "value")],
)
def update_filters(cohort_value):
    teams = data.get_teams(cohort_value)
    subjects = data.get_subjects(cohort_value)
    return [
        [{"label": t, "value": t} for t in teams],
        None,
        [{"label": s[0], "value": s[0]} for s in subjects],
        None,
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
