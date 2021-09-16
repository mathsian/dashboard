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

subject_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "academic",
        "tab": "edit"
    },
    options={
        "maxHeight": "60vh",
        "placeholder": "Select a subject",
        "resizableColumns": False,
        "index": "_id",
        "layout": "fitDataStretch",
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
    Input("assessment-dropdown", "label"),
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
                  State("academic-cohort-dropdown", "label"),
                  State("subject-dropdown", "label"),
              ]
)
def update_subject_table(assessment_name, changed, row_data, cohort, subject_code):
    # If the user hasn't selected a subject/assessment yet
    if not assessment_name:
        return [], []
    trigger = dash.callback_context.triggered[0].get("prop_id")
    # If we're here because a cell has been edited
    if "cellEdited" in trigger:
        row = changed.get("row")
        doc = data.get_doc(row.get("_id_x"))
        doc.update({"grade": row.get("grade"), "comment": row.get("comment")})
        data.save_docs([doc])
    elif "clipboardPasted" in trigger:
        # If we're here because data has been pasted
        assessment_docs = data.get_data(
            "assessment", "assessment_subject_cohort",
            [(assessment_name, subject_code, cohort)])
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
                                    [(assessment_name, subject_code, cohort)])
    assessment_df = pd.DataFrame.from_records(assessment_docs).sort_values(
        by='student_id')
    student_ids = assessment_df["student_id"].tolist()
    enrolment_df = pd.DataFrame.from_records(
        data.get_data("enrolment", "_id", student_ids))
    merged_df = pd.merge(assessment_df,
                         enrolment_df,
                         left_on='student_id',
                         right_on='_id',
                         how='inner')
    subtype = merged_df.iloc[0]["subtype"]
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
            "editor": "select",
            "editorParams": {
                "values": curriculum.scales.get(subtype)
            },
            "width": "15%"
        },
        {
            "title": "Comment",
            "field": "comment",
            "editor": "textarea",
            "editorParams": {
                "verticalNavigation": "hybrid"
            },
            "formatter": "plaintext",
        },
    ]
    return merged_df.to_dict(orient='records'), columns

