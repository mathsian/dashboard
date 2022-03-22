import sys
sys.path.append('..')
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
    academic = data.get_data("assessment", "student_id", [student_id], "ada")
    academic_df = pd.DataFrame.from_records(academic,
                                            columns=[
                                                "subject_name", "assessment",
                                                "grade", "date", "comment",
                                                "report"
                                            ]).query("report != 2").sort_values(by='date')
    academic_df["grade"] = academic_df["grade"].str.replace("S", "A*")
    academic_df["comment"] = academic_df["comment"].str.replace('%', '\%').replace('&', '\&')
    academic_df["comment"].fillna("", inplace=True)
    academic_multiindex = academic_df.set_index(["subject_name", "assessment"])[["grade", "date", "comment", "report"]]
    academic_dict = {
        subject: academic_multiindex.xs(subject).to_dict('index')
        for subject in academic_multiindex.index.levels[0]
    }
    student = data.get_student(student_id, "ada")
    latex_jinja_env = jinja2.Environment(variable_start_string='\VAR{',
                                         variable_end_string='}',
                                         line_statement_prefix='%%',
                                         trim_blocks=True,
                                         autoescape=False,
                                         loader = jinja2.FileSystemLoader(abspath('../templates')))

    template = latex_jinja_env.get_template('academic_template.tex')
    student_name = f"{student.get('given_name')} {student.get('family_name')}"
    with open(f"../latex/{student.get('_id')} {student_name}.tex", 'w') as f:
        template_data = {
            "name": student_name,
            "date": "March 2022",
            "team": student.get("team"),
            "academic": academic_dict,
        }
        f.write(template.render(template_data))


def cohort_reports(cohort):
    enrolment_docs = data.get_data("enrolment",
                                   "cohort",
                                   cohort,
                                   db_name="ada")
    for student in enrolment_docs:
        print(f"Generating report for {student.get('given_name')}")
        generate_report(student.get('_id'))
def group_reports(subject_code):
    group_docs = data.get_data("group", "subject_code", subject_code, db_name="ada")
    student_ids = [s.get("student_id") for s in group_docs]
    return student_ids

if __name__ == "__main__":
    #generate_report("201043")
    cohort_reports("2022")
    #for student_id in group_reports("BUS-L3AL"):
    #    generate_report(student_id)
