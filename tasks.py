from pathlib import Path
from celery import Celery
from celery.schedules import crontab
from datetime import date
import os
from redmail import gmail
import subprocess
import jinja2
import pandas as pd
import data
import app_data
from configparser import ConfigParser
import curriculum
import admin

config_object = ConfigParser()
config_file = 'config.ini'
config_object.read(config_file)

mail_config = config_object['SMTP']
gmail.username = mail_config['username']
gmail.password = mail_config['password']

rabbitmq_config = config_object['RABBITMQ']
rabbitmq_user = rabbitmq_config['username']
rabbitmq_password = rabbitmq_config['password']

couchdb_config = config_object['COUCHDB']
couchdb_user = couchdb_config['user']
couchdb_password = couchdb_config['pwd']
couchdb_ip = couchdb_config['ip']
couchdb_port = couchdb_config['port']
couchdb_db = couchdb_config['db']

app = Celery(
    'tasks',
    result_backend=
    f'couchdb://{couchdb_user}:{couchdb_password}@{couchdb_ip}:{couchdb_port}/{couchdb_db}',
    broker=f'amqp://{rabbitmq_user}:{rabbitmq_password}@localhost:5672/')

app.conf.beat_schedule = {
    "sync sf attendance": {
        "task": "tasks.sync_attendance",
        "schedule": crontab(minute='*/15', hour='8-16', day_of_week='mon-fri')
    }
}

@app.task
def sync_attendance():
    admin.sync_rems_attendance("weekly", "ada")
    admin.sync_rems_attendance("monthly", "ada")

@app.task
def send_email(subject, body, to_list=None, cc_list=None, bcc_list=None):
    params = {
        'subject': subject,
        'text': body,
        'receivers': to_list,
        'cc': cc_list,
        'bcc': bcc_list
    }
    try:
        gmail.send(**params)
        params.update({'sent': True})
    except Exception as e:
        params.update({'sent': False, 'exception': str(e)})
    return params


@app.task
def send_report(student_id):
    report_dict = sixthform_academic_report(student_id)
    student = report_dict.get("student")
    report = report_dict.get("report")
    issued = report_dict.get("issued")
    subject = f"{student.get('given_name')}'s {issued} report"
    body = f'Dear Parent/Carer,\n\nPlease find {student.get("given_name")}\'s latest academic report attached.\n\nBest Wishes,\n\nThe Sixth Form Team'
    gmail.send(subject=subject,
               bcc=['ian@ada.ac.uk'],
               text=body,
               attachments={report: Path('latex/' + report)})


def sixthform_academic_report(student_id):
    this_year_start = curriculum.this_year_start
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
    academic = data.get_data("assessment", "student_id", [student_id], "ada")
    academic_df = pd.DataFrame.from_records(
        academic,
        columns=[
            "subject_name", "assessment", "grade", "date", "comment", "report"
        ]).query("report != 2").sort_values(by='date')
    academic_df["comment"] = academic_df["comment"].str.replace('%',
                                                                '\%').replace(
                                                                    '&', '\&')
    academic_df["comment"].fillna("", inplace=True)
    academic_multiindex = academic_df.set_index(
        ["subject_name", "assessment"])[["grade", "date", "comment", "report"]]
    academic_dict = {
        subject: academic_multiindex.xs(subject).to_dict('index')
        for subject in academic_multiindex.index.levels[0]
    }

    student = data.get_student(student_id, "ada")
    latex_jinja_env = jinja2.Environment(
        variable_start_string='\VAR{',
        variable_end_string='}',
        line_statement_prefix='%%',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader('templates'))

    template = latex_jinja_env.get_template('academic_template.tex')
    student_name = f"{student.get('given_name')} {student.get('family_name')}"
    file_name = f"{student.get('_id')} {student_name}"
    wd = os.getcwd()
    os.chdir('latex')
    issued = date.today().strftime('%B %Y')
    with open(file_name + '.tex', 'w') as f:
        template_data = {
            "name": student_name,
            "date": issued,
            "team": student.get("team"),
            "academic": academic_dict,
            "attendance": attendance,
            "punctuality": punctuality,
        }
        f.write(template.render(template_data))
    subprocess.run(['xelatex', '-interaction=nonstopmode', file_name + '.tex'])
    subprocess.run(['xelatex', '-interaction=nonstopmode', file_name + '.tex'])
    if not os.path.exists(file_name + '.pdf'):
        raise RuntimeError(f'PDF not found: {file_name}.pdf')
    os.chdir(wd)
    return {"student": student, "report": file_name + '.pdf', "issued": issued}

@app.task
def send_result(student_id, instance_code):
    components_df = pd.DataFrame().from_records(app_data.get_result_for_instance(student_id, instance_code), index='Component').fillna("")
    student_dict = app_data.get_student_by_id(student_id)
    instance_dict = app_data.get_instance_by_instance_code(instance_code)
    results_dict = app_data.get_detailed_results_for_student(student_id)
    results_df = pd.DataFrame.from_records(results_dict).query('moderated')
    results_df.sort_values(by=['level', 'name'], inplace=True)
    results_df.drop(['code', 'moderated'], axis=1, inplace=True)
    results_df.rename(columns={'level': 'Level', 'name': 'Module', 'credits': 'Credits', 'total': 'Mark'}, inplace=True)
    results_df.set_index('Module', inplace=True)
    results_df = results_df.dropna().astype('int64')
    html = f"<p>Hi {student_dict.get('given_name')},<br/>"
    html += f"Your marks for {instance_dict.get('name')} have now been released.</p>"
    html += f"<h4>{instance_dict.get('name')}</h4>"
    html += "<p>{{ marks_table }}</p>"
    html += "<h4>Your modules</h4>"
    html += "<p>Your moderated results so far are as follows<p>"
    html += "<p>{{ results_table }}<p>"
    html += f"<p>This email is not monitored. If you have any queries about any of your results please raise a ticket with your apprenticeships helpdesk.</p>"
    subject = f"{instance_dict.get('name')} result"
    receivers=[student_dict.get('college_email', 'ian@ada.ac.uk')]
    #receivers=['ian@ada.ac.uk']
    msg = gmail.send(
        receivers=receivers,
        subject=subject,
        html=html,
        body_tables={'marks_table': components_df, 'results_table': results_df}
    )
    return msg.as_string()

def cohort_reports(cohort):
    enrolment_docs = data.get_data("enrolment",
                                   "cohort",
                                   cohort,
                                   db_name="ada")
    for student in enrolment_docs:
        print(f"Generating report for {student.get('given_name')}")
        print(f"Student ID {student.get('_id')}")
        sixthform_academic_report(student.get('_id'))


def instance_results(instance_code):
    student_ids = app_data.get_students_by_instance(instance_code)
    for student_id in student_ids:
        send_result.delay(student_id, instance_code)


if __name__ == "__main__":
    pass
