import dash_core_components as dcc


subtabs = [
    dcc.Tab(value="tab-cohort-summary", label="Summary"),
    dcc.Tab(value="tab-cohort-academic", label="Academic"),
    dcc.Tab(value="tab-cohort-pastoral", label="Pastoral")
]
content = {
    "tab-cohort-summary": [],
    "tab-cohort-academic": [],
    "tab-cohort-pastoral": []
}
sidebar = {
    "tab-cohort-summary": [],
    "tab-cohort-academic": [],
    "tab-cohort-pastoral": []
}
panel = {
    "tab-cohort-summary": [],
    "tab-cohort-academic": [],
    "tab-cohort-pastoral": []
}
