from dash import html

from pages import (
    sixthform_attendance, sixthform_attendance_year,
    sixthform_attendance_unauthorized, sixthform_attendance_punctuality,
    sixthform_attendance_missing, sixthform_pastoral,
    sixthform_attendance_daily,
    sixthform_pastoral_progress,
    sixthform_pastoral_attendance, sixthform_pastoral_punctuality,
    sixthform_pastoral_kudos, sixthform_pastoral_concern, sixthform_academic,
    sixthform_pastoral_weekly, sixthform_pastoral_details,
    sixthform_academic_view, sixthform_academic_edit, sixthform_student,
    sixthform_student_report, sixthform_student_kudos,
    sixthform_student_notes, sixthform_pastoral_notes,
    sixthform_student_concern, apprenticeships_academic,
    apprenticeships_info, apprenticeships_info_upcoming, apprenticeships_info_missing, apprenticeships_info_enrolments,
    apprenticeships_academic_edit, apprenticeships_academic_view, apprenticeships_academic_details,
    apprenticeships_attendance, apprenticeships_attendance_year, apprenticeships_attendance_missing,
    apprenticeships_cohorts, apprenticeships_cohorts_report,
    apprenticeships_employers, apprenticeships_employers_report, apprenticeships_employers_summary,
    apprenticeships_reports, apprenticeships_reports_results,
    apprenticeships_report_attendance, apprenticeships_reports_summary, apprenticeships_reports_learners,
    apprenticeships_reports_cohorts,
    # stats_enrolment, stats_enrolment_view,
    admin_records, admin_records_kudos, admin_records_concern, admin_records_notes)


class PathExistsError(Exception):
    """The given path already exists"""
    pass


class IncompleteError(Exception):
    """This instance is not fully defined"""
    pass


class Container(object):
    """Base class for sections, pages and tabs"""

    def __init__(self, name, path):
        self.name = name
        self.children = {}
        self.path = path

    def add_child(self, child):
        self.children[child.path] = child
        return child


# class Section(Container):
#     """Class for sections.
#     It's children are pages.
#     Any content is ..."""
Section = Container


class Page(Container):
    """A page of the dashboard.
    Owns a list of tabs and layout for sidebar content"""

    def __init__(self, name, path, layout):
        super().__init__(name, path)
        self.layout = layout


class Tab(Container):
    """The lowest division of content.
    Content is displayed in the main content area"""

    def __init__(self, name, path, layout):
        super().__init__(name, path)
        self.layout = layout


# content_dict = {
#     ("Summary", "summary"):
#         {
#             ("Sixth Form", "sixthform", html.Div("Summary, Sixth Form side")):
#                 [
#                     ("Academic", "academic", html.Div("Summary, Sixth Form, Academic")),
#                     ("Pastoral", "pastoral", html.Div("Summary, Sixth Form, Pastoral"))
#                 ],
#             ("Apprenticeships", "apprenticeships", html.Div("Summary, Apprenticeships")):
#                 [
#                     ("Academic", "academic", html.Div("Summary, Apprenticeships, Academic")),
#                     ("Pastoral", "pastoral", html.Div("Summary, Apprenticeships, Pastoral"))
#                 ],
#         },
#     ("Sixth Form", "sixthform"):
#         {
#             ("Attendance", "attendance", sixthform_attendance.layout):
#             [
#                 ("Year", "year", sixthform_attendance_year.layout),
#                 ("Unauthorized", "unauthorized", sixthform_attendance_unauthorized.layout),
#                 ("Missing marks", "missing", sixthform_attendance_missing.layout)
#         ],
#         },
#     ("Apprenticeships", "apprenticeships"):
#         {
#             ("Pastoral", "pastoral", html.Div("Apprenticeships, Pastoral")):
#                 [
#                     ("Attendance", "attendance", html.Div("Apprenticeships, Pastoral, Attendance")),
#                     ("Kudos", "kudos", html.Div("Apprenticeships, Pastoral, Kudos"))
#                 ],
#             ("Academic", "academic", html.Div("Apprenticeships, Academic")):
#                 [
#                     ("Cohort", "cohort", html.Div("Apprenticeships, Academic, Cohort")),
#                     ("Subject", "subject", html.Div("Apprenticeships, Academic, Subject"))
#                 ],
#         }
# }

