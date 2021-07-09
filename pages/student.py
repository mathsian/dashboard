import filters
from flask import session
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
import dash_table
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import callback_context as cc
import datetime
from flask import session
import dash_tabulator
from app import app
import data
import curriculum

# The student list is on a separate card alongside the tabs
# so that it isn't updated when the tab changes
student_table = dash_tabulator.DashTabulator(
    id={
        "type": "table",
        "page": "student"
    },
    options={
        "resizableColumns": False,
        "selectable": True,
        "maxHeight": "60vh",
    },
    theme='bootstrap/tabulator_bootstrap4',
    columns=[
        {
            "formatter": "rowSelection",
            "titleFormatter": "rowSelection",
            "horizAlign": "center",
            "headerSort": False,
            "widthGrow": 1,
        },
        {
            "title": "Student ID",
            "field": "student_id",
            "visible": False,
        },
        {
            "field": "given_name",
            "widthGrow": 4,
            "headerFilter": True,
            "headerFilterPlaceholder": "Search",
        },
        {
            "field": "family_name",
            "widthGrow": 6,
            "headerFilter": True,
            "headerFilterPlaceholder": "Search",
        },
    ],
)
student_table_container = html.Div(
    [student_table],
)
blank_attendance = {
    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        }
    }
}
report = html.Div([
    html.H2(id={
        "type": "text",
        "page": "student",
        "tab": "report",
        "name": "heading"
    }),
    html.Div(id={
        "type": "text",
        "page": "student",
        "tab": "report",
        "name": "subheading"
    }),
    html.H3("Attendance"),
    html.Div(id={
        "type": "text",
        "page": "student",
        "tab": "report",
        "name": "attendance"
    }),
    dcc.Graph(id={
        "type": "graph",
        "page": "student",
        "tab": "report",
        "name": "attendance"
    },
              figure=blank_attendance,
              config={"displayModeBar": False}),
    html.H3("Academic"),
    html.Div(id={
        "type": "text",
        "page": "student",
        "tab": "report",
        "name": "academic"
    }),
    html.H3("Pastoral"),
    html.H4("Kudos"),
    html.Div(
        dash_table.DataTable(
            id={
                "type": "table",
                "page": "student",
                "tab": "report",
                "name": "kudos"
            },
            columns=[
                {
                    "name": "Value",
                    "id": "ada_value"
                },
                {
                    "name": "Points",
                    "id": "points"
                },
                {
                    "name": "For",
                    "id": "description"
                },
                {
                    "name": "From",
                    "id": "from"
                },
                {
                    "name": "Date",
                    "id": "date"
                },
            ],
            style_cell={
                "textAlign": "left",
                "height": "auto",
                "whiteSpace": "normal",
            },
        )),
    html.H4("Concerns"),
    html.Div(
        dash_table.DataTable(
            id={
                "type": "table",
                "page": "student",
                "tab": "report",
                "name": "concern"
            },
            columns=[
                {
                    "name": "Date",
                    "id": "date"
                },
                {
                    "name": "Category",
                    "id": "category"
                },
                {
                    "name": "Description",
                    "id": "description"
                },
                {
                    "name": "Raised by",
                    "id": "from"
                },
                {
                    "name": "Additional",
                    "id": "discrimination"
                },
            ],
            style_cell={
                "textAlign": "left",
                "height": "auto",
                "whiteSpace": "normal",
            },
        )),
], style={"max-height": "60vh", "overflow-y": "auto"})
kudos_form = dbc.Row(children=[
    dbc.Col([
        dcc.Dropdown(
            id={
                "type": "dropdown",
                "page": "student",
                "tab": "kudos",
                "name": "value"
            },
            options=curriculum.values_dropdown["options"],
            value=curriculum.values_dropdown["default"],
        ),
        dcc.Dropdown(
            id={
                "type": "dropdown",
                "page": "student",
                "tab": "kudos",
                "name": "points"
            },
            options=curriculum.kudos_points_dropdown["options"],
            value=curriculum.kudos_points_dropdown["default"],
        ),
        dbc.Input(id={
            "type": "input",
            "page": "student",
            "tab": "kudos",
            "name": "description"
        },
                  type="text",
                  debounce=False,
                  placeholder="Comment (optional)"),
    ]),
    dbc.Col([
        dbc.Button("Submit",
                   id={
                       "type": "button",
                       "page": "student",
                       "tab": "kudos",
                       "name": "submit"
                   },
                   color="secondary",
                   n_clicks=0),
        html.Div(id={
            "type": "text",
            "page": "student",
            "tab": "kudos",
            "name": "message"
        })
    ])
])
concern_form = dbc.Row(children=[
    dbc.Col([
        dcc.Dropdown(
            id={
                "type": "dropdown",
                "page": "student",
                "tab": "concern",
                "name": "category"
            },
            options=curriculum.concern_categories_dropdown["options"],
            value=curriculum.concern_categories_dropdown["default"],
        ),
        dbc.Input(id={
            "type": "input",
            "page": "student",
            "tab": "concern",
            "name": "description"
        },
                  type="text",
                  debounce=False,
                  placeholder="Description"),
        dcc.Dropdown(
            id={
                "type": "dropdown",
                "page": "student",
                "tab": "concern",
                "name": "discrimination"
            },
            options=curriculum.concern_discrimination_dropdown["options"],
            placeholder="Discrimination (optional)",
            multi=True,
        ),
    ]),
    dbc.Col([
        dbc.Button("Submit",
                   id={
                       "type": "button",
                       "page": "student",
                       "tab": "concern",
                       "name": "submit"
                   },
                   color="secondary",
                   n_clicks=0),
        html.Div(id={
            "type": "text",
            "page": "student",
            "tab": "concern",
            "name": "message"
        })
    ])
])

