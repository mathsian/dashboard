from dash.dependencies import Input, Output, State
import data


def register_callbacks(app):
    @app.callback(
        Output("store-data", "data"),
        [Input({"type": "filter-dropdown", "id": "cohort"}, "value")],
    )
    def store_student_data(cohort_value):
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
