import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import curriculum
from dashboard import app, get_db

subtabs = dcc.Tabs(id='subject-tabs', value='view',
             children=[dcc.Tab(value='view', label='View'),
                       dcc.Tab(value='edit', label='Edit')])
subject_graph_div = dbc.Container(id='subject-graph-div', children=[dcc.Graph(id='subject-graph')])
subject_table_div = dbc.Container(id='subject-table-div',
             children=[dash_table.DataTable(id='subject-table',
                                            columns=[{'name': 'Given name', 'id': 'given_name'},
                                                     {'name': 'Family name', 'id': 'family_name'},
                                                     {'name': 'Grade', 'id': 'grade'}])])

layout = dbc.Col([
    dbc.Row([dbc.Col(subject_table_div, width=2),
             dbc.Col(dbc.Container(subject_graph_div))])
    ])

@app.callback(
    [Output('subject-graph', 'figure'),
     Output('subject-table', 'data')],
    [Input('cohort-dropdown', 'value'),
     Input('subject-dropdown', 'value'),
     Input('point-dropdown', 'value')])
def update_figure(cohort_values, subject_value, point_value):
    db = get_db()
    if type(cohort_values) != list:
        cohort_values = [cohort_values]
    assessments = [r['doc'] for r in db.get_view_result(
        'assessment', 'subject', key=subject_value, include_docs=True).all()]
    assessments_df = pd.DataFrame.from_records(assessments)
    students = [r['doc'] for r in db.get_view_result(
        'enrolment', 'cohort', keys=cohort_values, include_docs=True).all()]
    students_df = pd.DataFrame.from_records(students)
    df = assessments_df.merge(students_df, how='inner', left_on='student_id',
                              right_on='_id').query(f'point == "{point_value}"')
    figure = {
        'data': [
            go.Scatter(x=df['aps'],
                       y=df['grade'],
                       text=df['given_name'],
                       mode='markers')
        ],
        'layout':
            go.Layout(
                yaxis={'categoryorder': "array", 'categoryarray': curriculum.scales[subject_value]},
                hovermode='closest',
                title=f'Cohort {cohort_values} | {subject_value} | {point_value}'
        )
    }
    return figure, df.to_dict(orient='records')


@app.callback(
[Output('subject-table-div', 'hidden'),
 Output('subject-graph-div', 'hidden')],
[Input('subject-tabs', 'value')])
def show_subject_divs(value):
    if value == 'edit':
        return False, True
    else:
        return True, False