tabs = ["Report", "Kudos", "Concern"]
content = [
    dbc.Card([
        dbc.CardHeader([
            dbc.Row([
                dbc.Col([
                    dbc.Tabs(
                        [
                            dbc.Tab(label=t, tab_id=f"student-tab-{t.lower()}")
                            for t in tabs
                        ],
                        id=f"student-tabs",
                        card=True,
                        active_tab=f"student-tab-{tabs[0].lower()}",
                    )
                ],
                        align='end'),
                dbc.Col([filters.cohort]),
                dbc.Col([filters.team]),
            ])
        ]),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([student_table_container], width=4),
                dbc.Col([html.Div(id=f"student-content")], width=8)
            ], ),
        ],
                     style={
#                         "max-height": "70vh",
#                         "overflow-y": "auto"
                     }
        )
    ], )
]

validation_layout = content + [report, kudos_form, concern_form]
tab_map = {
    "student-tab-report": report,
    "student-tab-kudos": kudos_form,
    "student-tab-concern": concern_form,
}


@app.callback(
    Output(f"student-content", "children"),
    [Input(f"student-tabs", "active_tab")],
)
def get_content(active_tab):
    return tab_map.get(active_tab)


@app.callback(
    Output({
        "type": "table",
        "page": "student"
    }, "data"),
    [
        Input({
            "type": "filter-dropdown",
            "filter": ALL
        }, "value"),
    ],
)
def update_student_table(filter_value):
    cohort, team = filter_value
    if cohort and team:
        enrolment_docs = data.get_data("enrolment", "cohort_team",
                                       (cohort, team))
    elif cohort:
        enrolment_docs = data.get_data("enrolment", "cohort", cohort)
    else:
        return [], []
    enrolment_df = pd.DataFrame(enrolment_docs).sort_values(
        by=["given_name", "family_name"])
    enrolment_df["student_id"] = enrolment_df["_id"]
    return enrolment_df.to_dict(orient='records')


@app.callback([
    Output(
        {
            "type": "text",
            "page": "student",
            "tab": "report",
            "name": "heading"
        }, "children"),
    Output(
        {
            "type": "text",
            "page": "student",
            "tab": "report",
            "name": "subheading"
        }, "children"),
    Output(
        {
            "type": "text",
            "page": "student",
            "tab": "report",
            "name": "attendance"
        }, "children"),
    Output(
        {
            "type": "graph",
            "page": "student",
            "tab": "report",
            "name": "attendance"
        }, "figure"),
    Output(
        {
            "type": "text",
            "page": "student",
            "tab": "report",
            "name": "academic"
        }, "children"),
    Output(
        {
            "type": "table",
            "page": "student",
            "tab": "report",
            "name": "kudos"
        }, "data"),
    Output(
        {
            "type": "table",
            "page": "student",
            "tab": "report",
            "name": "concern"
        }, "data"),
], [Input("selected-student-ids", "data")])
def update_student_report(selected_student_ids):
    if not selected_student_ids:
        return "", "Select a student to view their report", "", blank_attendance, [], [], []
    student_id = selected_student_ids[-1]
    enrolment_doc = data.get_student(student_id)
    heading = f'{enrolment_doc.get("given_name")} {enrolment_doc.get("family_name")}'
    assessment_docs = data.get_data("assessment", "student_id", student_id)
    assessment_children = []
    if len(assessment_docs) > 0:
        assessment_df = pd.DataFrame.from_records(assessment_docs).set_index(
            ['subject_name', 'assessment'])
        for subject_name in assessment_df.index.unique(level=0):
            assessment_children.append(html.H4(subject_name))
            for assessment in assessment_df.loc[subject_name].index.unique():
                assessment_children.append(html.H5(assessment))
                results = assessment_df.query(
                    "subject_name == @subject_name and assessment == @assessment"
                )
                for result in results.to_dict(orient='records'):
                    assessment_children.append(result.get("grade", ""))
                    assessment_children.append(
                        html.Blockquote(result.get("comment", "")))
    kudos_docs = data.get_data("kudos", "student_id", student_id)
    concern_docs = data.get_data("concern", "student_id", student_id)
    attendance_docs = data.get_data("attendance", "student_id", student_id)
    attendance_df = pd.DataFrame.from_records(attendance_docs).query(
        "subtype == 'weekly'")
    attendance_df['percent'] = round(100 * attendance_df['actual'] /
                                     attendance_df['possible'])
    attendance_year = round(100 * attendance_df['actual'].sum() /
                            attendance_df['possible'].sum())
    attendance_figure = go.Figure()
    attendance_figure.add_trace(
        go.Bar(x=attendance_df["date"],
               y=attendance_df["percent"],
               name="Weekly attendance"))
    return heading, f"Team {enrolment_doc.get('team')}", attendance_year, attendance_figure, assessment_children, kudos_docs, concern_docs


