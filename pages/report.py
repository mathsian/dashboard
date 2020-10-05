"""
Layout of student report
"""
import dash_html_components as html
import dash_core_components as dcc
import dash_table


layout = [
    html.H2(id="report-heading"),
    html.Div(id="report-subheading"),
    html.H4("Attendance"),
    html.Div(id="report-attendance"),
    html.H4("Academic"),
    html.Div(id="report-academic"),
    html.H4("Pastoral"),
    html.H6("Kudos"),
    html.Div(
        dash_table.DataTable(
            id="report-kudos",
            columns=[
                {"name": "Value", "id": "ada_value"},
                {"name": "Points", "id": "points"},
                {"name": "For", "id": "description"},
                {"name": "From", "id": "from"},
                {"name": "Date", "id": "date"},
            ],
            style_cell={
                "maxWidth": "240px",
                "textAlign": "left",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
        )
    ),
    html.H6("Concerns"),
    html.Div(
        dash_table.DataTable(
            id="report-concerns",
            columns=[
                {"name": "Date", "id": "date"},
                {"name": "Category", "id": "category"},
                {"name": "Description", "id": "description"},
                {"name": "Raised by", "id": "from"},
                {"name": "Additional", "id": "discrimination"},
            ],
            style_cell={
                "maxWidth": "240px",
                "textAlign": "left",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
        )
    ),
]
