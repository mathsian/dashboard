import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_daq as daq
from datetime import date

from app import app
import data
import curriculum

# sort_dropdown = dcc.Dropdown(id='progress-sort-dropdown',
#                              options=[
#                                  {
#                                      'label': 'Alphabetical',
#                                      'value': 'alphabetical'
#                                  },
#                                  {
#                                      'label': 'Attendance',
#                                      'value': 'attendance'
#                                  },
#                                  {
#                                      'label': 'Progress',
#                                      'value': 'progress'
#                                  },
#                              ],
#                              value='Alphabetical')

layout = dbc.Container(dcc.Loading(html.Div(id='progress-content')))


@app.callback(Output('progress-content', 'children'), [
    Input('sixthform-pastoral-store', 'data'),
])
def update_progress_content(store_data):
    enrolment_docs = store_data.get('enrolment_docs')
    enrolment_df = pd.DataFrame.from_records(enrolment_docs, index='_id').sort_values(['family_name', 'given_name'])
    attendance_docs = store_data.get('attendance_docs')
    assessment_docs = store_data.get('assessment_docs')
    # Get docs in scope
    this_year_start = curriculum.this_year_start
    attendance_df = pd.DataFrame.from_records(attendance_docs).query(
        'subtype == "weekly" and date >= @this_year_start')
    # Group by student and create percentage
    grouped_df = attendance_df.groupby(by='student_id').sum()
    grouped_df.eval('percentage = 100 * actual / possible', inplace=True)
    # Pivot on grades to get profile
    assessment_df = pd.DataFrame.from_records(assessment_docs).sort_values(
        ['student_id', 'subject_code',
         'date']).set_index(['student_id', 'subject_code', 'assessment'])
    cards = []
    # A card for every student in scope
    for student_id in enrolment_df.index:
        # Get student's atttendance percentage
        student_attendance_row = grouped_df.loc[grouped_df.index.intersection(
            [student_id])]
        student_attendance = round(
            student_attendance_row['percentage'].squeeze())
        danger = low_attendance(student_attendance, 90)
        # And create list group
        student_attendance_listgroup = dbc.ListGroup([
            dbc.ListGroupItem('Attendance'),
            dbc.ListGroupItem(student_attendance)
        ])
        # Get student's assessment record
        student_assessment_record = assessment_df.loc[student_id]
        # List of unique subjects
        student_subjects = student_assessment_record.index.unique(0)
        # Start the list of popover list groups
        popover_listgroups = []
        # For every subject create a ListGroup
        for subject_code in student_subjects:
            # Set the heading to the subject code
            student_subject_listitems = [dbc.ListGroupItem(subject_code)]
            for student_assessment in student_assessment_record.loc[subject_code].index.unique(0):
                # Get their grade
                grade = student_assessment_record.loc[(subject_code,
                                                       student_assessment),
                                                      'grade']
                scale = student_assessment_record.loc[(subject_code,
                                                       student_assessment),
                                                      'subtype']
                danger = danger or low_grade(grade, scale)
                student_subject_listitems.append(
                    dbc.ListGroupItem(f'{student_assessment}\t{grade}'))
            # Add the assessments to the popover
            popover_listgroups.append(dbc.ListGroup(student_subject_listitems))
        full_name = f'{enrolment_df.loc[student_id]["given_name"]} {enrolment_df.loc[student_id]["family_name"]}'
        popover = dbc.Popover(
            target=f'sixthform-{student_id}',
            children=[
                dbc.PopoverHeader(
                    html.H5(full_name)),
                dbc.PopoverBody(popover_listgroups)
            ],
            trigger='legacy')
        cards.append(
            dbc.Card(
                id=f'sixthform-{student_id}',
                children=[
                    popover,
                    dbc.CardHeader(html.H5(full_name)),
                    dbc.CardBody(f'{student_attendance}% attendance')
                ],
                color=('danger' if danger else 'primary'),
                inverse=True))
    result = dbc.Row([
        dbc.Col(card, width=4, style={'margin-bottom': '10px'})
        for card in cards
    ],
                     align='center')
    return result


def low_grade(grade, scale):
    print(grade, scale)
    if scale == 'Expectations':
        return (grade == 'Below Expectations')
    elif scale == 'BTEC-Single':
        return (grade in ['U', 'NYP', 'N', 'P'])
    else:
        return (grade in ['U', 'E', 'D'])


def low_attendance(attendance, threshold):
    return (attendance < threshold)
