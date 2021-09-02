import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from app import app

from structure import home

navbar = dbc.Navbar([
    dbc.Col(dbc.NavbarBrand("data@ada"), width=1),
    dbc.Col(dbc.Nav(dbc.NavItem(dbc.DropdownMenu(id="section_links", nav=False, color='primary')), horizontal='end'), width=2),
    dbc.Col(dbc.Nav(id="page_links", pills=True), width=True),
    dbc.Col(dbc.Nav(dbc.NavItem(dbc.DropdownMenu(id="history_links", label="History", nav=True))), width=2),
    dbc.Col(dbc.Nav(dbc.NavItem(dbc.NavLink("Settings"))), width=1)
])
cardheader = dbc.CardHeader(dbc.Row([
    dbc.Col(dbc.Tabs(id="tabs", card=True), width=6),
    dbc.Col(id="cardheader_content", width=6)
]))

cardbody = dbc.CardBody(dbc.Row([
    dbc.Col(id="sidebar_content", width=3),
    dbc.Col(id="content", width=9)
]))

card = dbc.Card(children=[cardheader, cardbody])

app.layout = dbc.Container(
    children=[
        dcc.Location(
            id="location",
            refresh=False
        ),
        dcc.Store(
            id="history",
            storage_type='local'),
        navbar,
        card
    ],
    fluid=True
)


def parse(pathname):
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


@app.callback(
    [
        Output("section_links", "label"),
        Output("section_links", "children"),
        Output("page_links", "children"),
        Output("tabs", "children"),
        Output("tabs", "active_tab"),
        Output("cardheader_content", "children"),
        Output("sidebar_content", "children"),
        Output("content", "children"),
        Output("location", "pathname"),
        Output("history", "data"),
        Output("history_links", "children")
    ],
    [
        Input("location", "pathname"),
        Input("tabs", "active_tab")
    ],
    [
        State("history", "data")
    ]
)
def location_change(pathname, active_tab, history):

    history = history or []

    # Circular callback so we need to know whether it was called by a link or a tab change
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id == "location":
        # Attempt to parse link
        section, page, tab = parse(pathname)
        # If unsuccessful, look in matching history first, otherwise first added child
        if not section:
            if history:
                section, page, tab = parse(history[-1])
            else:
                section = list(home.children.values())[0]
        if not page:
            if matches := [path for path in history if path.startswith(section.path)]:
                section, page, tab = parse(matches[-1])
            else:
                page = list(section.children.values())[0]
        if not tab:
            if matches := [path for path in history if path.startswith(page.path)]:
                section, page, tab = parse(matches[-1])
            else:
                tab = list(page.children.values())[0]
        # Set the active tab from the location
        active_tab = tab.path
    elif input_id == "tabs":
        section, page, tab = parse(active_tab)
        # Set the location from the active tab
        pathname = tab.path

    # Update the history and history dropdown
    if tab.path in history:
        history.pop(history.index(tab.path))
    history.append(tab.path)
    if len(history) > 10:
        history.pop(0)
    history_links = [
        dbc.DropdownMenuItem(dbc.NavLink(" - ".join(map(str.capitalize, h.removeprefix("/").split("/"))), href=h))
        for h in reversed(history)
    ]
    # Update the section dropdown
    section_links = [
        dbc.DropdownMenuItem(dbc.NavLink(s.name, href=path))
        for path, s in home.children.items()
    ]

    # Update the page nav links
    page_links = [
        dbc.NavItem(dbc.NavLink(p.name, href=path, active=(p.path == page.path)))
        for path, p in section.children.items()
    ]

    # Update the tabs
    tabs = [dbc.Tab(label=t.name, tab_id=path) for path, t in page.children.items()]

    return (section.name, section_links, page_links,
            tabs, active_tab, section.layout, page.layout,
            tab.layout, pathname, history, history_links)


if __name__ == "__main__":
    app.run_server(debug=True, port=8001)
