import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
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

cohort_dropdown = dbc.DropdownMenu(
    id="report-cohort-dropdown",
    nav=True,
)
team_dropdown = dbc.DropdownMenu(id="report-team-dropdown", nav=True)

filter_nav = dbc.Nav(
    [dbc.NavItem(cohort_dropdown),
     dbc.NavItem(team_dropdown)], fill=True)

# The student list is on a separate card alongside the tabs
# so that it isn't updated when the tab changes
student_table = dash_tabulator.DashTabulator(
    id="this_table_right_here",
    options={
        "resizableColumns": False,
        "selectable": True,
        "maxHeight": "70vh",
        "dataLoaded": ns("dataLoaded"),
        "rowSelected": ns("rowSelected")
    },
    theme='bootstrap/tabulator_bootstrap4',
    columns=[
        {
            "title": "Selected",
            "field": "selected",
            "formatter": "tickCross",
            "formatterParams": {
                "crossElement": False
            },
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

layout = [
    dcc.Store(id="sixthform-student-store", storage_type='memory'),
    dcc.Store(id="sixthform-selected-store", storage_type='memory'),
    dbc.Row(dbc.Col(filter_nav)),
    dbc.Row(dbc.Col(student_table))
]


@app.callback([
    Output("report-cohort-dropdown", "label"),
    Output("report-cohort-dropdown", "children"),
    Output("report-team-dropdown", "label"),
    Output("report-team-dropdown", "children"),
    Output("sixthform-student-store", "data")
], [
    Input("location", "search"),
], [State("location", "pathname"),
    State("report-team-dropdown", "label")])
def update_teams(search, pathname, team):
    # Set teams and cohort from location
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of cohorts from query
    cohort = search_dict.get('cohort', [curriculum.cohorts[-1]])[0]
    teams = data.get_teams(cohort)
    # Get list of teams
    team = search_dict.get("team", ['All'])[0]
    # Populate the dropdowns
    team_items = [dbc.DropdownMenuItem()]
    for t in ['All'] + teams:
        s = urlencode(query={'cohort': cohort, 'team': t})
        team_items.append(dbc.DropdownMenuItem(t, href=f'{pathname}?{s}'))
    cohort_items = []
    for c in curriculum.cohorts:
        s = urlencode(query={'cohort': c})
        cohort_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))
    # Get data in scope
    this_year_start = curriculum.this_year_start
    enrolment_docs = data.get_enrolment_by_cohort_team(cohort, team)
    student_ids = [e.get('_id') for e in enrolment_docs]
    attendance_docs = data.get_data("attendance", "student_id", student_ids)
    assessment_docs = data.get_data("assessment", "student_id", student_ids)
    # Kudos processing
    kudos_docs = data.get_data("kudos", "student_id", student_ids)
    kudos_df = pd.merge(pd.DataFrame.from_records(enrolment_docs, columns=['_id', 'given_name', 'family_name']),
                        pd.DataFrame.from_records(kudos_docs, columns=['student_id', 'date', 'ada_value', 'points', 'from', 'description']).query("date >= @this_year_start"),
                        how="left",
                        left_on="_id",
                        right_on="student_id")
    kudos_pivot_df = pd.pivot_table(
        kudos_df,
        values="points",
        index=["student_id", "given_name", "family_name"],
        columns="ada_value",
        aggfunc=sum,
        fill_value=0,
    ).reindex(curriculum.values, axis=1, fill_value=0)
    kudos_pivot_df["total"] = kudos_pivot_df.sum(axis=1)
    kudos_pivot_df = kudos_pivot_df.reset_index()
    kudos_pivot_docs = kudos_pivot_df.to_dict(orient='records')

    concern_docs = data.get_data("concern", "student_id", student_ids)
    store_data = {
        "student_ids": student_ids,
        "enrolment_docs": enrolment_docs,
        "attendance_docs": attendance_docs,
        "assessment_docs": assessment_docs,
        "kudos_docs": kudos_docs,
        "kudos_pivot_docs": kudos_pivot_docs,
        "concern_docs": concern_docs,
    }
    return (cohort, cohort_items, team, team_items, store_data)


@app.callback(Output("sixthform-selected-store", "data"),
[
    Input("this_table_right_here", "multiRowsClicked"),
    Input("location", "hash")
])
def update_selected_students(multiRowsClicked, url_hash):
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if input_id == 'location':
        selected_ids = url_hash.removeprefix('#').split(',')
    else:
        multiRowsClicked = multiRowsClicked or []
        selected_ids = [row.get('_id') for row in multiRowsClicked]
    return selected_ids

@app.callback(Output("this_table_right_here", "data"),
              [Input("sixthform-student-store", "data")])
def update_student_table(store_data):
    enrolment_docs = store_data.get("enrolment_docs")
    return enrolment_docs
