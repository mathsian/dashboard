import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table
from urllib.parse import parse_qs
from dashboard import app, students_df, assessments_df

layout = html.Div([
    dcc.Location('student-url'),
    html.P("Testing student view."),
    dash_table.DataTable(id='student-table',
                         columns=[{"name": "id", "id": "id"},
                                  {"name": "Given Name", "id": "given_name"},
                                  {"name": "Family Name", "id": "family_name"},
                         ],
                         row_selectable='single',
                         data=[]),
    html.P("Report"),
    dash_table.DataTable(id='student-report-table',
                         columns=[
                                  {"name": "Subject", "id": "subject"},
                                  {"name": "Assessment", "id": "point"},
                                  {"name": "Grade", "id": "grade"},
                         ],
                         data=[]),
    html.Ul([
        html.Li(dcc.Link('Index', href='/')),
        html.Li(dcc.Link('Subject', href='/pages/subject'))
    ])
])

@app.callback(Output('student-table', 'data'),
              [Input('student-url', 'search')])
def display_student(search):
    query_dict = parse_qs(search[1:])
    if 'id' in query_dict.keys():
        # parse_qs will give a list of strings
        # we want integers
        id_list = list(map(int, filter(lambda i: i.isdigit(), query_dict['id'])))
        response = get_students_by_id_list(id_list)
    elif 's' in query_dict.keys():
        response = get_students_by_name(query_dict["s"][0])
    return response


def get_students_by_id_list(id_list):
    selected_students = students_df.loc[students_df.id.isin(id_list)]
    return selected_students.to_dict(orient='records')

def get_students_by_name(name):
    selected_students = students_df.loc[(students_df.given_name.str.contains(name)) | (students_df.family_name.str.contains(name))]
    return selected_students.to_dict(orient='records')


@app.callback(Output('student-report-table', 'data'),
              [Input('student-table', 'selected_row_ids')])
def update_student_report(rows):
    row = rows[0] if rows else None
    student_assessments = assessments_df.loc[assessments_df.id == row].sort_values(by=['subject', 'point'])
    return student_assessments.to_dict(orient='records')