content = {
    Section("Sixth Form", "sixthform"): {
        Page("Attendance", "attendance", sixthform_attendance.layout): [
            Tab("Year", "year", sixthform_attendance_year.layout),
            Tab("Punctuality", "punctuality",
                sixthform_attendance_punctuality.layout),
            Tab("Unauthorized", "unauthorized",
                sixthform_attendance_unauthorized.layout),
            Tab("Daily", "daily", sixthform_attendance_daily.layout),
            Tab("Missing marks", "missing",
                sixthform_attendance_missing.layout)
        ],
        Page("Pastoral", "pastoral", sixthform_pastoral.layout): [
            Tab("Attendance", "attendance",
                sixthform_pastoral_attendance.layout),
            Tab("Weekly", "weekly", sixthform_pastoral_weekly.layout),
            Tab("Punctuality", "punctuality", sixthform_pastoral_punctuality.layout),
            Tab("Notes", "notes", sixthform_pastoral_notes.layout),
            Tab("Kudos", "kudos", sixthform_pastoral_kudos.layout),
            # Tab("Concern summary", "concern", sixthform_pastoral_concern.layout),
            # Tab("Concern details", "details", sixthform_pastoral_details.layout),
            Tab("Progress", "progress", sixthform_pastoral_progress.layout),
        ],
        Page("Academic", "academic", sixthform_academic.layout): [
            Tab("Edit", "edit", sixthform_academic_edit.layout),
            Tab("View", "view", sixthform_academic_view.layout)
        ],
        Page("Student", "student", sixthform_student.layout): [
            Tab("Report", "report", sixthform_student_report.layout),
            Tab("Kudos", "kudos", sixthform_student_kudos.layout),
            Tab("Notes", "notes", sixthform_student_notes.layout),
            # Tab("Concern", "concern", sixthform_student_concern.layout)
        ]
    },
    Section("Apprenticeships", "apprenticeships"): {
        Page("Info", "info", apprenticeships_info.layout): [
            Tab("Upcoming", "upcoming", apprenticeships_info_upcoming.layout),
            Tab("Missing results", "missing", apprenticeships_info_missing.layout),
            Tab("Enrolments summary", "enrolments", apprenticeships_info_enrolments.layout),
        ],
        Page("Academic", "academic", apprenticeships_academic.layout): [
            Tab("Edit", "edit", apprenticeships_academic_edit.layout),
            Tab("View", "view", apprenticeships_academic_view.layout),
            Tab("Details", "details", apprenticeships_academic_details.layout)
        ],
        Page("Attendance", "attendance", apprenticeships_attendance.layout):
            [Tab("Year", "year", apprenticeships_attendance_year.layout),
             Tab("Missing", "missing", apprenticeships_attendance_missing.layout)],
        Page("Cohorts", "cohorts", apprenticeships_cohorts.layout):
            [Tab("Report", "report", apprenticeships_cohorts_report.layout)],
        Page("Employers", "employers", apprenticeships_employers.layout):
            [Tab("Summary", "summary", apprenticeships_employers_summary.layout),
             Tab("Report", "report", apprenticeships_employers_report.layout)],
        Page("Reports", "reports", apprenticeships_reports.layout):
            [Tab("Summary", "summary", apprenticeships_reports_summary.layout),
             Tab("Cohorts", "cohorts", apprenticeships_reports_cohorts.layout),
             Tab("Learners", "learners", apprenticeships_reports_learners.layout),
             Tab("Results", "results", apprenticeships_reports_results.layout),
             Tab("Attendance", "attendance", apprenticeships_report_attendance.layout)]
    },
    #     Section("Stats", "stats"): {
    #         Page("Enrolment", "enrolment", stats_enrolment.layout):
    #         [Tab("View", "view", stats_enrolment_view.layout)]
    #     },
    Section("Admin", "admin"): {
        Page("My records", "records", admin_records.layout): [
            Tab("Kudos", "kudos", admin_records_kudos.layout),
            Tab("Notes", "notes", admin_records_notes.layout),
            # Tab("Concern", "concern", admin_records_concern.layout)
        ]
    }
}
# The root container. Has no content of its own
home = Container("Home", "/")
for s in content.keys():
    section = home.add_child(s)
    for p in content[s].keys():
        page = section.add_child(p)
        for t in content[s][p]:
            tab = page.add_child(t)

if __name__ == "__main__":
    print(home.name, home.path, home.children)
    for section_path, section in home.children.items():
        print("\t", section.name, section.path, section.children)
        for page_path, page in section.children.items():
            print("\t\t", page.name, page.path, page.children)
            for tab_path, tab in page.children.items():
                print("\t\t\t", tab.name, tab.path)
