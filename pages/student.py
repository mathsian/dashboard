"""
Layout and callbacks for student lists
"""
from urllib.parse import parse_qs

import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State

from dashboard import app, get_db
from pages import report

layout = html.Div([
    html.Div(id='student-list-content',
             children=[dcc.Dropdown(
                 id='student-list-cohort-dropdown',
                 options=[
                     {'label': 'Cohort 1618', 'value': '1618'},
                     {'label': 'Cohort 1719', 'value': '1719'},
                     {'label': 'Cohort 1820', 'value': '1820'},
                     {'label': 'Cohort 1921', 'value': '1921'},
                 ],
                 value='1921',
                 multi=True),
                 dash_table.DataTable(id='student-list-student-table',
                                      columns=[
                                               {'name': 'Name', 'id': 'value'}],
                                      row_selectable='single',
                                      )]),
    html.Div(id='student-list-student-report', children=report.layout)
])


@app.callback(Output('student-list-student-table', 'data'),
              [Input('student-list-cohort-dropdown', 'value')])
def display_student_list(value):
    if type(value) == list:
        return get_cohort_students(value)
    else:
        return get_cohort_students([value])


@app.callback(Output('current-focus', 'data'),
              [Input('student-list-student-table', 'selected_row_ids')],
[State('current-focus', 'data')])
def show_student_report(row_ids, focus):
    if row_ids:
        student_id = row_ids[0]
        focus['student_id'] = student_id
    return focus


def get_cohort_students(cohort_list):
    """Get all student enrolment docs"""
    db = get_db()
    return db.get_view_result(
        'enrolment',
        'cohort',
        keys=cohort_list,
        include_docs=True).all()