@app.callback([
    Output(
        {
            "type": "text",
            "page": "student",
            "tab": "kudos",
            "name": "message"
        }, "children"),
    Output(
        {
            "type": "button",
            "page": "student",
            "tab": "kudos",
            "name": "submit"
        }, "color"),
], [
    Input("selected-student-ids", "data"),
    Input(
        {
            "type": "input",
            "page": "student",
            "tab": "kudos",
            "name": "description"
        }, "value"),
    Input(
        {
            "type": "dropdown",
            "page": "student",
            "tab": "kudos",
            "name": "value"
        }, "value"),
    Input(
        {
            "type": "dropdown",
            "page": "student",
            "tab": "kudos",
            "name": "points"
        }, "value"),
    Input(
        {
            "type": "button",
            "page": "student",
            "tab": "kudos",
            "name": "submit"
        }, "n_clicks")
], [
    State(
        {
            "type": "button",
            "page": "student",
            "tab": "kudos",
            "name": "submit"
        }, "color"),
])
def update_kudos_message(selected_student_ids, description, ada_value, points,
                         n_clicks, button_color):
    if selected_student_ids:
        enrolment_docs = data.get_students(selected_student_ids)
        intro = html.Div(
            f'Award {points} {ada_value} kudos from {session.get("email")} to')
        desc = html.Div(["For ", html.Blockquote(description)
                         ]) if description else html.Div()
        recipients = dbc.ListGroup(children=[
            dbc.ListGroupItem(f'{s.get("given_name")} {s.get("family_name")}')
            for s in enrolment_docs
        ])
        if cc.triggered and "n_clicks" in cc.triggered[0][
                "prop_id"] and button_color == "primary":
            date = datetime.datetime.today().strftime("%Y-%m-%d")
            docs = [{
                "type": "kudos",
                "student_id": s,
                "ada_value": ada_value,
                "points": points,
                "description": description if description else "",
                "date": date,
                "from": session.get('email', "none"),
            } for s in selected_student_ids]
            data.save_docs(docs)
            return "Kudos awarded", "secondary"
        return [intro, recipients, desc], "primary"
    else:
        return "Select one or more students to award kudos", "secondary"


@app.callback([
    Output(
        {
            "type": "text",
            "page": "student",
            "tab": "concern",
            "name": "message"
        }, "children"),
    Output(
        {
            "type": "button",
            "page": "student",
            "tab": "concern",
            "name": "submit"
        }, "color"),
], [
    Input("selected-student-ids", "data"),
    Input(
        {
            "type": "input",
            "page": "student",
            "tab": "concern",
            "name": "description"
        }, "value"),
    Input(
        {
            "type": "dropdown",
            "page": "student",
            "tab": "concern",
            "name": "category"
        }, "value"),
    Input(
        {
            "type": "dropdown",
            "page": "student",
            "tab": "concern",
            "name": "discrimination"
        }, "value"),
    Input(
        {
            "type": "button",
            "page": "student",
            "tab": "concern",
            "name": "submit"
        }, "n_clicks")
], [
    State(
        {
            "type": "button",
            "page": "student",
            "tab": "concern",
            "name": "submit"
        }, "color"),
])
def update_concern_message(selected_student_ids, description, category,
                           discrimination, n_clicks, button_color):
    if selected_student_ids:
        enrolment_docs = data.get_students(selected_student_ids)
        intro = html.Div(f'Raise {category} concern about')
        desc = html.Div(["For ", html.Blockquote(description)
                         ]) if description else html.Div()
        recipients = dbc.ListGroup(children=[
            dbc.ListGroupItem(f'{s.get("given_name")} {s.get("family_name")}')
            for s in enrolment_docs
        ])
        if cc.triggered and "n_clicks" in cc.triggered[0][
                "prop_id"] and button_color == "primary":
            date = datetime.datetime.today().strftime("%Y-%m-%d")
            docs = [{
                "type": "concern",
                "student_id": s,
                "category": category,
                "discrimination": discrimination,
                "description": description if description else "",
                "date": date,
                "from": session.get('email', "none"),
            } for s in selected_student_ids]
            data.save_docs(docs)
            return "Concern raised", "secondary"
        return [intro, recipients, desc], "primary"
    else:
        return "Select one or more students to raise concern", "secondary"
