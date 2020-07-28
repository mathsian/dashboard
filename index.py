"""
Owns top level tabs, dropdowns, and the storage of current context
"""
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from dashboard import app
from pages import report, student, subject, top

# Top level container
app.layout = html.Div([
    dcc.Store(id='current-student', storage_type='memory', data={}),
    html.Div(id='heading-content'),
    dcc.Tabs(id='top-tabs', value='cohort-tab',
             children=[
                 dcc.Tab(value='cohort-tab', label="Cohort"),
                 dcc.Tab(value='team-tab', label="Team"),
                 dcc.Tab(value='subject-tab', label="Subject"),
                 dcc.Tab(value='student-tab', label="Student")
             ]),
    html.Div(id='filters',
             children=[
                 html.Div(id='filter-cohort', children=[dcc.Dropdown(
                 id='cohort-dropdown',
                 options=[
                     {'label': 'Cohort 1618', 'value': '1618'},
                     {'label': 'Cohort 1719', 'value': '1719'},
                     {'label': 'Cohort 1820', 'value': '1820'},
                     {'label': 'Cohort 1921', 'value': '1921'},
                 ],
                 value='1921',
                 multi=True)]),

                 html.Div(id='filter-subject', children=[dcc.Dropdown(
                 id='subject-dropdown',
                 options=[
                     {'label': 'Maths', 'value': 'Maths'},
                     {'label': 'Business', 'value': 'Business'},
                     {'label': 'Graphics', 'value': 'Graphics'},
                     {'label': 'Computing', 'value': 'Computing'}
                 ],
                 value='Maths')]),
                 html.Div(id='filter-point', children=[dcc.Dropdown(
                 id='point-dropdown',
                 options=[
                     {'label': '12.1', 'value': '12.1'},
                     {'label': '12.2', 'value': '12.2'},
                     {'label': '12.3', 'value': '12.3'},
                     {'label': '13.1', 'value': '13.1'},
                     {'label': '13.2', 'value': '13.2'},
                     {'label': '13.3', 'value': '13.3'},
                 ],
                 value='13.3')]),
             ]),
    html.Div(id='top-tab-content')
])


@app.callback(Output('current-student', 'data'),
              [Input('student-list-student-table', 'selected_row_ids')],
              [State('current-student', 'data')])
def update_selected_student(row_ids, data):
    if row_ids:
        data['student_id'] = row_ids[0]
    return data


@app.callback(
    [Output('top-tab-content', 'children'),
     Output('filter-subject', 'hidden'),
     Output('filter-point', 'hidden')],
    [Input('top-tabs', 'value')])
def display_page(tab):
    response = top.layout, True, True
    if tab == 'student-tab':
        response = student.layout, True, True
    elif tab == 'subject-tab':
        response = subject.layout, False, False
    elif tab == 'top-tab':
        response = top.layout, True, True
    elif tab == 'team-tab':
        response = top.layout, True, True
    return response


if __name__ == '__main__':
    app.run_server(debug=True)
