from datetime import date
import jinja2
import pandas as pd
import numpy as np
import sys
import os
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
        return ''


def populate_template(student_id, **kwargs):
    if isinstance(student_id, str):
        student_id = int(student_id)
    student_dict = app_data.get_student_by_id(student_id)
    ic(student_dict)
    results_dict = app_data.get_passing_results_for_student(student_id)
    rpl = app_data.get_rpl_for_student(student_id)
    if rpl:
        results_dict.extend(rpl)

    top_up = kwargs.get("top_up", student_dict.get("top_up"))
    degree = kwargs.get("degree", student_dict.get("degree"))
    start_date = kwargs.get("start_date", student_dict.get("start_date"))
    end_date = kwargs.get("end_date", student_dict.get("end_date"))
    end_date = end_date if end_date < date.today() else "-"
    title = kwargs.get("title", student_dict.get("title"))
    programme = f"{degree} {title}"
    full_name = student_dict.get('transcript_name') or f'{student_dict.get("given_name")} {student_dict.get("family_name")}'
    levels = kwargs.get("levels", (4, 5, 6) if not top_up else (6,))

    results_df = pd.DataFrame.from_records(results_dict).query('Level in @levels')
    results_df['Class'] = results_df['Mark'].apply(lambda t: get_class(t))
    results_df['Mark'] = results_df['Mark'].fillna('')
    results_df = results_df.sort_values(by=['Level', 'Module'])

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

    with open("latex/{} {}.tex".format(student_id, full_name), 'w') as f:
        template_data = {"student_name": full_name,
                         "student_id": student_id,
                         "issued": date.today(),
                         "programme": programme,
                         "status": degree_status,
                         "modules": results_df.to_dict(orient='records'),
                         "top_up": top_up,
                         "start_date": start_date,
                         "end_date": end_date, 
                         "overall_credits": overall_credits
                         }
        f.write(template.render(template_data))


def cohort(cohort_name):
    for s in app_data.get_students_by_cohort_name(cohort_name):
        populate_template(s.get("student_id"))


if __name__ == "__main__":
    pass
