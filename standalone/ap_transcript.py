from os.path import abspath
import jinja2
from jinja2 import Template
import pandas as pd
import sys 
sys.path.append('..')
import app_data

latex_jinja_env = jinja2.Environment(
    variable_start_string = '\VAR{',
    variable_end_string = '}',
    line_statement_prefix = '%%',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(abspath('../templates'))
)

def get_class(mark):
    if mark >= 69.5:
        return 'Distinction'
    elif mark >= 59.5:
        return 'Merit'
    elif mark >= 39.5:
        return 'Pass'
    else:
        return 'Incomplete'

def populate_template(student_id):
    if isinstance(student_id, str):
        student_id = int(student_id)
    student_dict = app_data.get_student_by_id(student_id)
    results_dict = app_data.get_detailed_results_for_student(student_id)
    results_df = pd.DataFrame.from_records(results_dict)
    results_df['class'] = results_df['total'].apply(lambda t: get_class(t))
    results_df.sort_values(by=['level', 'name'], inplace=True)
    overall = round(results_df['total'].astype(int).mean())
    overall_class = get_class(overall)
    overall_credits = results_df['credits'].sum()
    template = latex_jinja_env.get_template('ap_transcript.tex')
    full_name = f'{student_dict.get("given_name")} {student_dict.get("family_name")}'
    with open("../latex/{} {}.tex".format(student_id, full_name),'w') as f:
        template_data = {"student_name": full_name, 
                         "student_id": student_id,
                         "issued": "24/02/22",
                         "programme": "Foundation Degree in Digital Innovation",
                         "modules": results_df.to_dict(orient='records'),
                         "overall": overall,
                         "overall_class": overall_class,
                         "overall_credits": overall_credits
                        }
        f.write(template.render(template_data))

populate_template(999999)
