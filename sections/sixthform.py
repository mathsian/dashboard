import dash_html_components as html

from structure import Section, Page, Tab

pastoral_tabs = [
    Tab("Attendance", "attendance", html.Div("Attendance"), []),
    Tab("Kudos", "Kudos", html.Div("Kudos"), [])
]
academic_tabs = [
    Tab("Cohort", "cohort", html.Div("Cohort"), []),
    Tab("Subject", "subject", html.Div("Subject"), [])
]
sixthform_pages = [
    Page("Pastoral", "pastoral", [], [], pastoral_tabs),
    Page("Academic", "academic", [], [], academic_tabs)
]
sixthform = Section("Sixth Form", "sixthform", [], [], sixthform_pages)
