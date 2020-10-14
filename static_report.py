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
    academic = data.get_data("assessment", "student_id", [student_id], "oct20")
    kudos = data.get_data("kudos", "student_id", [student_id], "oct20")
    concern = data.get_data("concern", "student_id", [student_id], "oct20")
    attendance = data.get_data("attendance", "student_id", [student_id], "oct20")
    student = data.get_student(student_id, "oct20")

    latex_jinja_env = jinja2.Environment(
        variable_start_string='\VAR{',
        variable_end_string='}',
        line_statement_prefix='%%',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(abspath('.'))
    )

    template = latex_jinja_env.get_template('template.tex')
    student_name = f"{student.get('given_name')} {student.get('family_name')}"
    with open(f"latex/{student_name}.tex", 'w') as f:
        template_data={"name": student_name,
                       "attendance": attendance,
                       "academic": academic,
                       "kudos": kudos,
                       "concern": concern}
        f.write(template.render(template_data))

        }
