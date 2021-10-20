from os.path import abspath
import jinja2
from jinja2 import Template
import pandas as pd

latex_jinja_env = jinja2.Environment(
    variable_start_string = '\VAR{',
    variable_end_string = '}',
    line_statement_prefix = '%%',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(abspath('../templates'))
)

df = pd.read_csv('./_newMarksheet - CACHE.csv')
progrs = pd.read_csv('./programmes.csv')

df.columns = ['student_id', 'student_name', 'name', 'code', 'level', 'total', 'class', 'first', 'company']

df = pd.merge(df, progrs, on='student_id')

df = df.set_index(['student_id', 'student_name', 'programme', 'level'])

df['class'] = df['class'].str.title().replace({"Tba": "tba"})
df['total'] = df['total'].str.title().replace({"Tba": "tba"})

df = df.sort_index().astype(str)

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
    student_name = df.loc[student_id].index.unique(0)[0]
    programme = df.loc[student_id].index.unique(1)[0]
    # there are level -1 in here, is that a mistake or a code?
    levels = filter(lambda l: l>=4, df.loc[student_id].index.unique(2))
    modules = [{"level": level, "results": df.loc[student_id, student_name, programme, level].to_dict(orient='records')} for level in levels]
    results = df.loc[student_id].query('total.str.isnumeric() and level > 3')
    overall = round(results['total'].astype(int).mean())
    overall_class = get_class(overall)
    template = latex_jinja_env.get_template('ap_transcript.tex')
    with open("../latex/{} {}.tex".format(student_id, student_name),'w') as f:
        template_data = {"student_name": student_name,
                         "student_id": student_id,
                         "issued": "27/09/21",
                         "programme": programme,
                         "modules": modules,
                         "overall": overall,
                         "overall_class": overall_class
                        }
        f.write(template.render(template_data))

populate_template('0000000')
