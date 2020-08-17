"""
Layout of student report
"""
import dash_html_components as html

layout = [
    html.Div(id="report-heading"),
    html.Div(id="report-subheading"),
    html.H3("Attendance"),
    html.Div(id="report-attendance"),
    html.H3("Academic"),
    html.Div(id="report-academic"),
    html.H3("Pastoral"),
    html.H4("Kudos"),
    html.Div(id="report-kudos"),
    html.H4("Concerns"),
    html.Div(id="report-concerns"),
]
