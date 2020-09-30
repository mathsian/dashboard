# Technologies

## CouchDB

https://couchdb.apache.org

NoSQL, json store database.

This allows to be flexible in the kinds of data we wish to store and report. Rather than instantiating new tables and risk getting stuck with poorly chosen schema, we can simply store json objects with a new `type` field.

`type` is currently one of
* `enrolment` for slow moving student information, name, team, cohort and prior attainment
* `group` for membership of teaching groups
* `attendance` for weekly attendance summaries per student
* `assessment` for a student score in a subject assessment
* `kudos` and `concern` for behaviour reporting

We use the IBM backed Python `cloudant` library for working with CouchDB.

Comes with a useful admin web interface.

## Python `dash`

https://plotly.com/dash

# Implementation

## `dashboard.py`

The app definition, configuration and authorization logic. Imports content layout and callbacks.

## `index.py`

Holds the content that is common to all tabs: the top level tabs, the containers for main, sidebar, and panel content.

## `store.py`
All the data required for all tab/subtabs is stored in the browser session whenever the cohort selection changes. This has the advantage of making transitions smooth but at the cost of higher browser memory demand. This may need to be reviewed. The alternative, of querying CouchDB on tab transitions would be fairly straightforward to implement but may result in slower transitions.

Also stored in the session is the ID of the currently selected student for use by the student report and kudos and concern forms.

## `pages` and `forms`

`pages` collects the modules responsible for top level division of content, or tabs.

`forms` collects the modules responsible for form content.

In order to be able to register all the callbacks on initialisation, all the component IDs need to be in the layout from the start. Components that are not relevant to the current tab/subtab are then selectively hidden. Tabs are responsible for hiding their own content in their `register_callbacks` method.

In order to be able to register all the callbacks on initialisation, all the component IDs need to be in the layout from the start. Components that are not relevant to the current tab/subtab are then selectively hidden 

Each tab, `cohort`, `team` and so on, has at least the following attributes, each of which is a list of html.Div:
* `content` - the main content div(s)
* `sidebar` - content for the left sidebar such as the student selection table
* `panel` - content for the right hand panel, intended for subtab-specific content
and an attribute `subtabs` which is a list of dcc.Tab.

Each tab also implements a method `register_callbacks` which controls all the callback functionality specific to that tab.

## `dispatch.py`

The `dispatch` module is currently responsible for hiding filter dropdowns that are not relevant to the current context. By hiding rather than removing this content from the layout we ensure that dropdown selections are remembered between tab transitions.

## `data.py`

Methods for acquiring data from CouchDB.

## `admin.py`

Manual (currently) methods for importing data via SQL from the MIS.

## `curriculum.py`

Static information such as subject grade scales.

## `create_views.py`

One off methods for creating indices on the database

## `random_data.py`

Generate random testing data and push to database
