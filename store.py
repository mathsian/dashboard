from dash import callback_context
from dash.dependencies import Input, Output, State
import data


def register_callbacks(app):
    @app.callback(
        Output("store-data", "data"),
        [Input({"type": "filter-dropdown", "id": "cohort"}, "value"),
         Input("subject-save-button", "n_clicks")],
        [State("subject-table", "data")],
    )
    def store_student_data(cohort_value, n_clicks, subject_table_data):
        if callback_context.triggered:
            if callback_context.triggered[0]['prop_id'] == "subject-save-button.n_clicks":
                # subject table data is based on a pandas join so
                # we need to parse it remembering that the left (x) was assessments
                assessments = [
                {
                    "_id": row.get("_id_x"),
                    "_rev": row.get("_rev_x"),
                    "type": "assessment",
                    "subtype": row.get("subtype"),
                    "subject": row.get("subject"),
                    "student_id": row.get("student_id"),
                    "cohort": row.get("cohort_x"),
                    "assessment": row.get("assessment"),
                    "date": row.get("date"),
                    "grade": row.get("grade"),
                }
                    for row in subject_table_data]
        result = {
            "student": data.get_data("enrolment", "cohort", cohort_value),
            "attendance": data.get_data("attendance", "cohort", cohort_value),
            "assessment": data.get_data("assessment", "cohort", cohort_value),
            "kudos": data.get_data("kudos", "cohort", cohort_value),
            "concern": data.get_data("concern", "cohort", cohort_value),
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
