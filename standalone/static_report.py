import sys

from os.path import abspath
import jinja2
import pandas as pd

sys.path.append('..')
import data
import curriculum


def generate_report(student_id):
    this_year_start = curriculum.this_year_start
    student = data.get_student(student_id, "ada")
    academic_multiindex = pd.DataFrame.from_records(
        data.get_data("assessment", "student_id", [student_id], "ada"),
        columns=["subject_name", "assessment", "grade", "date",
                 "comment", "report"]).query('report == 1').set_index(["subject_name", "assessment"
                                        ])[["grade", "date", "comment"]]
    # Escape manually for now
    academic_multiindex['comment'].fillna("", inplace=True)
    academic_multiindex.eval(
        "comment = comment.str.replace('%', '\%').replace('&', '\&')",
        inplace=True)
    academic = {
        subject: academic_multiindex.xs(subject).to_dict('index')
        for subject in academic_multiindex.index.levels[0]
    }
    kudos_df = pd.DataFrame(
        data.get_data("kudos", "student_id", [student_id], "ada"),
        columns=["ada_value", "points", "date", "from",
                 "description"]).sort_values(
                     "date", ascending=False).query("date >= @this_year_start")
    kudos_df.eval(
        "description = description.str.replace('%', '\%').replace('&', '\&')",
        inplace=True)
    kudos_df["date"] = kudos_df["date"].apply(data.format_date)
    kudos_df['points'] = pd.to_numeric(kudos_df['points'], downcast='integer')
    kudos_total = kudos_df['points'].sum()
    kudos = kudos_df.to_dict(orient='records')
    concern_df = pd.DataFrame(
        data.get_data("concern", "student_id", [student_id], "ada"),
        columns=["category", "date", "description", "from"]).sort_values(
            "date", ascending=False).query("date >= @this_year_start")
    concern_df["date"] = concern_df["date"].apply(data.format_date)
    concern_df.eval(
        "description = description.str.replace('%', '\%').replace('&', '\&')",
        inplace=True)
    concern_total = len(concern_df)
    concerns = concern_df.to_dict(orient='records')
    attendance_df = pd.DataFrame.from_records(
        data.get_data("attendance", "student_id", [student_id],
                      "ada")).query("subtype == 'monthly'").sort_values(
                          by='date',
                          ascending=True).query("date >= @this_year_start")
    # attendance_df['date'] = attendance_df['date'].apply(data.format_date)
    attendance_totals = attendance_df.sum()
    attendance = round(100 * attendance_totals['actual'] /
                       attendance_totals['possible'])
    punctuality = round(100 - 100 * attendance_totals['late'] /
                        attendance_totals['actual'])
    ucas = data.get_data("ucas", "student_id", [student_id], "ada")
    messages = []
    if ucas:
        ucas_status = ucas[0].get("ucas_status")
        if ucas_status == "Not Submitted":
            message = {"title": "UCAS application", "message": f"{student.get('given_name')} has not yet submitted their UCAS form. We strongly advise they do this even if they are not intending to go to university. The UCAS process is great practice for an apprenticeship or job application. Submitting their UCAS form will also mean the college will have a reference for them on file should they need one in the future. This will also provide them with a backup option should they not be successful in securing an apprenticeship."}
            messages.append(message)
        elif ucas_status == "Returned":
            message = {"title": "UCAS application", "message": f"{student.get('given_name')} has had their UCAS form returned to them to correct an error. Please take a look at the form with them and help them complete and resubmit it. If further support is required please email mumtaz@ada.ac.uk"}
            messages.append(message)
    # attendance_df['percent'] = round(
    #     100 * (attendance_df['actual'] - attendance_df['late']) /
    #     attendance_df['possible'])
    # attendance_df['late'] = round(100 * attendance_df['late'] /
    #                               attendance_df['possible'])
    # cumulative = int(100 * attendance_df['actual'].sum() /
    #                  attendance_df['possible'].sum())
    # attendance_min = attendance_df['date'].tolist()[0]
    # attendance_max = attendance_df['date'].tolist()[-1]
    # attendance_dates = ",".join(f"{d}" for d in attendance_df["date"].tolist())
    # attendance_zip = " ".join(f"({d}, {p})" for d, p in zip(
    #     attendance_df["date"].tolist(), attendance_df['percent'].tolist()))
    # punctuality_zip = " ".join(f"({d}, {p})" for d, p in zip(
    #     attendance_df["date"].tolist(), attendance_df['late'].tolist()))

    latex_jinja_env = jinja2.Environment(variable_start_string='\VAR{',
                                         variable_end_string='}',
                                         line_statement_prefix='%%',
                                         trim_blocks=True,
                                         autoescape=False,
                                         loader=jinja2.FileSystemLoader(
                                             abspath('../templates')))

    template = latex_jinja_env.get_template('template.tex')
    student_name = f"{student.get('given_name')} {student.get('family_name')}"
    with open(f"../latex/{student.get('_id')} {student_name}.tex", 'w') as f:
        template_data = {
            "name": student_name,
            "date": "December 2021",
            "team": student.get("team"),
            # "attendance_dates": attendance_dates,
            # "attendance_zip": attendance_zip,
            # "punctuality_zip": punctuality_zip,
            "attendance": attendance,
            "punctuality": punctuality,
            "academic": academic,
            "kudos": kudos,
            "kudos_total": kudos_total,
            "concerns": concerns,
            "concern_total": concern_total,
            "messages": messages
        }
        f.write(template.render(template_data))
        print("tex done")


def cohort_reports(cohort):
    enrolment_docs = data.get_data("enrolment",
                                   "cohort",
                                   cohort,
                                   db_name="ada")
    for student in enrolment_docs:
        print(f"Generating report for {student.get('given_name')}")
        print(f"Student ID {student.get('_id')}")
        generate_report(student.get('_id'))


if __name__ == "__main__":
    #generate_report("190817")
    cohort_reports("2123")
