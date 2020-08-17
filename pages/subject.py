"""
Layout for subject-focused data
"""
import dash_core_components as dcc
import dash_table

subject_graph = dcc.Graph(id="subject-graph")
subject_table = dash_table.DataTable(
            id="subject-table",
            columns=[
                {"name": "Given name", "id": "given_name"},
                {"name": "Family name", "id": "family_name"},
                {"name": "Grade", "id": "grade"},
            ],
        )
subtabs = [
    dcc.Tab(value="tab-subject-view", label="View"),
    dcc.Tab(value="tab-subject-edit", label="Edit"),
]
content = {"tab-subject-view": subject_graph, "tab-subject-edit": subject_table}
sidebar = {
    "tab-subject-view": [],
    "tab-subject-edit": []
}
panel = {
    "tab-subject-view": [],
    "tab-subject-edit": []
}
