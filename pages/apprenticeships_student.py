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
import app_data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")

cohort_dropdown = dbc.DropdownMenu(
    id={
        "type": "dropdown",
        "section": "apprenticeships",
        "page": "student",
        "name": "cohort"
    },
    nav=True,
)

filter_nav = dbc.Nav([dbc.NavItem(cohort_dropdown)], fill=True)

# The student list is on a separate card alongside the tabs
# so that it isn't updated when the tab changes
student_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "section": "apprenticeships",
        "page": "student",
        "name": "list"
    },
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
    dcc.Store(id="apprenticeships-student-store", storage_type='memory'),
    dcc.Store(id="apprenticeships-selected-store", storage_type='memory'),
    dbc.Row(dbc.Col(filter_nav)),
    dbc.Row(dbc.Col(student_table))
]


@app.callback([
    Output({
        "type": "dropdown",
        "section": "apprenticeships",
        "page": "student",
        "name": "cohort"
    }, "label"),
    Output({
        "type": "dropdown",
        "section": "apprenticeships",
        "page": "student",
        "name": "cohort"
    }, "children"),
    Output("apprenticeships-student-store", "data")
], [
    Input("location", "search"),
], [State("location", "pathname"),
    State({
        "type": "dropdown",
        "section": "apprenticeships",
        "page": "student",
        "name": "cohort"
    }, "label")])
def update_cohorts(search, pathname, cohort):
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of cohorts
    cohorts = app_data.get_cohort_list()
    cohort_query = search_dict.get('cohort', False)
    # Default to first cohort
    cohort = cohort or cohorts[0]
    # If cohort in query is valid switch to that
    if cohort_query:
        if cohort_query[0] in cohorts:
            cohort = cohort_query[0]
    cohort_items = []
    for c in cohorts:
        s = urlencode(query={'cohort': c})
        cohort_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))
    # Get students in scope
    students = app_data.get_students_by_cohort_name(cohort)
    store_data = {"students": students}
    return (cohort, cohort_items, store_data)


@app.callback(Output("apprenticeships-selected-store", "data"),
[
    Input({
        "type": "table",
        "section": "apprenticeships",
        "page": "student",
        "name": "list"
    }, "multiRowsClicked"),
    Input("location", "hash")
])
def update_selected_students(multiRowsClicked, url_hash):
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if input_id == 'location':
        selected_ids = url_hash.removeprefix('#').split(',')
    else:
        multiRowsClicked = multiRowsClicked or []
        selected_ids = [row.get('student_id') for row in multiRowsClicked]
    return selected_ids

@app.callback(Output({
        "type": "table",
        "section": "apprenticeships",
        "page": "student",
        "name": "list"
    }
 , "data"),
              [Input("apprenticeships-student-store", "data")])
def update_student_table(store_data):
    students = store_data.get("students")
    return students
