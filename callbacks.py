"""
Pass the app once instantiated to register_callbacks(app)
"""
import datetime
from dash.dependencies import Input, Output, State
from pages import student, subject, cohort, team
import data


def register_callbacks(app):
    # When a main tab is selected
    # Show the appropriate subtabs
    # And change visibility of revelevant dropdowns
    @app.callback(
        [
            Output("div-tabs-sub", "children"),
            Output("dropdown-team", "hidden"),
            Output("dropdown-subject", "hidden"),
            Output("dropdown-assessment", "hidden"),
        ],
        [Input("tabs-main", "value")],
    )
    def tabs_main_value(tab):
        tab_dict = {
            "tab-main-cohort": (cohort.subtabs, True, True, True),
            "tab-main-team": (team.subtabs, True, False, False),
            "tab-main-subject": (subject.subtabs, False, True, True),
            "tab-main-student": (student.subtabs, True, False, False),
        }
        return tab_dict.get(tab)

    # When a subtab is selected
    # Get the main, sidebar and panel content
    @app.callback(
        [
            Output("div-main-content", "children"),
            Output("div-sidebar-content", "children"),
            Output("div-panel-content", "children"),
        ],
        [Input("tabs-sub", "value")],
        [State("tabs-main", "value")],
    )
    def tabs_sub_value(subtab_value, tab_value):
        tab_dict = {
            "tab-main-student": student,
            "tab-main-cohort": cohort,
            "tab-main-team": team,
            "tab-main-subject": subject,
        }
        tab = tab_dict.get(tab_value)
        return (
            tab.content.get(subtab_value),
            tab.sidebar.get(subtab_value),
            tab.panel.get(subtab_value),
        )

    @app.callback(
        Output("store-student-data", "data"),
        [Input("dropdown-cohort", "value"), Input("dropdown-team", "value")],
    )
    def store_student_data(cohort_value, team_value):
        return data.get_student_data(cohort_value, team_value)

    @app.callback(
        Output("store-assessment-data", "data"),
        [
            Input("dropdown-cohort", "value"),
            Input("dropdown-subject", "value"),
            Input("dropdown-assessment", "value"),
        ],
    )
    def store_assessment_data(cohort_values, subject_value, assessment_value):
        return data.get_assessment_data(cohort_values, subject_value, assessment_value)

    @app.callback(
        Output("store-student", "data"),
        [Input("student-list-student-table", "selected_row_ids")],
    )
    def store_student(row_ids):
        if row_ids:
            return row_ids[0]
        else:
            return {}

    @app.callback(
        [
            Output("kudos-confirm-dialog", "message"),
            Output("kudos-confirm-dialog", "displayed"),
        ],
        [Input("kudos-input-description", "n_submit")],
        [
            State("kudos-input-description", "value"),
            State("kudos-value-dropdown", "value"),
            State("kudos-points-dropdown", "value"),
        ],
    )
    def confirm_kudos(n_submit, description, value, points):
        if n_submit:
            msg = f"Award {points} {value} kudos for {description}?"
            return msg, True
        else:
            return "", False

    @app.callback(
        Output("div-kudos-message", "children"),
        [Input("dialog-kudos-confirm", "submit_n_clicks")],
        [
            State("input-kudos-description", "value"),
            State("dropdown-kudos-value", "value"),
            State("dropdown-kudos-points", "value"),
            State("store-student", "data"),
        ],
    )
    def submit_kudos(clicks, description, value, points, student):
        if clicks and student:
            date = datetime.datetime.today().strftime("%Y-%m-%d")
            doc = {
                "type": "kudos",
                "student_id": student["student_id"],
                "ada_value": value,
                "points": points,
                "description": description,
                "date": date,
            }
            result = data.save_docs([doc])
            return str(result)
        else:
            return "Not submitted"

    @app.callback(
        [
            Output("report-heading", "children"),
            Output("report-subheading", "children"),
            Output("report-attendance", "children"),
            Output("report-academic", "children"),
            Output("report-kudos", "children"),
            Output("report-concerns", "children"),
        ],
        [Input("current-student", "data"), Input("student-tabs", "value")],
    )
    def generate_report(data, tab):
        if tab != "report" or "student_id" not in data.keys():
            return [html.P("No student selected")], [], [], [], [], []
        db = get_db()
        student_id = data["student_id"]
        enrolment = db[student_id]
        heading_layout = html.H1(
            f'{enrolment["given_name"]} {enrolment["family_name"]}'
        )
        # The other data we want as pandas dataframes
        # Assessment
        assessment_df = get_as_df(db, "assessment", "student_id", student_id)
        assessment_layout = []
        # For each subject, graph grades against time
        for subject in assessment_df["subject"].unique():
            results = assessment_df.query(f'subject == "{subject}"').sort_values(
                by="date"
            )
            grade_array = curriculum.scales[subject]
            assessment_layout.append(
                dcc.Graph(
                    figure={
                        "data": [go.Scatter(x=results["date"], y=results["grade"])],
                        "layout": go.Layout(
                            title=subject,
                            yaxis={
                                "categoryorder": "array",
                                "categoryarray": grade_array,
                            },
                        ),
                    }
                )
            )
        # Kudos
        kudos_df = get_as_df(db, "kudos", "student_id", student_id)
        kudos_layout = dash_table.DataTable(
            columns=[
                {"name": "Value", "id": "ada_value"},
                {"name": "Points", "id": "points"},
                {"name": "For", "id": "description"},
                {"name": "Date", "id": "date"},
            ],
            data=kudos_df.to_dict(orient="records"),
        )

        # Concerns
        concerns_df = get_as_df(db, "concern", "student_id", student_id)
        concerns_layout = dash_table.DataTable(
            columns=[
                {"name": "Date", "id": "date"},
                {"name": "Category", "id": "category"},
                {"name": "Comment", "id": "comment"},
            ],
            data=concerns_df.to_dict(orient="records"),
        )

        return (
            heading_layout,
            [],
            [],
            assessment_layout,
            kudos_layout,
            concerns_layout,
        )
