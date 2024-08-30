import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State
import dash_tabulator
import pandas as pd
from dateutil.utils import today

from app import app
import data
import curriculum

progress_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "section": "sixthform",
        "page": "pastoral",
        "tab": "progress"
    },
    options={
        "resizableColumns": False,
        # by default tabulator uses a period as a nested field separator. Disable this
        "nestedFieldSeparator": False,
        "layout": "fitDataTable",
        "height": "70vh",
        "clipboard": "copy",
        "initialSort": [{"column": "family_name", "dir": "asc"}, {"column": "given_name", "dir": "asc"}]
    },
    downloadButtonType={
        "css": "btn btn-primary",
        "text": "Download",
        "type": "csv"
    },
    theme='bootstrap/tabulator_bootstrap4',
)
layout = dbc.Container(dcc.Loading(progress_table))


@app.callback([
    Output({
        "type": "table",
        "section": "sixthform",
        "page": "pastoral",
        "tab": "progress"
    }, 'columns'),
    Output({
        "type": "table",
        "section": "sixthform",
        "page": "pastoral",
        "tab": "progress"
    }, 'data')
],
              [
    Input('sixthform-pastoral-store', 'data'),
])
def update_progress_content(store_data):
    student_ids = store_data.get('student_ids')
    enrolment_docs = store_data.get('enrolment_docs')
    enrolment_df = pd.DataFrame.from_records(enrolment_docs)[['_id', 'given_name', 'family_name']].sort_values(['family_name', 'given_name'])
    assessment_docs = data.get_data("assessment", "student_id", student_ids)
    tdy = today().isoformat()
    assessment_df = pd.DataFrame.from_records(assessment_docs).query('date <= @tdy').sort_values(['student_id', 'subject_name', 'assessment'])[['student_id', 'subject_code', 'assessment', 'grade']]
    assessment_df['category'] = assessment_df['subject_code'].apply(subject_category)
    cs_df = assessment_df.query('category == "Computer Science"').rename({'subject_code': 'Computer Science'}, axis=1).pivot(index=['student_id', 'Computer Science'], columns='assessment', values='grade').add_suffix("_cs").reset_index()
    ss_df = assessment_df.query('category == "Second subject"').rename({'subject_code': 'Second subject'}, axis=1).pivot(index=['student_id', 'Second subject'], columns='assessment', values='grade').add_suffix("_ss").reset_index()
    csss_df = pd.merge(left=cs_df, right=ss_df, how='left', on='student_id')
    merged_df = pd.merge(enrolment_df, csss_df, left_on='_id', right_on='student_id')
    attendance_docs = store_data.get('attendance_docs')
    this_year_start = curriculum.this_year_start
    attendance_df = pd.DataFrame.from_records(attendance_docs).query('subtype == "weekly"').query('date > @this_year_start')[['student_id', 'actual', 'possible']]
    attendance_df = attendance_df.groupby('student_id').sum().reset_index()
    attendance_df['attendance'] = attendance_df['actual'].div(attendance_df['possible']).mul(100).round().astype('int64', errors='ignore')
    merged_df = pd.merge(left=merged_df, right=attendance_df[['student_id', 'attendance']], how='left', on='student_id')
    columns=[
       {
            "title": "Given name",
            "field": "given_name",
            "headerFilter": True,
            "widthGrow": 2,
            "frozen": True
      },
        {
            "title": "Family name",
            "field": "family_name",
            "headerFilter": True,
            "widthGrow": 2,
            "frozen": True
        },
        {
            "title": "Student ID",
            "field": "student_id",
            "visible": False,
            "clipboard": "true",
            "download": "true"
        },
         {
            "title": "Attendance",
            "field": "attendance",
            "sorter": "number",
            "hozAlign": "right",
            "headerFilter": True,
            "headerFilterFunc": "<",
            "headerFilterPlaceholder": "Less than",
        }
    ]
    cs_columns = [{
            "title": "Computer Science",
            "field": "Computer Science",
            "headerFilter": True,
        }]
    cs_columns += [{
            "title": assessment[:-3],
            "field": assessment,
            "headerFilter": True,
        } for assessment in merged_df.columns if assessment.endswith('_cs')]
    ss_columns = [{
            "title": "Second subject",
            "field": "Second subject",
            "headerFilter": True,
    }]
    ss_columns += [{
            "title": assessment[:-3],
            "field": assessment,
            "headerFilter": True,
        } for assessment in merged_df.columns if assessment.endswith('_ss')]
    return columns+cs_columns+ss_columns, merged_df.to_dict(orient='records')


def subject_category(subject_code):
    if subject_code.startswith('CSC'):
        return 'Computer Science'
    elif subject_code.startswith('FMA') or subject_code.startswith('MAT-L3CE') or subject_code.startswith('ENG-L2GC'):
        return 'Third subject'
    elif subject_code.startswith('ADA'):
        return 'Ada Skills'
    else:
        return 'Second subject'

def low_grade(grade, scale):
    if scale == 'Expectations':
        return (grade == 'Below Expectations')
    elif scale == 'BTEC-Single':
        return (grade in ['U', 'NYP', 'N', 'P'])
    else:
        return (grade in ['U', 'E', 'D'])


def low_attendance(attendance, threshold):
    return (attendance < threshold)
