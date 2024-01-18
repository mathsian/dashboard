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

from dash_ag_grid import AgGrid

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
        "page": "cohorts",
        "name": "cohort"
    },
    nav=True,
)

filter_nav = dbc.Nav([dbc.NavItem(cohort_dropdown)], fill=True)

student_table = AgGrid(
    id={
        "type": "table",
        "section": "apprenticeships",
        "page": "cohorts",
        "name": "list"
    },
    className='ag-theme-alpine',
    columnDefs=[
        {
            "field": "given_name",
            "headerName": "Given",
            "filter": True,
            "suppressMenu": True,
            "floatingFilter": True,
            "checkboxSelection": True,
            "headerCheckboxSelection": True,
            "headerCheckboxSelectionFilteredOnly": True,
            "headerCheckboxSelectionCurrentPageOnly": True,
        },
        {
            "field": "family_name",
            "headerName": "Family",
            "filter": True,
            "suppressMenu": True,
            "floatingFilter": True,
        },
    ],
    getRowId="params.data.student_id",
    columnSize='responsiveSizeToFit',
    dashGridOptions={
        'pagination': True,
        'paginationAutoPageSize': True,
        'rowSelection': 'multiple',
        'rowMultiSelectWithClick': True,
    }
)

layout = [
    dcc.Store(id={
        "type": "storage",
        "section": "apprenticeships",
        "page": "cohorts",
        "name": "selected"
    },
              storage_type='memory'),
    dbc.Card([
        dbc.CardHeader(filter_nav),
        dbc.CardBody(student_table)
    ])
]


@app.callback([
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "cohorts",
            "name": "cohort"
        }, "label"),
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "cohorts",
            "name": "cohort"
        }, "children"),
    Output(
        {
            "type": "table",
            "section": "apprenticeships",
            "page": "cohorts",
            "name": "list"
        }, "rowData")
], [
    Input("location", "search"),
], [
    State("location", "pathname"),
    State(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "cohorts",
            "name": "cohort"
        }, "label")
])
def update_cohorts(search, pathname, cohort):
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of cohorts
    cohorts = ['All'] + app_data.get_cohort_list()
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
    if cohort == 'All':
        students = app_data.get_all_students()
    else:
        students = app_data.get_students_by_cohort_name(cohort)
    return (cohort, cohort_items, students)


@app.callback(
    Output(
        {
            "type": "storage",
            "section": "apprenticeships",
            "page": "cohorts",
            "name": "selected"
        }, "data"), [
            Input(
                {
                    "type": "table",
                    "section": "apprenticeships",
                    "page": "cohorts",
                    "name": "list"
                }, "selectedRows"),
            Input("location", "hash")
        ])
def update_selected_students(selectedRows, url_hash):
    input_id = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
    if input_id == 'location':
        selected_ids = url_hash.removeprefix('#').split(',')
    else:
        selectedRows = selectedRows or []
        selected_ids = [row.get('student_id') for row in selectedRows]
    return selected_ids
