from os.path import abspath
import jinja2
from jinja2 import Template
import subprocess
import pandas as pd
from configparser import ConfigParser
import pyodbc
from datetime import date

latex_jinja_env = jinja2.Environment(
    variable_start_string = '\VAR{',
    variable_end_string = '}',
    line_statement_prefix = '%%',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(abspath('../templates'))
)

def populate_template(student_id):
    # Get connection settings
    config_object = ConfigParser()
    config_object.read("../config.ini")
    rems_settings = config_object["REMS"]
    rems_server = rems_settings["ip"]
    rems_uid = rems_settings["uid"]
    rems_pwd = rems_settings["pwd"]
    conn = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={rems_server};DATABASE=Reports;UID={rems_uid};PWD={rems_pwd}'
    )
    with open("../sql/sf_transcript.sql", 'r') as sql:
        outcomes_df = pd.read_sql(sql.read(), conn, params=[student_id])
    student_name = f'{outcomes_df.iloc[0]["STUD_Forename_1"]} {outcomes_df.iloc[0]["STUD_Surname"]}'
    student_uln = outcomes_df.iloc[0]["STUD_ULN"]
    glh_df = outcomes_df[['LEARNING_AIM_REF', 'STEN_Annual_GLH']].groupby('LEARNING_AIM_REF').sum().reset_index()
    achieved_df = outcomes_df.drop('STEN_Annual_GLH', axis=1).query("outcome == 'Achieved'")
    merged_df = pd.merge(left=achieved_df, right=glh_df, left_on='LEARNING_AIM_REF', right_on='LEARNING_AIM_REF', how='left')
    print(merged_df)
    subjects = merged_df.to_dict(orient='records')
    template = latex_jinja_env.get_template('sf_transcript.tex')
    with open("../latex/{} {}.tex".format(student_id, student_name),'w') as f:
        template_data = {"student_name": student_name,
                         "student_id": student_id,
                         "student_uln": student_uln,
                         "subjects": subjects,
                         "issued": date.today()
                        }
        print(template_data)
        f.write(template.render(template_data))


if __name__ == "__main__":
    populate_template(160065)
