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

blank_figure = {'layout': {'xaxis': {'visible': False}, 'yaxis': {'visible': False}}}
ns = Namespace("myNameSpace", "tabulator")
single_report_attendance = dbc.AccordionItem([
    html.H5(children=[html.Span(
        id={
            "section": "sixthform",
            "type": "text",
            "page": "student",
            "tab": "report",
            "name": "attendance"
        }), "% attendance"]),
    dcc.Graph(id={
        "section": "sixthform",
        "type": "graph",
        "page": "student",
        "tab": "report",
        "name": "attendance"
    },
              figure=blank_figure,
              config={"displayModeBar": False}),
    html.Div(id={
        "section": "sixthform",
        "type": "table",
        "page": "student",
        "tab": "report",
        "name": "attendance"
    })
],
                                             title="Attendance")
single_report_academic = dbc.AccordionItem([
    html.Div(
        id={
            "section": "sixthform",
            "type": "text",
            "page": "student",
            "tab": "report",
            "name": "academic"
        }),
],
                                           title="Academic")
single_report_kudos = dbc.AccordionItem([
    html.Div(
        dash_table.DataTable(
            id={
                "section": "sixthform",
                "type": "table",
                "page": "student",
                "tab": "report",
                "name": "kudos"
            },
            columns=[
                {
                    "name": "Value",
                    "id": "ada_value"
                },
                {
                    "name": "Points",
                    "id": "points"
                },
                {
                    "name": "For",
                    "id": "description"
                },
                {
                    "name": "From",
                    "id": "from"
                },
                {
                    "name": "Date",
                    "id": "date"
                },
            ],
            sort_by=[{"column_id": "date", "direction": "desc"}],
            style_header={
                "textAlign": "left",
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0
                },
            sort_action='native',
            style_data={
                "textAlign": "left",
                "height": "auto",
                "whiteSpace": "normal",
            },
        ))
],
                                        title="Kudos")

# single_report_concerns = dbc.AccordionItem([
#     html.Div(
#         dash_table.DataTable(
#             id={
#                 "section": "sixthform",
#                 "type": "table",
#                 "page": "student",
#                 "tab": "report",
#                 "name": "concern"
#             },
#             columns=[
#                 {
#                     "name": "Date",
#                     "id": "date"
#                 },
#                 {
#                     "name": "Category",
#                     "id": "category"
#                 },
#                 {
#                     "name": "Description",
#                     "id": "description"
#                 },
#                 {
#                     "name": "Raised by",
#                     "id": "from"
#                 },
#                 {
#                     "name": "Additional",
#                     "id": "discrimination"
#                 },
#             ],
#             sort_by=[{"column_id": "date", "direction": "desc"}],
#             sort_action='native',
#             style_header={
#                 "textAlign": "left",
#         'overflow': 'hidden',
#         'textOverflow': 'ellipsis',
#         'maxWidth': 0
#                 },
#              style_data={
#                 "textAlign": "left",
#                 "height": "auto",
#                 "whiteSpace": "normal",
#             },
#         ))
# ],
#                                            title="Concerns")

single_report = dbc.Accordion([
    single_report_attendance, single_report_academic, single_report_kudos,
#    single_report_concerns
], start_collapsed=True)

layout = html.Div([
    html.H3(
        id={
            "section": "sixthform",
            "type": "text",
            "page": "student",
            "tab": "report",
            "name": "heading"
        }), single_report
])


@app.callback([
    Output(
        {
            "section": "sixthform",
            "type": "text",
            "page": "student",
            "tab": "report",
            "name": "heading"
        }, "children"),
   Output(
        {
            "section": "sixthform",
            "type": "text",
            "page": "student",
            "tab": "report",
            "name": "attendance"
        }, "children"),
    Output(
        {
            "section": "sixthform",
            "type": "graph",
            "page": "student",
            "tab": "report",
            "name": "attendance"
        }, "figure"),
    Output(
        {
            "section": "sixthform",
            "type": "table",
            "page": "student",
            "tab": "report",
            "name": "attendance"
        }, "children"),
    Output(
        {
            "section": "sixthform",
            "type": "text",
            "page": "student",
            "tab": "report",
            "name": "academic"
        }, "children"),
    Output(
        {
            "section": "sixthform",
            "type": "table",
            "page": "student",
            "tab": "report",
            "name": "kudos"
        }, "data"),
#     Output(
#         {
#             "section": "sixthform",
#             "type": "table",
#             "page": "student",
#             "tab": "report",
#             "name": "concern"
#         }, "data"),
], [Input("sixthform-selected-store", "data")])
def update_student_report(store_data):
    if not store_data:
        return "Select a student to view their report", "", blank_figure, [], [], []
    student_id = store_data[-1]
    enrolment_doc = data.get_student(student_id)
    heading = f'{enrolment_doc.get("_id")} {enrolment_doc.get("given_name")} {enrolment_doc.get("family_name")}'
    assessment_docs = data.get_data("assessment", "student_id", student_id)
    assessment_children = []
    if len(assessment_docs) > 0:
        assessment_df = pd.DataFrame.from_records(assessment_docs).set_index(
            ['subject_name', 'assessment']).query("report != 2")
        for subject_name in assessment_df.index.unique(level=0):
            assessment_children.append(html.H4(subject_name))
            for assessment in assessment_df.loc[subject_name].index.unique():
                assessment_children.append(html.H5(assessment))
                results = assessment_df.query(
                    "subject_name == @subject_name and assessment == @assessment"
                )
                for result in results.to_dict(orient='records'):
                    assessment_children.append(result.get("grade", ""))
                    assessment_children.append(
                        html.Blockquote(result.get("comment", "")))
    kudos_docs = data.get_data("kudos", "student_id", student_id)
    # concern_docs = data.get_data("concern", "student_id", student_id)
    attendance_docs = data.get_data("attendance", "student_id", student_id)
    attendance_df = pd.DataFrame.from_records(attendance_docs).query(
        "subtype == 'weekly'")
    attendance_df['percent'] = round(100 * attendance_df['actual'] /
                                     attendance_df['possible'])
    attendance_year = round(100 * attendance_df['actual'].sum() /
                            attendance_df['possible'].sum())
    attendance_figure = go.Figure()
    attendance_figure.add_trace(
        go.Bar(x=attendance_df["date"],
               y=attendance_df["percent"],
               name="Weekly attendance"))
    notes_docs = data.get_data("note", "student_id", student_id)
    notes_df = pd.DataFrame.from_records(notes_docs, columns=['date', 'category', 'comment'])
    notes_df = notes_df.rename({'date': 'Date', 'category': 'Category', 'comment': 'Comment'}, axis='columns').sort_values('Date', ascending=False)
    notes_table = dbc.Table.from_dataframe(notes_df)
    # return heading, attendance_year, attendance_figure, assessment_children, kudos_docs, concern_docs
    return heading, attendance_year, attendance_figure, notes_table, assessment_children, kudos_docs
