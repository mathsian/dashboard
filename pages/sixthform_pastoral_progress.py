import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_daq as daq
from datetime import date

from app import app
import data
import curriculum

sort_dropdown = dcc.Dropdown(id='progress-sort-dropdown',
                             options=[
                                 {'label': 'Alphabetical', 'value': 'alphabetical'},
                                 {'label': 'Attendance', 'value': 'attendance'},
                                 {'label': 'Progress', 'value': 'progress'},
                             ],
                             value='Alphabetical')

layout = dbc.Row(
    [
    dbc.Col(id='progress-content'),
    dbc.Col(sort_dropdown, width=2)
    ]
)


@app.callback(
    Output('progress-content', 'children'),
    [
        Input('progress-sort-dropdown', 'value'),
        Input('sixthform-pastoral', 'data'),
    ]
)
def update_progress_content(sort_value, store_data):
    enrolment_docs = store_data.get('enrolment_docs')
    enrolment_df = pd.DataFrame.from_records(enrolment_docs, index='_id')
    student_ids = store_data.get('student_ids')
    attendance_docs = store_data.get('attendance_docs')
    assessment_docs = store_data.get('assessment_docs')
    # Get docs in scope
    this_year_start = curriculum.this_year_start
    attendance_df = pd.DataFrame.from_records(attendance_docs).query('subtype == "weekly" and date >= @this_year_start')
    # Group by student and create percentage
    grouped_df = attendance_df.groupby(by='student_id').sum()
    grouped_df.eval('percentage = 100 * actual / possible', inplace=True)
    # Pivot on grades to get profile
    assessment_df = pd.DataFrame.from_records(assessment_docs)
    assessment_pivot = pd.pivot_table(assessment_df, values='assessment', columns='grade', index='student_id', aggfunc='count', fill_value=0)
    cards = []
    # A card for every student in scope
    for s in enrolment_docs:
        student_id = s.get("_id")
        # Get student's atttendance percentage
        student_attendance_row = grouped_df.loc[grouped_df.index.intersection([student_id])]
        student_attendance = round(student_attendance_row['percentage'].squeeze())
        danger = low_attendance(student_attendance, 90)
        # And create list group
        student_attendance_listgroupitem = dbc.ListGroupItem([dbc.ListGroupItemHeading('Attendance'), dbc.ListGroupItemText(student_attendance)])
        # Get student's assessment record, alphabetical by subject, and date order
        student_assessment_record = assessment_df.query('student_id == @student_id').sort_values(['subject_code', 'date']).set_index(['subject_code', 'assessment'])
        # List of unique subjects
        student_subjects = student_assessment_record.index.unique(0)
        # For every subject create a ListGroup
        student_subject_list = []
        for subject_code in student_subjects:
            # Set the heading to the subject code
            student_subject_itemheading = dbc.ListGroupItemHeading(subject_code)
            # For every assessment in that subject
            assessment_list = []
            for student_assessment in student_assessment_record.loc[subject_code].index.unique(0):
                # Get their grade
                grade = student_assessment_record.loc[(subject_code, student_assessment), 'grade']
                scale = student_assessment_record.loc[(subject_code, student_assessment), 'subtype']
                # And add a text item
                assessment_list.append(dbc.ListGroupItemText(f'{student_assessment}\t{grade}'))
                danger = danger or low_grade(grade, scale)
                student_subject_list.append(dbc.ListGroupItem(children=[student_subject_itemheading] + assessment_list))
                popover_content = [dbc.ListGroup(student_attendance_listgroupitem), dbc.ListGroup(student_subject_list)]
                popover = dbc.Popover(target=f'sixthform-{student_id}',
                                      children=[
                                          dbc.PopoverHeader(html.H5(f'{s.get("given_name")} {s.get("family_name")}')),
                                          dbc.PopoverBody(popover_content)
                                      ],
                                      trigger='legacy')
        cards.append(dbc.Card(id=f'sixthform-{student_id}',
                                    children=[
                                        popover,
                                        dbc.CardHeader(html.H5(f'{s.get("given_name")} {s.get("family_name")}')),
                                        dbc.CardBody(f'{student_attendance}% attendance')
                                    ], color=('danger' if danger else 'primary'), inverse=True))
    result = dbc.Row([dbc.Col(card, width=4, style={'margin-bottom': '10px'}) for card in cards], align='center')
    return result


def low_grade(grade, scale):
    if scale == 'Expectations':
        return (grade == 'Below Expectations')
    elif scale == 'BTEC-Single':
        return (grade in ['U', 'NYP', 'N', 'P'])
    else:
        return (grade in ['U', 'E', 'D'])

def low_attendance(attendance, threshold):
    return (attendance < threshold)
