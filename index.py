from urllib.parse import parse_qs, urlencode, urlparse
from flask import session
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL

from app import app, server

from structure import home
from history import History
import filters

navbar = dbc.Navbar([
    dbc.Col(dbc.NavbarBrand("data@ada"), width=1),
    dbc.Col(dbc.Nav(dbc.NavItem(dbc.DropdownMenu(id="section_links", nav=False, color='primary')), horizontal='end'), width=2),
    dbc.Col(dbc.Nav(id="page_links", pills=True), width=True),
    dbc.Col(dbc.Nav(dbc.NavItem(dbc.DropdownMenu(id="history_links", label="History", nav=True))), width=2),
    dbc.Col(dbc.Nav(dbc.NavItem(dbc.NavLink(id="settings_links"))), width=2)
])

cardheader = dbc.CardHeader(dbc.Row([
    dbc.Col(dbc.Tabs(id="tabs", card=True), width=6),
    dbc.Col(id="cardheader_content", width=6),
]))
cardbody = dbc.CardBody(dbc.Row([
    dbc.Col(id="content")
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
    '''Parse the url.
    Return section, page and tab objects.'''

    # Remove query if we got this from the history
    pathname = pathname[:pathname.find('?')]

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
        Output("content", "children"),
        Output("location", "pathname"),
        Output("location", "search"),
        Output("history", "data"),
        Output("history_links", "children"),
        Output("settings_links", "children"),
    ],
    [
        Input("location", "pathname"),
        Input("location", "search"),
        Input("tabs", "active_tab"),
        Input({"type": "filter-dropdown", "filter": ALL}, "value")
    ],
    [
        State("history", "data")
    ]
)
def location_change(pathname, search, active_tab, filter_values, history):
    '''Called whenever the location should change, either through url or tab click.
    Returns content from the appropriate section, page and tab to the layout'''

    history = history or History(maxlen=10)

    # Circular callback so we need to know whether it was called by a link, a tab change or a dropdown
    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Which filters are in context?
    # The last item of inputs_list will be a list of ALL filters in context
    filter_list = ctx.inputs_list[-1]

    url = False
    if input_id == "location":
        # Attempt to parse link
        section, page, tab = parse(pathname)
        # If unsuccessful, look in matching history first, otherwise first added child
        if not (section and page and tab):
            if url := history.get_match(pathname, search):
                section, page, tab = parse(url)
                search = '?' + parse_qs(urlparse(url).query)
            else:
                if not section:
                    section = list(home.children.values())[0]
                if not page:
                    page = list(section.children.values())[0]
                if not tab:
                    tab = list(page.children.values())[0]
        # Set the active tab from the location
        active_tab = tab.path
    elif input_id == "tabs":
        if url := history.get_match(active_tab, search):
            section, page, tab = parse(url)
            search = '?' + parse_qs(urlparse(url).query)
        else:
            section, page, tab = parse(active_tab)
        # Set the location from the active tab
        pathname = tab.path
    else:
        # Extract filters and their values from inputs_list
        section, page, tab = parse(active_tab)
        filter_dict = {i.get("id").get("filter"):i.get("value") for i in filter_list}
        search = '?'+urlencode(query=filter_dict)

    if not url:
        url = pathname + search
    # Update the history and history dropdown
    history.append(url)
    history_links = [
        dbc.DropdownMenuItem(dbc.NavLink(h, href=h))
        for h in history
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

    # Filter dropdowns are updated on change in search in their own callbacks

    return (section.name,
            section_links,
            page_links,
            tabs,
            active_tab,
            page.layout,
            tab.layout,
            pathname,
            search,
            history,
            history_links,
            session.get("email", "No email"),
    )
