import dash_tabulator
import dash
import plotly.express as px
import plotly.subplots as sp
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy as np
from urllib.parse import parse_qs, urlencode

from icecream import ic

from app import app
import app_data
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

layout = dbc.Row(
    dbc.Col(
        [html.H4(
            id={
                "section": "apprenticeships",
                "type": "heading",
                "page": "cohorts",
                "tab": "report",
                "name": "reports"
            }),
            dmc.Accordion(
                id={
                    "section": "apprenticeships",
                    "type": "accordion",
                    "page": "cohorts",
                    "tab": "report",
                    "name": "reports"
                },
                children=""
            )]
    ))


@app.callback([
    Output(
        {
            "section": "apprenticeships",
            "type": "heading",
            "page": "cohorts",
            "tab": "report",
            "name": "reports"
        }, "children"),
    Output(
        {
            "section": "apprenticeships",
            "type": "accordion",
            "page": "cohorts",
            "tab": "report",
            "name": "reports"
        }, "children"),
], [
    Input(
        {
            "section": "apprenticeships",
            "type": "storage",
            "page": "cohorts",
            "name": "selected"
        }, "data")
])
def update_student_report(store_data):
    if not store_data:
        return "Select a student to view their report", []
    accordion_items = []
    for student_id in store_data:
        student = app_data.get_student_by_id(student_id)

        results, credits, average_result = app_data.get_results_report_for_student(student_id,
                                                                                   student.get('top_up', False))

        attendance_dict = app_data.get_apprentice_attendance(student_id)[0]

        info_table = dbc.Table([
            html.Tr([
                html.Td("Student ID"),
                html.Td(student_id)
            ]),
            html.Tr([
                html.Td("Cohort"),
                html.Td(student.get("cohort_name"))
            ]),
            html.Tr([
                html.Td("Employer"),
                html.Td(student.get("employer"))
            ]),
            html.Tr([
                html.Td("Status"),
                html.Td(student.get("status"))
            ]),
            html.Tr([
                html.Td("Top up"),
                html.Td("Yes" if student.get('top_up', False) else "No")
            ]),
        ], borderless=True)

        summary_table = dbc.Table([
            html.Tr([html.Td("Credits"),
                     html.Td(credits, style={'text-align': 'right'})
                     ]),
            html.Tr([html.Td("Average"),
                     html.Td(average_result, style={'text-align': 'right'})
                     ]),
            html.Br(),
            html.Tr([html.Td("90 day attendance"),
                     html.Td("-" if attendance_dict.get('90 day attendance (%)') is None else f"{attendance_dict.get('90 day attendance (%)'):.1f}", style={'text-align': 'right'})
                     ]),
            html.Tr([html.Td("90 day punctuality"),
                     html.Td("-" if attendance_dict.get('90 day punctuality (%)') is None else f"{attendance_dict.get('90 day punctuality (%)'):.1f}", style={'text-align': 'right'})
                     ]),
            html.Tr([html.Td("All time attendance"),
                     html.Td("-" if attendance_dict.get('All time attendance (%)') is None else f"{attendance_dict.get('All time attendance (%)'):.1f}", style={'text-align': 'right'})
                     ]),
            html.Tr([html.Td("All time punctuality"),
                     html.Td("-" if attendance_dict.get('All time punctuality (%)') is None else f"{attendance_dict.get('All time punctuality (%)'):.1f}", style={'text-align': 'right'})
                     ]),
        ], borderless=True, style={'max-width': '320px'})

        results_table = dbc.Table([
            html.Tr([
                html.Td(r.get("level", "-"), style={'text-align': 'right'}),
                html.Td(r.get("name", "-")),
                html.Td(
                    html.A(r.get("code"),
                           href=f'/apprenticeships/academic/edit?module={r.get("short")}&instance={r.get("code")}')
                ),
                html.Td(r.get("total", "-"), style={'text-align': 'right'}),
                html.Td(f"({r.get('credits', '-')})", style={'text-align': 'right'}),

            ]) for r in results
        ], style={'max-width': '480px'})

        accordion_children = [dbc.Row([
            dbc.Col([info_table, summary_table], width=4),
            dbc.Col([results_table], width=8)
        ], justify='between')]

        accordion_item = dmc.AccordionItem(children=[
            dmc.AccordionControl(html.B(f'{student.get("given_name")} {student.get("family_name")}')),
            dmc.AccordionPanel(id={
                "type": "accordion_item",
                "section": "apprenticeships",
                "page": "cohorts",
                "tab": "report",
                "name": f'{student_id}'
            },
                children=accordion_children,

            )],
            value=f'{student.get("given_name")} {student.get("family_name")}'
        )
        accordion_items.append(accordion_item)

    return "", accordion_items
