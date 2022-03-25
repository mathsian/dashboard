from flask import request
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
import app_data
import plotly.graph_objects as go
import curriculum
from dash_extensions.javascript import Namespace

ns = Namespace("myNameSpace", "tabulator")

subject_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "academic",
        "tab": "edit"
    },
    options={
        "placeholder": "Select a subject",
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
layout=dbc.Row(dbc.Col([subject_table]))

@app.callback([
    Output({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "data"),
    Output({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "columns"),
], [
    Input("sixthform-academic-store", "data"),
    Input({
        "type": "table",
        "page": "academic",
        "tab": "edit"
    }, "cellEdited"),
    Input({
        "type": "table",
        "page": "academic",
        "tab": "edit",
    }, "clipboardPasted")
],
              [
                  State("subject-dropdown", "label"),
              ]
)
def update_subject_table(store_data, changed, row_data, cohort):
    if not store_data:
        return [], []
    assessment_subject_cohort = store_data.get("assessment_subject_cohort")
    trigger = dash.callback_context.triggered[0].get("prop_id")
    permissions = app_data.get_permissions(request.headers.get("X-Email"))
    # If we're here because a cell has been edited
    if "cellEdited" in trigger and permissions.get("can_edit_sf"):
        row = changed.get("row")
        doc = data.get_doc(row.get("_id_x"))
        doc.update({"grade": row.get("grade"), "comment": row.get("comment")})
        data.save_docs([doc])
    elif "clipboardPasted" in trigger and permissions.get("can_edit_sf"):
        # If we're here because data has been pasted
        assessment_docs = data.get_data("assessment", "assessment_subject_cohort",
                                    [assessment_subject_cohort])
        assessment_df = pd.DataFrame.from_records(assessment_docs)
        try:
            pasted_df = pd.DataFrame.from_records(row_data)[[
                "student_id", "grade", "comment"
            ]]
        except KeyError:
            pass
            # Silently fail if student_id, grade, and comment fields were not present
        else:
            pasted_df = pasted_df.replace('\r', '', regex=True)
            merged_df = pd.merge(assessment_df, pasted_df, on="student_id")
            merged_df = merged_df.rename(columns={
                "grade_y": "grade",
                "comment_y": "comment"
            }).drop(["grade_x", "comment_x"], axis=1)
            merged_docs = merged_df.to_dict(orient='records')
            data.save_docs(merged_docs)
    assessment_docs = data.get_data("assessment", "assessment_subject_cohort",
                                    [assessment_subject_cohort])
    assessment_df = pd.DataFrame.from_records(assessment_docs)
    enrolment_df = pd.DataFrame.from_records(store_data.get("enrolment_docs"))
    merged_df = pd.merge(assessment_df,
                         enrolment_df,
                         left_on='student_id',
                         right_on='_id',
                         how='inner').sort_values(by=["family_name", "given_name"])
    subtype = merged_df.iloc[0]["subtype"]
    if permissions.get("can_edit_sf"):
        grade_editor = "select" if not subtype == 'Percentage' else "number"
        comment_editor = "textarea"
    else:
        grade_editor = False
        comment_editor = False
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
            "field": "student_email",
            "visible": False,
            "clipboard": "true",
            "download": "true"
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
            "title": "Grade",
            "field": "grade",
            "editor": grade_editor,
            "editorParams": {
                "values": curriculum.scales.get(subtype)
            } if subtype != 'Percentage' else {"max": 100, "min": 0, "step": 1},
            "width": "15%"
        },
        {
            "title": "Comment",
            "field": "comment",
            "editor": comment_editor,
            "editorParams": {
                "verticalNavigation": "hybrid"
            },
            "formatter": "plaintext",
        },
    ]
    return merged_df.to_dict(orient='records'), columns

