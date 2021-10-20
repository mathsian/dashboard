from os.path import abspath
import jinja2
from jinja2 import Template
import subprocess
import pandas as pd

latex_jinja_env = jinja2.Environment(
    variable_start_string = '\VAR{',
    variable_end_string = '}',
    line_statement_prefix = '%%',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(abspath('../templates'))
)

def populate_template(student_id):
    template = latex_jinja_env.get_template('sf_transcript.tex')
    #####
    with open("../latex/{} {}.tex".format(student_id, student_name),'w') as f:
        template_data = {"student_name": student_name,
                         "student_id": student_id,
                         "student_uln": student_uln,
                         "subjects": subjects,
                        }
        print(template_data)
        f.write(template.render(template_data))


if __name__ == "__main__":
    populate_template()
