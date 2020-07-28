from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import dash_table
from dashboard import get_db, app

layout = html.Div([
    html.Div([
        html.Div([dcc.Graph(id='cohort-graph')]),
        ])
])


@app.callback(
    Output('cohort-graph', 'figure'),
    [Input('cohort-dropdown', 'value'),
     Input('subject-dropdown', 'value'),
     Input('point-dropdown', 'value')])
def update_figure(cohort_value, subject_value, point_value):
    db = get_db()
    assessments = [r['doc'] for r in db.get_view_result('assessment', 'subject', key=subject_value, include_docs=True).all()]
    assessments_df = pd.DataFrame.from_records(assessments)
    students = [r['doc'] for r in db.get_view_result('enrolment', 'cohort', key=cohort_value, include_docs=True).all()]
    students_df = pd.DataFrame.from_records(students)
    df = assessments_df.merge(students_df, how='left', left_on='student_id', right_on='_id').query(f'point == "{point_value}"')
    figure = {
        'data': [
            go.Scatter(x=df['aps'],
                       y=df['grade'],
                       text=df['given_name'],
                       mode='markers')
        ],
        'layout':
            go.Layout(
                yaxis={'categoryorder': "array", 'categoryarray': ['U','E','D','C','B','A','S']},
                hovermode='closest',
                title=f'Cohort {cohort_value} | {subject_value} | {point_value}'
            )
        }
    return figure
