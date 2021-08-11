from operator import itemgetter
from os.path import abspath
import jinja2
from jinja2 import Template
import subprocess
import pandas as pd
import numpy as np
import data
import curriculum
import plotly.graph_objects as go

def generate_report(student_id):
    kudos = sorted(data.get_data("kudos", "student_id", [student_id], "ada"), key=itemgetter('date'), reverse=True)
    kudos_total = 0
    for k in kudos:
        k["description"] = k.get("description", "").replace('%', '\%').replace('&', '\&')
        k['date'] = data.format_date(k['date'])
        kudos_total += k['points']
    student = data.get_student(student_id, "ada")

    latex_jinja_env = jinja2.Environment(
        variable_start_string='\VAR{',
        variable_end_string='}',
        line_statement_prefix='%%',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(abspath('.'))
    )

    template = latex_jinja_env.get_template('kudos_template.tex')
    student_name = f"{student.get('given_name')} {student.get('family_name')}"
    with open(f"latex/{student.get('_id')} {student_name}.tex", 'w') as f:
        template_data={"name": student_name,
                       "date": "June 2021",
                       "team": student.get("team"),
                       "kudos": kudos,
                       "kudos_total": kudos_total,
                       }
        f.write(template.render(template_data))


def cohort_reports(cohort):
    enrolment_docs = data.get_data("enrolment", "cohort", cohort, db_name="ada")
    for student in enrolment_docs:
        print(f"Generating report for {student.get('given_name')}")
        generate_report(student.get('_id'))

if __name__ == "__main__":
    cohort_reports("1921")
