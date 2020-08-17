"""
Layout for student-focused data
"""
import dash_core_components as dcc
import dash_html_components as html
import dash_table

from pages import report
from forms import kudos, concern

subtabs = [
    dcc.Tab(value="tab-student-report", label="Report"),
    dcc.Tab(value="tab-student-kudos", label="Kudos"),
    dcc.Tab(value="tab-student-concern", label="Concern"),
]
content = {
    "tab-student-report": [report.layout],
    "tab-student-kudos": [kudos.layout],
    "tab-student-concern": [concern.layout],
}
student_list = dash_table.DataTable(
    id="sidebar-student-table",
    columns=[{"name": "Name", "id": "value"}],
    row_selectable="single",
)
sidebar = {
    "tab-student-report": [student_list],
    "tab-student-kudos": [student_list],
    "tab-student-concern": [student_list],
}

panel = {"tab-student-report": [],
         "tab-student-kudos": [],
         "tab-student-concern": []}
