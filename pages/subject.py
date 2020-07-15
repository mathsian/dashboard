from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import dash_table
from dashboard import app, students_df, assessments_df

layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id='subject-dropdown',
            options=[
                {'label': 'Maths', 'value': 'Maths'},
                {'label': 'Business', 'value': 'Business'},
                {'label': 'Graphics', 'value': 'Graphics'}
            ],
            value='Maths'),
        dcc.Dropdown(
            id='point-dropdown',
            options=[
                {'label': '12.1', 'value': '12.1'},
                {'label': '12.2', 'value': '12.2'},
                {'label': '12.3', 'value': '12.3'},
                {'label': '13.1', 'value': '13.1'},
                {'label': '13.2', 'value': '13.2'},
                {'label': '13.3', 'value': '13.3'},
            ],
            value='13.3'),
        dcc.Dropdown(
            id='cohort-dropdown',
            options=[
                {'label': 'Cohort 1618', 'value': '1618'},
                {'label': 'Cohort 1719', 'value': '1719'},
                {'label': 'Cohort 1820', 'value': '1820'},
                {'label': 'Cohort 1921', 'value': '1921'},
            ],
            value='1921'),
        html.Div(id='output-container'),
        html.Div([dcc.Graph(id='cohort-graph')]),
        ])
])


# A quick callback to make sure the dropdown is working
@app.callback(
    Output('output-container', 'children'),
    [Input('cohort-dropdown', 'value'),
     Input('subject-dropdown', 'value'),
     Input('point-dropdown', 'value')])
def update_output(cohort_value, subject_value, point_value):
    return 'You selected {}, subject {}, cohort {}'.format(
        point_value, subject_value, cohort_value)


@app.callback(
    Output('cohort-graph', 'figure'),
    [Input('cohort-dropdown', 'value'),
     Input('subject-dropdown', 'value'),
     Input('point-dropdown', 'value')])
def update_figure(cohort_value, subject_value, point_value):
    filtered_ass_df = assessments_df.loc[(assessments_df.point == point_value) & (assessments_df.subject == subject_value)]
    graph_data = filtered_ass_df.join(students_df[students_df.cohort == cohort_value],
                                      on='id', how='inner',
                                      lsuffix='_assessments',
                                      rsuffix='_students')
    return {
        'data': [
            go.Scatter(x=graph_data.aps,
                       y=graph_data.grade,
                       text=graph_data.full_name,
                       mode='markers')
        ],
        'layout':
            go.Layout(
                yaxis={'categoryorder': "array", 'categoryarray': ['U','E','D','C','B','A','S']},
                hovermode='closest',
                title=f'Cohort {cohort_value} | {subject_value} | {point_value}'
            )
        }
