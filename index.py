from flask import session
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app, server

from structure import home
from history import History

navbar = dbc.Navbar(dbc.Container([
    dbc.Col(dbc.NavbarBrand("data@ada"), width=1),
    dbc.Col(dbc.Nav(dbc.DropdownMenu(id="section_links", nav=True), justified=True), width=2),
    dbc.Col(dbc.Nav(id="page_links", justified=True, pills=True), width="auto"),
    dbc.Col(dbc.Nav(dbc.NavItem(dbc.NavLink(id="settings_links")), justified=True), width=2)
    ]))

cardheader = dbc.CardHeader(
    dbc.Row([
        dbc.Col(dbc.Tabs(id="tabs", active_tab=""), width='auto'),
    ],
            align='end'))
cardbody = dbc.CardBody(id="content")
card = dbc.Card(children=[cardheader, cardbody])

sidebar = dbc.Card(dbc.CardBody(id="sidebar_content"), body=True)

app.layout = dbc.Container([
    dcc.Location(id="location", refresh=False),
    navbar,
    dbc.Row([dbc.Col(sidebar, width=3),
             dbc.Col(card, width=9)], class_name='g-0')
], fluid=True)


def parse(pathname):
    '''Parse the url.
    Return section, page and tab objects.'''
    levels = pathname.split("/")
    section_path = levels[1] if len(levels) > 1 else None
    page_path = levels[2] if len(levels) > 2 else None
    tab_path = levels[3] if len(levels) > 3 else None

    page, tab = None, None
    # retrieve child if found or None
    section = home.children.get(section_path, None)
    if section:
        page = section.children.get(page_path, None)
        if page:
            tab = page.children.get(tab_path, None)
    return section, page, tab


@app.callback([
    Output("section_links", "label"),
    Output("section_links", "children"),
    Output("page_links", "children"),
    Output("tabs", "children"),
    Output("tabs", "active_tab"),
    Output("sidebar_content", "children"),
    Output("content", "children"),
    Output("location", "pathname"),
    Output("settings_links", "children"),
], [
    Input("location", "pathname"),
    Input("tabs", "active_tab"),
])
def location_change(pathname, active_tab):
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
        # Get the previous location from active_tab
        previous_section, previous_page, previous_tab = parse(active_tab)
        active_tab = "/".join(["", section.path, page.path, tab.path])
    elif input_id == "tabs":
        # Set the location from the active tab
        section, page, tab = parse(active_tab)
        # Get the previous location from pathname
        previous_section, previous_page, previous_tab = parse(pathname)
        pathname = active_tab

    # If the section hasn't changed we don't need to update section_links
    if previous_section and (section.path == previous_section.path):
        section_links = dash.no_update
    else:
        # Update the section dropdown
        section_links = [
                dbc.DropdownMenuItem(dbc.NavLink(s.name, href="/" + path))
                for path, s in home.children.items()
            ]

    # If the page hasn't changed we don't need to update it
    if previous_page and (page.path == previous_page.path):
        page_layout = dash.no_update
        page_links = dash.no_update
    else:
        page_layout = page.layout
        # Update the page nav links
        page_links = [
            dbc.NavItem(
                dbc.NavLink(p.name,
                            href="/".join(["", section.path, path]),
                            active=(p.path == page.path)))
            for path, p in section.children.items()
        ]

    # Update the tabs
    tabs = [
        dbc.Tab(label=t.name,
                tab_id="/".join(["", section.path, page.path, t.path]))
        for _, t in page.children.items()
    ]
    return [
        section.name,
        section_links,
        page_links,
        tabs,
        active_tab,
        page_layout,
        tab.layout,
        pathname,
        session.get("email", "No email"),
    ]
