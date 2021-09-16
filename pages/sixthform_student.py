import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from urllib.parse import parse_qs, urlencode
from app import app
import data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")

cohort_dropdown = dbc.DropdownMenu(id="student-cohort-dropdown")
team_dropdown = dbc.DropdownMenu(id="student-team-dropdown")

cardheader_layout = dbc.Row([
    dbc.Col(html.Div("Cohort"), width=2, align='center'),
    dbc.Col([cohort_dropdown], width=2, align='end'),
    dbc.Col(html.Div("Team"), width=2, align='center'),
    dbc.Col([team_dropdown], width=2, align='end')
],
                 justify='start')

# The student list is on a separate card alongside the tabs
# so that it isn't updated when the tab changes
student_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "student"
    },
    options={
        "resizableColumns": False,
        "selectable": True,
        "maxHeight": "60vh",
    },
    theme='bootstrap/tabulator_bootstrap4',
    columns=[
        {
            "formatter": "rowSelection",
            "titleFormatter": "rowSelection",
            "horizAlign": "center",
            "headerSort": False,
            "widthGrow": 1,
        },
        {
            "title": "Student ID",
            "field": "student_id",
            "visible": False,
        },
        {
            "field": "given_name",
            "widthGrow": 4,
            "headerFilter": True,
            "headerFilterPlaceholder": "Search",
        },
        {
            "field": "family_name",
            "widthGrow": 6,
            "headerFilter": True,
            "headerFilterPlaceholder": "Search",
        },
    ],
)

sidebar_layout = student_table


@app.callback([
    Output("student-cohort-dropdown", "label"),
    Output("student-cohort-dropdown", "children"),
    Output("student-team-dropdown", "label"),
    Output("student-team-dropdown", "children"),
], [
    Input("location", "pathname"),
    Input("location", "search"),
], [State("student-team-dropdown", "label")])
def update_teams(pathname, search, team):
    # Set teams and cohort from location
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of cohorts from query
    cohort = search_dict.get('cohort', ['All'])[0]
    if cohort == 'All':
        teams = data.get_teams(['2022', '2123'])
    else:
        teams = data.get_teams(cohort)
    # Get list of teams
    team = search_dict.get("team", ['All'])[0]
    # Populate the dropdowns
    team_items = [dbc.DropdownMenuItem()]
    for t in ['All'] + teams:
        s = urlencode(query={'cohort': cohort, 'team': t})
        team_items.append(dbc.DropdownMenuItem(t, href=f'{pathname}?{s}'))
    cohort_items = []
    for c in ['All', '2022', '2123']:
        s = urlencode(query={'cohort': c})
        cohort_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))
    return (cohort, cohort_items, team, team_items)

@app.callback(
    Output({
        "type": "table",
        "page": "student"
    }, "data"),
    [
        Input("student-cohort-dropdown", "label"),
        Input("student-team-dropdown", "label")
    ],
)
def update_student_table(cohort, team):
    if cohort != 'All' and team != 'All':
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort != 'All':
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        enrolment_docs = data.get_data("all", "type", "enrolment")
    enrolment_df = pd.DataFrame(enrolment_docs).sort_values(
        by=["given_name", "family_name"])
    enrolment_df["student_id"] = enrolment_df["_id"]
    return enrolment_df.to_dict(orient='records')

