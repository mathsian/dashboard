import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd

from dashboard import app, db

enrolment_query = {"selector": {"type": "enrolment"},
                      "fields": ["id", "given_name", "family_name", "cohort", "aps"],
                      "sort": [{"cohort": "asc"}, {"family_name": "asc"}, {"given_name": "asc"}]}
students= list(db.find(enrolment_query))

layout = html.Div([
   dash_table.DataTable(
       id='table',
       columns=[{'name': i, 'id': i} for i in students[0].keys()],
       data=students)
])
