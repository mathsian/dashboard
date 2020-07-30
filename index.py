"""
Owns top level tabs, dropdowns, and the storage of current context
"""
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from dashboard import app
from pages import report, student, subject, top
import curriculum


filters = [
    html.Div(id='filter-cohort', children=[dcc.Dropdown(
        id='cohort-dropdown',
        options=curriculum.cohorts['options'],
        value=curriculum.cohorts['default'],
        multi=True)]),
    html.Div(id='filter-subject', children=[dcc.Dropdown(
        id='subject-dropdown',
        options=curriculum.subjects['options'],
        value=curriculum.subjects['default'])]),
    html.Div(id='filter-point', children=[dcc.Dropdown(
        id='point-dropdown',
        options=curriculum.points['options'],
        value=curriculum.points['default'])]),
    html.Div(id='side-table-div')]

top_tabs = dcc.Tabs(id='top-tabs', value='cohort-tab',
                    children=[
                        dcc.Tab(value='cohort-tab', label="Cohort"),
                        dcc.Tab(value='team-tab', label="Team"),
                        dcc.Tab(value='subject-tab', label="Subject"),
                        dcc.Tab(value='student-tab', label="Student")
                    ])


# Top level container
app.layout = dbc.Container([
    dcc.Store(id='current-student', storage_type='memory', data={}),
    html.Div(id='heading-content'),
    dbc.Row([
        dbc.Col(filters, width=2, align='stretch'),
        dbc.Col([html.Div(top_tabs), html.Div(id='sub-tabs')])
    ]),
    dbc.Row(id='top-tab-content'),
    ], fluid=True)


@app.callback(Output('current-student', 'data'),
               [Input('student-list-student-table', 'selected_row_ids')],
               [State('current-student', 'data')])
def update_selected_student(row_ids, data):
    if row_ids:
        data['student_id'] = row_ids[0]
    return data


@app.callback(
    [Output('top-tab-content', 'children'),
     Output('sub-tabs', 'children'),
     Output('filter-subject', 'hidden'),
     Output('filter-point', 'hidden')],
    [Input('top-tabs', 'value')])
def display_page(tab):
    response = top.layout, [], True, True
    if tab == 'student-tab':
        response = student.layout, student.subtabs, True, True
    elif tab == 'subject-tab':
        response = subject.layout, subject.subtabs, False, False
    elif tab == 'top-tab':
        response = top.layout, [], True, True
    elif tab == 'team-tab':
        response = top.layout, [], True, True
    return response


if __name__ == '__main__':
    app.run_server(debug=True)
