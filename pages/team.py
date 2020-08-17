import dash_core_components as dcc


subtabs = [
    dcc.Tab(value="tab-team-attendance", label="Attendance"),
    dcc.Tab(value="tab-team-kudos", label="Kudos"),
    dcc.Tab(value="tab-team-concern", label="Concern")
]
content = {
    "tab-team-attendance": [],
    "tab-team-kudos": [],
    "tab-team-concern": []
}
sidebar = {
    "tab-team-attendance": [],
    "tab-team-kudos": [],
    "tab-team-concern": []
}
panel = {
    "tab-team-attendance": [],
    "tab-team-kudos": [],
    "tab-team-concern": []
}
