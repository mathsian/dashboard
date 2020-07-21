"""
An individual student report
"""
from urllib.parse import parse_qs

import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from dashboard import app, db

layout = html.Div([
    # We need the id of the student from the url
    dcc.Location('report-url'),
    html.Div(id="report-heading"),
    html.Div(id="report-subheading"),
    html.H3("Attendance"),
    html.Div(id="report-attendance"),
    html.H3("Academic"),
    html.Div(id="report-academic"),
    html.H3("Pastoral"),
    html.H4("Kudos"),
    html.Div(id="report-kudos"),
    html.H4("Concerns"),
    html.Div(id="report-concerns"),
])

# One page load we extract student id from the url and populate all the sections of the report


@app.callback([Output('report-heading', 'children'),
               Output("report-subheading", "children"),
               Output("report-attendance", "children"),
               Output("report-academic", "children"),
               Output("report-kudos", "children"),
               Output("report-concerns", "children")],
              [Input('report-url', 'search')]
              )
def generate_report(search):
    # search captures url parameters, including leading ?
    query_dict = parse_qs(search[1:])
    if not 'id' in query_dict.keys():
        return html.P("No student requested"), [], [], [], [], []
    # parse_qs returns a list
    student_id = query_dict['id'][0]
    # The enrolment doc can be found just by doc id
    enrolment = db[student_id]
    heading_layout = html.H1(
        f'{enrolment["given_name"]} {enrolment["family_name"]}')

    # The other data we want as pandas dataframes
    # Assessment
    assessment_df = get_as_df("assessment", "student_id", student_id)
    assessment_layout = []
    # For each subject, graph grades against time
    for subject in assessment_df['subject'].unique():
        results = assessment_df.query(
            f'subject == "{subject}"').sort_values(by='date')
        assessment_layout.append(
            dcc.Graph(figure={
                'data': [go.Scatter(x=results['date'],
                                    y=results['grade'])],
                'layout': go.Layout(
                    title=subject,
                    yaxis={'categoryorder': "array",
                           'categoryarray': ['U', 'E', 'D', 'C', 'B', 'A', 'S']})
            }))
    # Kudos
    kudos_df = get_as_df("kudos", "student_id", student_id)
    kudos_layout = html.H4("Values circle goes here")

    # Concerns
    concerns_df = get_as_df("concern", "student_id", student_id)
    concerns_layout = dash_table.DataTable(
        columns=[{'name': "Date", 'id': 'date'},
                 {'name': "Category", 'id': 'category'},
                 {'name': "Comment", 'id': 'comment'}],
        data=concerns_df.to_dict(orient='records')
    )

    return (heading_layout, [], [],
            assessment_layout, kudos_layout, concerns_layout)


def get_as_df(ddoc, view, student_id):
    """Returns a pandas df.

    ddoc: The Design Document name
    view: The view name
    student_id: The student id (the id of the student's enrolment doc)
    """
    # We extract the doc from each view result
    records = list(map(lambda r: r['doc'],
                       db.get_view_result(
        ddoc,
        view,
        key=student_id,
        include_docs=True).all()))
    return pd.DataFrame.from_records(records)
 
