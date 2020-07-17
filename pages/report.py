"""
An individual student report
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
from urllib.parse import parse_qs
from dashboard import app, db
import pandas as pd
import plotly.graph_objs as go

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
    heading_layout = html.H1(f'{enrolment["given_name"]} {enrolment["family_name"]}')

    # The other data we want as pandas dataframes
    assessment_df = get_as_df("assessment", "student_id", student_id)
    assessment_layout = []
    for subject in assessment_df['subject'].unique():
        results = assessment_df.query(f'subject == "{subject}"').sort_values(by='date')
        assessment_layout.append(
            dcc.Graph(figure={
                'data': [go.Scatter(x=results['date'],
                                    y=results['grade'])],
                'layout': go.Layout(title=subject,
                yaxis={'categoryorder': "array", 'categoryarray': ['U','E','D','C','B','A','S']})
            }))

    kudos_df = get_as_df("kudos", "student_id", student_id)
    kudos_layout = html.H2("Values circle goes here")
    concerns_df = get_as_df("concern", "student_id", student_id)
    concerns_layout = dash_table.DataTable(
        columns=[{'name': "Date", 'id': 'date'},
                   {'name': "Category", 'id': 'category'},
                   {'name': "Comment", 'id': 'comment'}],
        data=concerns_df.to_dict(orient='records')
        )
    return heading_layout, [], [], assessment_layout, kudos_layout, concerns_layout

def get_as_df(ddoc, view, student_id):
    # We extract the doc from each view result
    records = list(map(lambda r: r['doc'],
                    db.get_view_result(
                        ddoc,
                        view,
                        key=student_id,
                        include_docs=True).all()))
    return pd.DataFrame.from_records(records)
