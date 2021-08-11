# Architecture


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

Defines the top level container, and holds the nav bar, filters and temporary data store objects. Runs the development server if executed.

## `nav.py`

Links to the various pages of the dashboard. Callback on click sets the main content to the content of the appropriate page.

## `filters.py`

Hides and shows filters for cohort, subject and team.

## `pages`

Collects the modules responsible for the content linked to from the navigation bar.

A typical page will have a list of tabs with callback logic to set the page content.

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

## `static_report.py`

Generate a pdf of a student report using `template.tex`
