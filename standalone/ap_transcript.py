from datetime import date
import jinja2
# from jinja2 import Template
import pandas as pd
import numpy as np
import sys
import os
# sys.path.append('..')
import app_data
from icecream import ic

TEMPLATE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '../templates'
)


latex_jinja_env = jinja2.Environment(
    variable_start_string='\VAR{',
    variable_end_string='}',
    line_statement_prefix='%%',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.FileSystemLoader(TEMPLATE_PATH)
)


def get_class(mark):
    if mark >= 69.5:
        return 'Distinction'
    elif mark >= 59.5:
        return 'Merit'
    elif mark >= 39.5:
        return 'Pass'
    else:
        return 'Fail'


def populate_template(student_id, levels=(4, 5, 6)):
    if isinstance(student_id, str):
        student_id = int(student_id)
    student_dict = app_data.get_student_by_id(student_id)
    results_dict = app_data.get_passing_results_for_student(student_id)
    results_df = pd.DataFrame.from_records(results_dict).query('Level in @levels')
    results_df['Class'] = results_df['Mark'].apply(lambda t: get_class(t))
    results_df.sort_values(by=['Level', 'Module'], inplace=True)
    top_up = student_dict.get("top_up")
    degree = student_dict.get("degree")
    if top_up:
        overall = app_data.round_normal(results_df.query('Level == 6')['Mark'].mean())
    else:
        overall = app_data.round_normal(results_df['Mark'].mean())
    if overall == '-':
        overall_class = ''
    else:
        overall_class = get_class(overall)
    overall_credits = results_df['Credits'].sum()
    if degree == 'Foundation Degree' and overall_credits >= 240:
        degree_status = 'Completed'
    elif degree == 'BSc' and overall_credits >= 360:
        degree_status = 'Completed'
    elif top_up and overall_credits >= 120:
        degree_status = 'Completed'
    else:
        degree_status = 'Not completed'

    template = latex_jinja_env.get_template('ap_transcript.tex')
    full_name = student_dict.get('transcript_name') or f'{student_dict.get("given_name")} {student_dict.get("family_name")}'
    programme = f'{student_dict.get("degree")} {student_dict.get("title")}'
    with open("latex/{} {}.tex".format(student_id, full_name), 'w') as f:
        template_data = {"student_name": full_name,
                         "student_id": student_id,
                         "issued": date.today(),
                         "programme": programme,
                         "status": degree_status,
                         "modules": results_df.to_dict(orient='records'),
                         "top_up": top_up,
                         "start_date": student_dict.get("start_date"),
                         "end_date": student_dict.get("end_date"),
                         "overall": overall,
                         "overall_class": overall_class,
                         "overall_credits": overall_credits
                         }
        f.write(template.render(template_data))


def cohort(cohort_name):
    for s in app_data.get_students_by_cohort_name(cohort_name):
        populate_template(s.get("student_id"))


if __name__ == "__main__":
    pass
