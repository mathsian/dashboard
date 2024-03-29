import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
from dash_ag_grid import AgGrid
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

employer_dropdown = dbc.DropdownMenu(
    id={
        "type": "dropdown",
        "section": "apprenticeships",
        "page": "employers",
        "name": "employer"
    },
    nav=True,
)

filter_nav = dbc.Nav([dbc.NavItem(employer_dropdown)], fill=True)

student_table = AgGrid(
    id={
        "type": "table",
        "section": "apprenticeships",
        "page": "employers",
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
        "page": "employers",
        "name": "selected"
    }, storage_type='memory'),
    dcc.Store(id={
        "type": "storage",
        "section": "apprenticeships",
        "page": "employers",
        "name": "students"
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
            "page": "employers",
            "name": "employer"
        }, "label"),
    Output(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "employers",
            "name": "employer"
        }, "children"),
    Output(
        {
            "type": "table",
            "section": "apprenticeships",
            "page": "employers",
            "name": "list"
        }, "rowData"),
    Output(
        {
            "type": "storage",
            "section": "apprenticeships",
            "page": "employers",
            "name": "students"
        }, "data"),
], [
    Input("location", "search"),
], [
    State("location", "pathname"),
    State(
        {
            "type": "dropdown",
            "section": "apprenticeships",
            "page": "employers",
            "name": "employer"
        }, "label")
])
def update_employers(search, pathname, employer):
    search_dict = parse_qs(search.removeprefix('?'))
    # Get list of employers
    employers = app_data.get_employer_list()
    employer_query = search_dict.get('employer', False)
    # Default to first employer
    employer = employer or employers[0]
    # If employer in query is valid switch to that
    if employer_query:
        if employer_query[0] in employers:
            employer = employer_query[0]
    employer_items = []
    for c in employers:
        s = urlencode(query={'employer': c})
        employer_items.append(dbc.DropdownMenuItem(c, href=f'{pathname}?{s}'))
    # Get students in scope
    students = app_data.get_students_by_employer(employer)
    return (employer, employer_items, students, students)


@app.callback(
    Output(
        {
            "type": "storage",
            "section": "apprenticeships",
            "page": "employers",
            "name": "selected"
        }, "data"), [
            Input(
                {
                    "type": "table",
                    "section": "apprenticeships",
                    "page": "employers",
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
