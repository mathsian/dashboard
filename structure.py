import dash_html_components as html

from pages import (
    sixthform_attendance,
    sixthform_attendance_year,
    sixthform_attendance_unauthorized,
    sixthform_attendance_missing,
    sixthform_pastoral,
    sixthform_pastoral_progress,
    sixthform_pastoral_attendance,
    sixthform_pastoral_weekly,
    sixthform_pastoral_kudos,
    sixthform_pastoral_concern,
    sixthform_academic,
    sixthform_academic_view,
    sixthform_academic_edit,
    sixthform_student,
    sixthform_student_report,
    sixthform_student_kudos,
    sixthform_student_concern
)


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

    def add_child(self, name, path):
        child = Section(name, "/" + path)
        self.children[child.path] = child
        return child


class Section(Container):
    """Class for sections.
    It's children are pages.
    Any content is ..."""

    def add_child(self, name, path, cardheader_layout, sidebar_layout):
        child = Page(name, self.path + "/" + path, cardheader_layout, sidebar_layout)
        self.children[child.path] = child
        return child


class Page(Container):
    """A page of the dashboard.
    Owns a list of tabs. Sidebar content and cardheader content"""

    def __init__(self, name, path, cardheader_layout, sidebar_layout):
        super().__init__(name, path)
        self.cardheader_layout = cardheader_layout
        self.sidebar_layout = sidebar_layout

    def add_child(self, name, path, layout):
        child = Tab(name, self.path + "/" + path, layout)
        if path in self.children:
            raise PathExistsError
        else:
            self.children[child.path] = child
        return child


class Tab(Container):
    """The lowest division of content.
    Content is displayed in the main content area"""

    def __init__(self, name, path, layout):
        super().__init__(name, path)
        self.layout = layout


content_dict = {
    ("Summary", "summary"):
        {
            ("Sixth Form", "sixthform", html.Div("Summary, Sixth Form"), html.Div("Summary, Sixth Form side")):
                [
                    ("Academic", "academic", html.Div("Summary, Sixth Form, Academic")),
                    ("Pastoral", "pastoral", html.Div("Summary, Sixth Form, Pastoral"))
                ],
            ("Apprenticeships", "apprenticeships", html.Div("Summary, Apprenticeships"), html.Div("Summary, Apprenticeships")):
                [
                    ("Academic", "academic", html.Div("Summary, Apprenticeships, Academic")),
                    ("Pastoral", "pastoral", html.Div("Summary, Apprenticeships, Pastoral"))
                ],
        },
    ("Sixth Form", "sixthform"):
        {
            ("Attendance", "attendance", sixthform_attendance.cardheader_layout, sixthform_attendance.sidebar_layout):
            [
                ("Year", "year", sixthform_attendance_year.layout),
                ("Unauthorized", "unauthorized", sixthform_attendance_unauthorized.layout),
                ("Missing marks", "missing", sixthform_attendance_missing.layout)
        ],
            ("Pastoral", "pastoral", sixthform_pastoral.cardheader_layout, sixthform_pastoral.sidebar_layout):
                [
                    ("Progress", "progress", sixthform_pastoral_progress.layout),
                    ("Attendance", "attendance", sixthform_pastoral_attendance.layout),
                    ("Weekly attendance", "weekly", sixthform_pastoral_weekly.layout),
                    ("Kudos", "kudos", sixthform_pastoral_kudos.layout),
                    ("Concern", "concern", sixthform_pastoral_concern.layout),
                ],
            ("Academic", "academic", sixthform_academic.cardheader_layout, sixthform_academic.sidebar_layout):
                [
                    ("Edit", "edit", sixthform_academic_edit.layout),
                    ("View", "view", sixthform_academic_view.layout)
                ],
            ("Student", "student", sixthform_student.cardheader_layout, sixthform_student.sidebar_layout):
            [
                ("Report", "report", sixthform_student_report.layout),
                ("Kudos", "kudos", sixthform_student_kudos.layout),
                ("Concern", "concern", sixthform_student_concern.layout)
            ]
        },
    ("Apprenticeships", "apprenticeships"):
        {
            ("Pastoral", "pastoral", html.Div("Apprenticeships, Pastoral"), html.Div("Apprenticeships, Pastoral")):
                [
                    ("Attendance", "attendance", html.Div("Apprenticeships, Pastoral, Attendance")),
                    ("Kudos", "kudos", html.Div("Apprenticeships, Pastoral, Kudos"))
                ],
            ("Academic", "academic", html.Div("Apprenticeships, Academic"), html.Div("Apprenticeships, Academic")):
                [
                    ("Cohort", "cohort", html.Div("Apprenticeships, Academic, Cohort")),
                    ("Subject", "subject", html.Div("Apprenticeships, Academic, Subject"))
                ],
        }
}

# The root container. Has no content of its own
home = Container("Home", "/")

for s in content_dict.keys():
    section = home.add_child(*s)
    for p in content_dict[s].keys():
        page = section.add_child(*p)
        for t in content_dict[s][p]:
            tab = page.add_child(*t)


if __name__ == "__main__":
    print(home.name, home.path, home.children)
    for section_path, section in home.children.items():
        print("\t", section.name, section.path, section.children)
        for page_path, page in section.children.items():
            print("\t\t", page.name, page.path, page.children)
            for tab_path, tab in page.children.items():
                print("\t\t\t", tab.name, tab.path)
