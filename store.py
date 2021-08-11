# All callbacks which effect stored data
from dash import callback_context as cc
from dash.dependencies import Input, Output, State, ALL

import data
from app import app

# Keep this for reference for academic data when it's implemented
def store_student_data(cohort_value, n_clicks, subject_table_data):
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
                "comment": row.get("comment"),
                "date": row.get("date"),
                "grade": row.get("grade"),
            }
                for row in subject_table_data]
            data.save_docs(assessments)
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
    Output("selected-student-ids", "data"),
[
    Input(
    {"type": "table",
     "page": "student"},
        "multiRowsClicked"),
     Input({"type": "filter-dropdown", "filter": ALL}, "value"),
])
def store_student_ids(multiRowsClicked, filter_value):
    if cc.triggered and "multiRowsClicked" not in cc.triggered[0]["prop_id"]:
        return []
    else:
        return [row.get("student_id") for row in multiRowsClicked]

