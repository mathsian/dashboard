"""
Layout and callbacks for student lists
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
from urllib.parse import parse_qs
from dashboard import app, get_db

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
    # A list of students answering given ids
    html.Ul(id='student-list'),
    # A table of students answering given ids
    # Single selectable, hidden id is student id
    dash_table.DataTable(id='student-table',
                         columns=[
                                  {"name": "Name", "id": "value"},
                         ],
                         row_selectable='single',
                         data=[]),
   # Rudimentary navigation
    html.Ul([
        html.Li(dcc.Link('Index', href='/')),
        html.Li(dcc.Link('Subject', href='/pages/subject'))
    ])
])

@app.callback(Output('student-list', 'children'),
              [Input('student-url', 'search'),
               Input('cohort-dropdown', 'value')])
def display_student_list(search, value):
    """Called on page load with url and on change to the cohort dropdown"""
    # search captures url parameters, including leading ?
    query_dict = parse_qs(search[1:])
    if 'id' in query_dict.keys():
        # if there is one or more id= then we want those ids
        records = get_students_by_id_list(query_dict['id'])
    elif type(value)==list:
        # get students in selected cohorts
        records = get_all_students(value)
    elif value:
        # get students in selected cohort
        records = get_all_students([value])
    else:
         records = []
    return [html.Li(dcc.Link(s['value'], href=f'/pages/report?id={s["id"]}')) for s in records]

def get_students_by_id_list(id_list):
    """Get student enrolment docs for ids in list"""
    db = get_db()
    selected_students = db.get_view_result(
        'enrolment',
        'student_id',
        keys=id_list,
        include_docs=True).all()
    return selected_students

def get_all_students(cohort_list):
    """Get all student enrolment docs"""
    db = get_db()
    return db.get_view_result(
        'enrolment',
        'cohort',
        keys=cohort_list,
        include_docs=True).all()

