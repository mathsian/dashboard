from flask import session
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app, server

from structure import home
from history import History

navbar = dbc.Navbar([
    dbc.Col(dbc.NavbarBrand("data@ada"), width=1),
    dbc.Col(dbc.Nav(dbc.NavItem(id="section_links"), horizontal='end'),
            width=2),
    dbc.Col(id="page_links", width=True),
    dbc.Col(dbc.Nav(
        dbc.NavItem(
            dbc.DropdownMenu(id="history_links", label="History", nav=True))),
            width=2),
    dbc.Col(dbc.Nav(dbc.NavItem(dbc.NavLink(id="settings_links"))), width=2)
],
                    # style={"margin-bottom": 10}
)

cardheader = dbc.CardHeader(
    dbc.Row([
        dbc.Col(dbc.Tabs(id="tabs", card=True), width='auto'),
    ], align='end'))
cardbody = dbc.CardBody(id="content")
card = dbc.Card(children=[cardheader, cardbody])

sidebar_header = dbc.Row(dbc.Col(id="cardheader_content"))
sidebar_content = dbc.Row(dbc.Col(id="sidebar_content"))
sidebar = dbc.Card(dbc.CardBody([sidebar_header, sidebar_content]), body=True)

app.layout = dbc.Container([
        dcc.Location(id="location", refresh=False),
        dcc.Store(id="history", storage_type='local'),
        dbc.Row(dbc.Col(navbar)),
        dbc.Row([dbc.Col(sidebar, width=3), dbc.Col(card, width=9)], no_gutters=True)
    ], fluid=True)
# app.layout = dbc.Container(children=layout, fluid=True)


def parse(pathname):
    '''Parse the url.
    Return section, page and tab objects.'''

    levels = pathname.split("/")
    section_path = "/".join(levels[:2])
    page_path = "/".join(levels[:3])
    tab_path = pathname

    section = None
    page = None
    tab = None

    # retrieve child if found or False
    section = home.children.get(section_path, None)
    if section:
        page = section.children.get(page_path, None)
        if page:
            tab: Tab = page.children.get(tab_path, None)

    return section, page, tab


@app.callback([
    Output("section_links", "children"),
    Output("page_links", "children"),
    Output("tabs", "children"),
    Output("tabs", "active_tab"),
    Output("cardheader_content", "children"),
    Output("sidebar_content", "children"),
    Output("content", "children"),
    Output("location", "pathname"),
    Output("location", "search"),
    Output("settings_links", "children"),
], [
    Input("location", "pathname"),
    Input("location", "search"),
    Input("tabs", "active_tab"),
], [State("history", "data")])
def location_change(pathname, search, active_tab, history):
    '''Called whenever the location should change, either through url or tab click.
    Returns content from the appropriate section, page and tab to the layout'''

    # Circular callback so we need to know whether it was called by a link, a tab change or a dropdown
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if input_id == "location":
        # Attempt to parse link
        section, page, tab = parse(pathname)
        if not section:
            section = list(home.children.values())[0]
        if not page:
            page = list(section.children.values())[0]
        if not tab:
            tab = list(page.children.values())[0]
        # Set the active tab from the location
        active_tab = tab.path
    elif input_id == "tabs":
        # Set the location from the active tab
        section, page, tab = parse(active_tab)
        pathname = tab.path

    # Update the section dropdown
    section_links = dbc.DropdownMenu(label=section.name,
                                     nav=False,
                                     color='primary',
                                     children=[
                                         dbc.DropdownMenuItem(
                                             dbc.NavLink(s.name, href=path))
                                         for path, s in home.children.items()
                                     ])

    # Update the page nav links
    page_links = dbc.Nav(children=[
        dbc.NavItem(
            dbc.NavLink(p.name, href=path, active=(p.path == page.path)))
        for path, p in section.children.items()
    ],
                         pills=True)

    # Update the tabs
    tabs = [
        dbc.Tab(label=t.name, tab_id=path)
        for path, t in page.children.items()
    ]

    return [
        section_links,
        page_links,
        tabs,
        active_tab,
        page.cardheader_layout,
        page.sidebar_layout,
        tab.layout,
        pathname,
        search,
        session.get("email", "No email"),
    ]
