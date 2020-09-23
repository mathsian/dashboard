from dash import callback_context
from dash.dependencies import Input, Output, State
import data
from flask_dance.contrib.google import google

def register_callbacks(app):
    @app.callback(
        Output("store-data", "data"),
        [Input({"type": "filter-dropdown", "id": "cohort"}, "value"),
         Input("subject-save-button", "n_clicks"),
         Input("div-kudos-message", "children")],
        [State("subject-table", "data")],
    )
    def store_student_data(cohort_value, n_clicks, msg, subject_table_data):
        if callback_context.triggered:
            if callback_context.triggered[0]['prop_id'] == "subject-save-button.n_clicks":
                # subject table data is based on a pandas join so
                # we need to parse it remembering that the left (x) was assessments
                # be sure to compare this to the column headings from pages/subject.py
                assessments = [
                {
                    "_id": row.get("_id_x"),
                    "_rev": row.get("_rev"),
                    "type": "assessment",
                    "subtype": row.get("subtype"),
                    "subject": row.get("subject"),
                    "student_id": row.get("student_id"),
                    "assessment": row.get("assessment"),
                    "date": row.get("date"),
                    "grade": row.get("grade"),
                }
                    for row in subject_table_data]
        student_data = data.get_data("enrolment", "cohort", cohort_value)
        student_ids = [s.get("_id") for s in student_data]
        groups = data.get_data("group", "student_id", student_ids)
        attendance_data = data.get_data("attendance", "student_id", student_ids)
        assessment_data = data.get_data("assessment", "student_id", student_ids)
        kudos_data = data.get_data("kudos", "student_id", student_ids)
        concern_data = data.get_data("concern", "student_id", student_ids)
        result = {
            "student": student_data,
            "attendance": attendance_data,
            "assessment": assessment_data,
            "kudos": kudos_data,
            "concern": concern_data,
            "group": groups,
        }
        return result

    @app.callback(
        Output("store-student", "data"),
        [Input("sidebar-student-table", "selected_row_ids")],
        [State("store-student", "data")],
    )
    def store_student(row_ids, store_student):
        if row_ids:
            return data.get_student(row_ids[0])
        else:
            return store_student
