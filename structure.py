import dash_html_components as html

from pages import (
    sixthform_attendance,
    sixthform_attendance_year,
    sixthform_attendance_unauthorized,
    sixthform_attendance_missing,
    sixthform_pastoral,
    sixthform_pastoral_attendance,
    sixthform_pastoral_weekly,
    sixthform_pastoral_kudos,
    sixthform_pastoral_concern,
    sixthform_academic,
    sixthform_academic_subject
)


class PathExistsError(Exception):
    """The given path already exists"""
    pass


class IncompleteError(Exception):
    """This instance is not fully defined"""
    pass


class Container(object):
    """Base class for sections, pages and tabs"""

    def __init__(self, name, path, layout, callbacks):
        if not (name and path and layout):
            raise IncompleteError
        self.name = name
        self.layout = layout
        self.callbacks = callbacks
        self.children = {}
        self.path = path

    def add_child(self, name, path, layout, callbacks):
        child = Section(name, "/" + path, layout, callbacks)
        self.children[child.path] = child
        return child


class Section(Container):
    """Class for sections.
    It's children are tabs.
    Any content is displayed in the card header"""

    def add_child(self, name, path, layout, callbacks):
        child = Page(name, self.path + "/" + path, layout, callbacks)
        self.children[child.path] = child
        return child


class Page(Section):
    """A page of the dashboard.
    Owns a list of tabs.
    Any content is displayed in the sidebar"""

    def add_tab(self, name, path, layout, callbacks):
        child = Tab(name, self.path + "/" + path, layout, callbacks)
        if path in self.children:
            raise PathExistsError
        else:
            self.children[child.path] = child
        return child


class Tab(Page):
    """The lowest division of content.
    Content is displayed in the main content area"""

    def add_child(self, *args):
        pass


content_dict = {
    ("Summary", "summary", html.Div("Summary"), None):
        {
            ("Sixth Form", "sixthform", html.Div("Summary, Sixth Form"), None):
                [
                    ("Academic", "academic", html.Div("Summary, Sixth Form, Academic"), None)
                ],
            ("Apprenticeships", "apprenticeships", html.Div("Summary, Apprenticeships"), None):
                [
                    ("Academic", "academic", html.Div("Summary, Apprenticeships, Academic"), None)
                ],
        },
    ("Sixth Form", "sixthform", html.Div(""), None):
        {
            ("Attendance", "attendance", sixthform_attendance.layout, None):
            [
                ("Year", "year", sixthform_attendance_year.layout, None),
                ("Unauthorized", "unauthorized", sixthform_attendance_unauthorized.layout, None),
                ("Missing registers", "missing", sixthform_attendance_missing.layout, None)
        ],
            ("Pastoral", "pastoral", sixthform_pastoral.layout, None):
                [
                    ("Attendance", "attendance", sixthform_pastoral_attendance.layout, None),
                    ("Weekly attendance", "weekly", sixthform_pastoral_weekly.layout, None),
                    ("Kudos", "kudos", sixthform_pastoral_kudos.layout, None),
                    ("Concern", "concern", sixthform_pastoral_concern.layout, None),
                ],
            ("Academic", "academic", sixthform_academic.layout, None):
                [
                    ("Cohort", "cohort", html.Div("Sixth Form, Academic, Cohort"), None),
                    ("Subject", "subject", sixthform_academic_subject.layout, None)
                ],
        },
    ("Apprenticeships", "apprenticeships", html.Div("Apprenticeships"), None):
        {
            ("Pastoral", "pastoral", html.Div("Apprenticeships, Pastoral"), None):
                [
                    ("Attendance", "attendance", html.Div("Apprenticeships, Pastoral, Attendance"), None),
                    ("Kudos", "kudos", html.Div("Apprenticeships, Pastoral, Kudos"), None)
                ],
            ("Academic", "academic", html.Div("Apprenticeships, Academic"), None):
                [
                    ("Cohort", "cohort", html.Div("Apprenticeships, Academic, Cohort"), None),
                    ("Subject", "subject", html.Div("Apprenticeships, Academic, Subject"), None)
                ],
        }
}

# The root container. Has no content of its own
home = Container("Home", "/", "Home", None)

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
