"""
Layout and callbacks for student lists
"""
from urllib.parse import parse_qs

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
from dash.dependencies import Input, Output, State

from dashboard import app, get_db
from pages import report

layout = [
    dbc.Col(id='student-list-div',
             children=[
                 dash_table.DataTable(id='student-list-student-table',
                                      columns=[
                                               {'name': 'Name', 'id': 'value'}],
                                      row_selectable='single',
                                      )], width=2),
    dbc.Col(id='student-list-student-report',
            children=report.layout, width=True)
]


@app.callback(Output('student-list-student-table', 'data'),
              [Input('cohort-dropdown', 'value')])
def display_student_list(value):
    if type(value) == list:
        return get_cohort_students(value)
    else:
        return get_cohort_students([value])


def get_cohort_students(cohort_list):
    """Get all student enrolment docs"""
    db = get_db()
    return db.get_view_result(
        'enrolment',
        'cohort',
        keys=cohort_list,
        include_docs=True).all()
