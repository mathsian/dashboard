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
    academic = data.get_data("assessment", "student_id", [student_id], "ada")
    kudos = data.get_data("kudos", "student_id", [student_id], "ada")
    for k in kudos:
        k['date'] = data.format_date(k['date'])
    concern = data.get_data("concern", "student_id", [student_id], "ada")
    for c in concern:
        c['date'] = data.format_date(c['date'])
    attendance = data.get_data("attendance", "student_id", [student_id], "ada")
    student = data.get_student(student_id, "ada")

    attendance_df = pd.DataFrame.from_records(attendance).sort_values(by='date', ascending=True)
    attendance_df['date'] = attendance_df['date'].apply(data.format_date)
    attendance_df['percent'] = round(100*(attendance_df['actual']-attendance_df['late'])/attendance_df['possible'])
    attendance_df['late'] = round(100*attendance_df['late']/attendance_df['possible'])
    cumulative = int(100*attendance_df['actual'].sum()/attendance_df['possible'].sum())
    attendance_min = attendance_df['date'].tolist()[0]
    attendance_max = attendance_df['date'].tolist()[-1]
    attendance_dates = ",".join(f"{d}" for d in attendance_df["date"].tolist())
    attendance_zip = " ".join(f"({d}, {p})" for d, p in zip(attendance_df["date"].tolist(), attendance_df['percent'].tolist()))
    punctuality_zip = " ".join(f"({d}, {p})" for d, p in zip(attendance_df["date"].tolist(), attendance_df['late'].tolist()))
    print(punctuality_zip)
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
                       "attendance_dates": attendance_dates,
                       "attendance_zip": attendance_zip,
                       "punctuality_zip": punctuality_zip,
                       "attendance_cumulative": cumulative,
                       "academic": academic,
                       "kudos": kudos,
                       "concerns": concern}
        f.write(template.render(template_data))

if __name__ == "__main__":
    generate_report("200961")
