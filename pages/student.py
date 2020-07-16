"""
Layout and callbacks for student oriented data
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
from urllib.parse import parse_qs
from dashboard import app, db

layout = html.Div([
    # The url at which the page is being served. Useful to pick up parameters
    dcc.Location('student-url'),
    html.P("Testing student view."),
    dcc.Dropdown(
            id='cohort-dropdown',
            options=[
                {'label': 'Cohort 1618', 'value': '1618'},
                {'label': 'Cohort 1719', 'value': '1719'},
                {'label': 'Cohort 1820', 'value': '1820'},
                {'label': 'Cohort 1921', 'value': '1921'},
            ],
            value='1921',
        multi=True),
    # A table of students answering given ids
    dash_table.DataTable(id='student-table',
                         columns=[
                                  {"name": "Name", "id": "value"},
                         ],
                         row_selectable='single',
                         data=[]),
    html.P("Report"),
    # The academic data for the student selected above
    dash_table.DataTable(id='student-report-table',
                         columns=[
                                  {"name": "Subject", "id": "subject"},
                                  {"name": "Assessment", "id": "point"},
                                  {"name": "Grade", "id": "grade"},
                         ],
                         data=[]),
    # Rudimentary navigation
    html.Ul([
        html.Li(dcc.Link('Index', href='/')),
        html.Li(dcc.Link('Subject', href='/pages/subject'))
    ])
])

@app.callback(Output('student-table', 'data'),
              [Input('student-url', 'search'),
               Input('cohort-dropdown', 'value')])
def display_student_list(search, value):
    """Called on page load with url and on change to the cohort dropdown"""
    # search captures url parameters, including leading ?
    query_dict = parse_qs(search[1:])
    if 'id' in query_dict.keys():
        # if there is one or more id= then we want those ids
        response = get_students_by_id_list(query_dict['id'])
    elif type(value)==list:
        # get students in selected cohorts
        response = get_all_students(value)
    elif value:
        # get students in selected cohort
        response = get_all_students([value])
    else:
        response = []
    return response

def get_students_by_id_list(id_list):
    """Get student enrolment docs for ids in list"""
    selected_students = db.get_view_result(
        'enrolment',
        'student_id',
        keys=id_list,
        include_docs=True).all()
    return selected_students

def get_all_students(cohort_list):
    """Get all student enrolment docs"""
    return db.get_view_result(
        'enrolment',
        'cohort',
        keys=cohort_list,
        include_docs=True).all()

@app.callback(Output('student-report-table', 'data'),
              [Input('student-table', 'selected_row_ids')])
def update_student_report(rows):
    """Called when a row is selected"""
    if rows:
        row = rows[0]
        # row is the student id because datatable uses id field from records as row_ids
        student_assessments = db.get_view_result(
            'assessment',
            'student_id',
            key=row,
            include_docs=True).all()
        return [record['doc'] for record in student_assessments]
    else:
        return []
