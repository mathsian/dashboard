import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State, ALL, MATCH
from dash import callback_context as cc
from app import app
from pages import summary, pastoral, academic, student

url_map = {
    "/": summary,
    "/pastoral": pastoral,
    "/academic": academic,
    "/student": student,
}

layout = dbc.Nav(
    children=[
        dbc.NavItem(
            children=dbc.NavLink(
                id={"type": "nav", "pathname": "/"}, children="Summary", href="/"
            ),
        ),
        dbc.NavItem(
            children=dbc.NavLink(
                id={"type": "nav", "pathname": "/pastoral"},
                children="Pastoral",
                href="/pastoral",
            ),
        ),
        dbc.NavItem(
            children=dbc.NavLink(
                id={"type": "nav", "pathname": "/academic"},
                children="Academic",
                href="/academic",
            ),
        ),
        dbc.NavItem(
            children=dbc.NavLink(
                id={"type": "nav", "pathname": "/student"},
                children="Student",
                href="/student",
            ),
        ),
    ],
    vertical=True,
    justified=True,
    pills=True,
)

# Get the relevant page content based on the url
@app.callback(
    Output("content", "children"), [Input("url", "pathname")],
)
def display_content(pathname):
    return url_map.get(pathname, summary).content


@app.callback(
    [Output({"type": "nav", "pathname": p}, "active") for p in url_map.keys()],
    [Input("url", "pathname")],
)
def update_active_link(pathname):
    return [p == pathname for p in url_map.keys()]
