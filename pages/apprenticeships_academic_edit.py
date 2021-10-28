import filters
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
import urllib
from app import app
import data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")

result_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "section": "apprenticeships",
        "page": "academic",
        "tab": "edit"
    },
    options={
        "placeholder": "Select a module",
        # "layout": "fitDataStretch",
        # "maxHeight": "60vh",
        "resizableColumns": False,
        "index": "_id",
        "clipboard": True,
        "selectable": False,
        "clipboardPasteAction": ns("clipboardPasteAction"),
        "clipboardCopySelector": "table",
        "clipboardPasted": ns("clipboardPasted")
    },
    downloadButtonType={
        "css": "btn btn-primary",
        "text": "Download",
        "type": "csv"
    },
    theme='bootstrap/tabulator_bootstrap4',
)
layout=dbc.Row(dbc.Col([result_table]))

@app.callback([
    Output({
        "type": "table",
        "section": "apprenticeships",
        "page": "academic",
        "tab": "edit"
    }, "data"),
    Output({
        "type": "table",
        "page": "academic",
        "section": "apprenticeships",
        "tab": "edit"
    }, "columns"),
], [
    Input("apprenticeships-academic-store", "data"),
    Input({
        "type": "table",
        "section": "apprenticeships",
        "page": "academic",
        "tab": "edit"
    }, "cellEdited"),
    Input({
        "type": "table",
        "section": "apprenticeships",
        "page": "academic",
        "tab": "edit",
    }, "clipboardPasted")
]
)
def update_subject_table(store_data, changed, row_data):
    if not store_data:
        return [], []
    trigger = dash.callback_context.triggered[0].get("prop_id")
    # If we're here because a cell has been edited
    if "cellEdited" in trigger:
        pass
        # row = changed.get("row")
        # doc = data.get_doc(row.get("_id_x"))
        # doc.update({"grade": row.get("grade"), "comment": row.get("comment")})
        # data.save_docs([doc])
    elif "clipboardPasted" in trigger:
        pass
        # # If we're here because data has been pasted
        # assessment_docs = store_data.get("assessment_docs")
        # assessment_df = pd.DataFrame.from_records(assessment_docs)
        # try:
        #     pasted_df = pd.DataFrame.from_records(row_data)[[
        #         "student_id", "grade", "comment"
        #     ]]
        # except KeyError:
        #     pass
        #     # Silently fail if student_id, grade, and comment fields were not present
        # else:
        #     pasted_df = pasted_df.replace('\r', '', regex=True)
        #     merged_df = pd.merge(assessment_df, pasted_df, on="student_id")
        #     merged_df = merged_df.rename(columns={
        #         "grade_y": "grade",
        #         "comment_y": "comment"
        #     }).drop(["grade_x", "comment_x"], axis=1)
        #     merged_docs = merged_df.to_dict(orient='records')
        #     data.save_docs(merged_docs)

    columns = [
        {
            "title": "Student ID",
            "field": "student_id",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        },
        {
            "title": "Email",
            "field": "email",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        },
        {
            "title": "Instance",
            "field": "moduleCode",
            "width": "15%"
        },
        {
            "title": "Given name",
            "field": "given_name",
            "width": "20%"
        },
        {
            "title": "Family name",
            "field": "family_name",
            "width": "20%"
        },
        {
            "title": "Marks",
            "field": "total",
            "editor": "select",
            "editorParams": {
                "values": curriculum.scales.get('percentage')
            },
            "width": "15%"
        },
        {
            "title": "Class",
            "field": "class",
            "width": "15%"
        }
        # {
        #     "title": "Comment",
        #     "field": "comment",
        #     "editor": "textarea",
        #     "editorParams": {
        #         "verticalNavigation": "hybrid"
        #     },
        #     "formatter": "plaintext",
        # },
    ]
    return store_data.get("result_docs"), columns

